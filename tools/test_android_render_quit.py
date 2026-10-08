"""Android renderer race and main-menu exit checks, without game assets or a GPU.

Compiles production mirror_refresh against an upload-order model. This proves
upload scheduling, not that a particular phone's driver renders correctly.
"""
from pathlib import Path
import subprocess
import tempfile
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]

PREAMBLE = r'''
#include <assert.h>
#include <limits.h>
#include <stdlib.h>
#include <string.h>
#define HALO_ANDROID 1
#define TRUE 1
#define FALSE 0
#define STREAM_BUFFER_RING 3UL
#define PLATFORM_CONTIGUOUS_BASE 0x80000000UL
#define PLATFORM_CONTIGUOUS_SIZE 0x800000UL
#define GL_COPY_WRITE_BUFFER 1
#define GL_DYNAMIC_DRAW 2
typedef int BOOL;
typedef unsigned int GLuint;
static struct { unsigned long frame; } device;
static unsigned long generation[2048];
static unsigned long sync_calls, async_calls;
static GLuint bound, next_buffer;
static unsigned long pending_frame[8];
static int pending[8];
static void glGenBuffers(int n, GLuint *out) { assert(n == 1); *out = ++next_buffer; }
static void glBindBuffer(int target, GLuint buffer) { (void)target; bound = buffer; }
static void glBufferData(int target, unsigned long size, void *data, int usage) {
    (void)target; (void)size; (void)data; (void)usage; pending[bound] = 0;
}
static unsigned long memory_watch_generation(unsigned long address, unsigned long size) {
    (void)size; return generation[(address - PLATFORM_CONTIGUOUS_BASE) / 4096];
}
static void memory_watch_protect(unsigned long address, unsigned long size) { (void)address; (void)size; }
static void host_gl_buffer_write(int target, unsigned int offset, unsigned int size, const void *data) {
    (void)target; (void)offset; (void)size; (void)data;
    /* A delayed whole-buffer copy would overwrite an unsynchronized write. */
    assert(!pending[bound] || device.frame - pending_frame[bound] >= STREAM_BUFFER_RING);
    async_calls++;
}
static void buffer_upload(int target, unsigned long offset, unsigned long size, const void *data) {
    (void)target; (void)offset; (void)size; (void)data;
    pending[bound] = 1; pending_frame[bound] = device.frame; sync_calls++;
}
'''
CASES = r'''
int main(void) {
    device.frame = 40;
    assert(mirror_refresh(0, 1)); assert(async_calls == 1 && sync_calls == 0);
    /* A page written again causes a GPU copy; untouched neighboring pages
       must not be mapped unsynchronized until the corresponding fence. */
    generation[0] = 1;
    assert(mirror_refresh(0, 1)); assert(sync_calls == 1);
    assert(mirror_refresh(1, 2)); assert(sync_calls == 2 && async_calls == 1);
    device.frame += 2;
    assert(mirror_refresh(2, 3)); assert(sync_calls == 3 && async_calls == 1);
    device.frame += STREAM_BUFFER_RING;
    assert(mirror_refresh(3, 4)); assert(async_calls == 2);
    /* Segments are independent: another segment still takes the fast path. */
    assert(mirror_refresh(1024, 1025)); assert(async_calls == 3);
    /* Unsigned frame rollover preserves the short age across wrap. */
    memset(&mirror, 0, sizeof(mirror)); memset(generation, 0, sizeof(generation));
    device.frame = ULONG_MAX - 1;
    assert(mirror_refresh(0, 1));
    generation[0] = 2; assert(mirror_refresh(0, 1));
    device.frame = 0; assert(mirror_refresh(1, 2));
    device.frame = 3; assert(mirror_refresh(2, 3));
    return 0;
}
'''


def build_run(source, folder, name):
    c = folder / (name + '.c')
    c.write_text(source)
    exe = folder / name
    subprocess.run(['cc', '-std=c99', '-Wall', '-Wextra', '-Werror', str(c), '-o', str(exe)], check=True)
    return subprocess.run([str(exe)], stdout=subprocess.PIPE, stderr=subprocess.PIPE)


def test_mirror(folder):
    text = (ROOT / 'port/linux/src/d3d8_gl.c').read_text()
    start = text.index('#define MIRROR_SEGMENT_SIZE')
    end = text.index('/* makes [address, address + size)', start)
    production = text[start:end]
    assert build_run(PREAMBLE + production + CASES, folder, 'mirror').returncode == 0
    old = production.replace('unused && device.frame - mirror.subdata_frame[segment] >= STREAM_BUFFER_RING', 'unused')
    assert old != production
    assert build_run(PREAMBLE + old + CASES, folder, 'old_mirror').returncode != 0, 'negative control missed the race'


def test_quit(folder):
    platform = (ROOT / 'port/linux/src/sdl_platform.c').read_text()
    start = platform.index('void platform_request_quit(void)')
    end = platform.index('void platform_scoreboard_scroll', start)
    source = '#include <stdlib.h>\n#define HALO_ANDROID 1\n' + platform[start:end]
    # With the Android macro, production Quit must exit rather than return.
    assert build_run(source + 'int main(void) { platform_request_quit(); return 99; }', folder, 'quit').returncode == 0
    old = source.replace('exit(EXIT_SUCCESS);', '(void)0;')
    assert build_run(old + 'int main(void) { platform_request_quit(); return 99; }', folder, 'old_quit').returncode == 99
    widgets = (ROOT / 'source/interface/ui_widget.c').read_text()
    extension = (ROOT / 'source/interface/ui_widget_porting.h').read_text()
    assert 'ui_porting_is_quit' not in widgets + extension, 'Quit is still intercepted or hidden'
    # Each native main-menu theme routes Quit through confirmation, not exit.
    for path in [ROOT / 'port/assets/menus/ce/main_menu.xml', *sorted((ROOT / 'port/assets/menus/skin').glob('*/ce/main_menu.xml'))]:
        menu = ET.parse(path).getroot()
        item = next(w for w in menu.findall('widget') if w.get('name') == 'main_menu/main_menu_item_quit_game')
        for event in ('a', 'start'):
            handler = next(h for h in item.findall('on') if h.get('event') == event)
            assert handler.get('open') == 'main_menu/quit_select/quit_screen'
            assert handler.get('run') is None
        assert menu.find(".//child[@widget='main_menu/main_menu_item_quit_game']") is not None
    confirm = ET.parse(ROOT / 'port/assets/menus/ce/main_menu.quit_select.xml').getroot()
    assert confirm.find(".//child[@widget='common_button_back']") is not None
    assert confirm.find(".//on[@run='main menu quit game']") is not None
    for path in (ROOT / 'port/assets/menus/ce').glob('*pause*.xml'):
        assert 'main menu quit game' not in path.read_text()


if __name__ == '__main__':
    with tempfile.TemporaryDirectory() as name:
        folder = Path(name)
        test_mirror(folder)
        test_quit(folder)
    print('Android mirror upload race, negative controls, Quit confirmation and themes passed.')
