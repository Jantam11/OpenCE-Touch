"""Check upstream integration without a device: no duplicate touch consumer,
and a progress capture without a depth buffer. Compile production snippets.
"""
from pathlib import Path
import subprocess
import tempfile
ROOT = Path(__file__).resolve().parents[1]
def run(code, name, folder):
    c = folder / (name + '.c'); exe = folder / name
    c.write_text(code)
    subprocess.run(['cc', '-std=c99', '-Wall', '-Wextra', '-Werror', str(c), '-o', str(exe)], check=True)
    return subprocess.run([str(exe)], capture_output=True).returncode
xinput = (ROOT / 'port/linux/src/xinput_sdl.c').read_text()
functions = []
for name in ['halo_linux_touch_move', 'halo_linux_touch_look', 'halo_linux_touch_aiming']:
    start = xinput.index('int ' + name + '(')
    end = xinput.index('\n}', start) + 2
    functions.append(xinput[start:end])
# No declarations for the upstream overlay readers: linking must fail if the
# fork starts consuming their deltas in addition to its SDL virtual input.
code = '#include <assert.h>\n#define HALO_ANDROID 1\n#define HALO_TOUCH_SDL_GAMEPAD 1\n#define TRUE 1\n#define FALSE 0\n'
code += '\n'.join(functions)
code += '\nint main(void) { float f=1,s=1,y=1,p=1,gy=1,gp=1; assert(!halo_linux_touch_move(0,&f,&s)); assert(f==0 && s==0); assert(!halo_linux_touch_look(0,&y,&p,&gy,&gp)); assert(y==0 && p==0 && gy==0 && gp==0); assert(!halo_linux_touch_aiming(0)); return 0; }\n'
progress = (ROOT / 'source/interface/progress_bar.c').read_text()
start = progress.index('\t\tIDirect3DSurface8_Release(back_buffer);', progress.index('static void progress_bar_make_stuff_ready(', progress.index('static void progress_bar_make_stuff_ready(')+1))
end = progress.index('\n\t}', start)
release = progress[start:end]
prefix = '#include <assert.h>\n#include <stddef.h>\nstatic int releases; static void IDirect3DSurface8_Release(void *p) { assert(p); releases++; }\nstatic void check(void *depth_buffer) { int b,f; void *back_buffer=&b, *front_buffer=&f;\n'
suffix = '\n}\nint main(void) { int d; check(NULL); assert(releases==2); check(&d); assert(releases==5); return 0; }\n'
with tempfile.TemporaryDirectory() as directory:
    folder=Path(directory)
    assert run(code,'one_touch_consumer',folder)==0
    assert run(prefix+release+suffix,'depth_optional',folder)==0
    assert run(prefix+release.replace('if (depth_buffer)', 'if (1)')+suffix,'old_depth',folder)!=0
print('Android single touch-consumer and optional depth-buffer checks passed.')
