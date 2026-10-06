"""Regression checks for fast taps, cancellation and the real keyboard hit map.

Runs production C snippets with tiny platform stubs; no phone/game assets needed.
Build verification and an actual phone test are separate checks.
"""
from pathlib import Path
import subprocess
import tempfile

ROOT = Path(__file__).resolve().parents[1]


def compile_and_run(source):
    with tempfile.TemporaryDirectory() as directory:
        path = Path(directory)
        (path / "test.c").write_text(source)
        subprocess.run(["cc", "-std=c99", "-Wall", "-Wextra", "-Werror", "-I", str(ROOT),
                        str(path / "test.c"), "-lm", "-o", str(path / "test")], check=True)
        subprocess.run([str(path / "test")], check=True)


def test_taps_and_cancel():
    compile_and_run(r'''
#include <assert.h>
#include "port/android/host/touch_state.h"
int main(void) {
    struct touch_state state;
    touch_state_reset(&state);
    touch_state_button(&state, 0, 1, 100);
    touch_state_button(&state, 0, 0, 101);
    assert(touch_state_pressed(&state, 0, 133));
    assert(!touch_state_pressed(&state, 0, 181));
    touch_state_button(&state, 16, 1, 200);
    touch_state_button(&state, 11, 1, 200);
    state.x = 12000; state.y = -20000;
    assert(touch_state_pressed(&state, 16, 400));
    assert(touch_state_pressed(&state, 11, 400));
    touch_state_button(&state, 11, 0, 400);
    assert(touch_state_pressed(&state, 16, 401));
    assert(!touch_state_pressed(&state, 11, 401));
    touch_state_reset(&state);
    assert(!touch_state_pressed(&state, 16, 201));
    assert(state.x == 0 && state.y == 0);
    touch_state_button(&state, -1, 1, 500);
    touch_state_button(&state, TOUCH_BUTTON_COUNT, 1, 500);
    assert(!touch_state_pressed(&state, 0, 501));
    return 0;
}
''')


def test_menu_coordinates():
    source = (ROOT / "port/linux/src/d3d8_gl.c").read_text()
    start = source.index("static void ui_point_from_window(")
    end = source.index("int halo_ui_pointer_update(", start)
    compile_and_run('''
#include <assert.h>
#include <math.h>
#include <stddef.h>
struct render_target_entry { struct { int gl_width, gl_height, width, height; } target; };
static struct render_target_entry buffer = {{640, 480, 640, 480}};
static struct { int back_buffer; } device;
static int window_width = 1920, window_height = 1080, pixels_width = 1920, pixels_height = 1080;
static struct render_target_entry *render_target_get(int *unused) { (void)unused; return &buffer; }
static void platform_video_window_size(int *w, int *h) { *w = window_width; *h = window_height; }
static void platform_video_drawable_size(int *w, int *h) { *w = pixels_width; *h = pixels_height; }
static int halo_screen_width(void) { return buffer.target.width; }
''' + source[start:end] + r'''
int main(void) {
    short x, y;
    ui_point_from_window(744, 463.5f, &x, &y);
    assert(x == 224 && y == 206); /* landscape letterboxing */
    ui_point_from_window(0, 463.5f, &x, &y);
    assert(x < 0); /* black border must not activate a widget */
    pixels_width = 3840; pixels_height = 2160;
    ui_point_from_window(744, 463.5f, &x, &y);
    assert(x == 224 && y == 206); /* display scaling */
    window_width = pixels_width = 640; window_height = pixels_height = 480;
    ui_point_from_window(224, 206, &x, &y);
    assert(x == 224 && y == 206);
    return 0;
}
''')


def test_keyboard_pointer():
    source = (ROOT / "source/interface/virtual_keyboard.c").read_text()
    # Compile the actual production enum, rectangles, layout and hit function.
    enum_start = source.index("enum", source.index("#include"))
    key_enum_end = source.index("NUMBER_OF_VIRTUAL_KEYS,")
    key_enum_start = source.rfind("enum", enum_start, key_enum_end)
    key_enum_end = source.index("};", key_enum_end) + 2
    table_start = source.index("static char const virtual_keyboard_layout_table")
    table_end = source.index("static struct virtual_keyboard_globals", table_start)
    function_start = source.index("void virtual_keyboard_pointer(")
    function_end = source.index("static void virtual_keyboard_port_type(", function_start)
    compile_and_run('''
#include <assert.h>
#define VIRTUAL_KEYBOARD_ROW_COUNT 5
#define VIRTUAL_KEYBOARD_COLUMN_COUNT 11
typedef struct { short y0, x0, y1, x1; } rectangle2d;
static struct { int active; short row, column; } virtual_keyboard_globals;
static int selects, cancels;
static void virtual_keyboard_select(void) { selects++; }
static void virtual_keyboard_cancel(void) { cancels++; virtual_keyboard_globals.active = 0; }
''' + source[key_enum_start:key_enum_end] + source[table_start:table_end] +
        source[function_start:function_end] + r'''
int main(void) {
    virtual_keyboard_globals.active = 1;
    virtual_keyboard_pointer(224, 206, 1, 0);
    assert(virtual_keyboard_layout_table[virtual_keyboard_globals.row][virtual_keyboard_globals.column] == _vkey_a);
    assert(selects == 1);
    virtual_keyboard_pointer(224, 158, 1, 0);
    assert(virtual_keyboard_layout_table[virtual_keyboard_globals.row][virtual_keyboard_globals.column] == _vkey_1);
    virtual_keyboard_pointer(416, 270, 1, 0);
    assert(virtual_keyboard_layout_table[virtual_keyboard_globals.row][virtual_keyboard_globals.column] == _vkey_backspace);
    virtual_keyboard_pointer(120, 170, 1, 0);
    assert(virtual_keyboard_layout_table[virtual_keyboard_globals.row][virtual_keyboard_globals.column] == _vkey_done);
    assert(selects == 4);
    virtual_keyboard_pointer(-1, 270, 1, 0);
    assert(selects == 4);
    virtual_keyboard_pointer(224, 206, 0, 1);
    assert(cancels == 1);
    virtual_keyboard_pointer(224, 206, 1, 0);
    assert(selects == 4);
    return 0;
}
''')


if __name__ == "__main__":
    test_taps_and_cancel()
    test_menu_coordinates()
    test_keyboard_pointer()
    print("Touch tap/cancel, menu-coordinate and profile keyboard regression checks passed.")
