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


def test_controller_ports():
    source = (ROOT / "port/linux/src/xinput_sdl.c").read_text()
    start = source.index("static int sdl_gamepads(")
    end = source.index("static SHORT stick(", start)
    compile_and_run('''
#include <assert.h>
#include <stdlib.h>
#include <string.h>
#define HALO_ANDROID 1
#define PORT_COUNT 4
#define TRUE 1
#define FALSE 0
#define SDL_GAMEPAD_BUTTON_COUNT 26
#define SDL_GAMEPAD_AXIS_COUNT 6
#define SDL_GAMEPAD_TYPE_UNKNOWN 0
#define SDL_GAMEPAD_TYPE_STANDARD 1
typedef int BOOL;
typedef int SDL_JoystickID;
typedef int SDL_GamepadType;
typedef int SDL_GamepadButton;
typedef int SDL_GamepadAxis;
typedef struct { int id, type, virtual_pad, held; } SDL_Gamepad;
static SDL_Gamepad pads[] = {{1, 2, 0, 0}, {2, 0, 0, 0}, {3, 1, 1, 0}};
static int listed = 3, split = 1;
static SDL_JoystickID *SDL_GetGamepads(int *count) {
    int *ids = malloc(3 * sizeof(int));
    *count = listed;
    for (int i = 0; i < listed; i++) ids[i] = pads[i].id;
    return ids;
}
static SDL_Gamepad *SDL_GetGamepadFromID(int id) {
    for (int i = 0; i < 3; i++) if (pads[i].id == id) return &pads[i];
    return NULL;
}
static int SDL_GetGamepadType(SDL_Gamepad *pad) { return pad->type; }
static int SDL_GetGamepadID(SDL_Gamepad *pad) { return pad->id; }
static int SDL_IsJoystickVirtual(int id) { return SDL_GetGamepadFromID(id)->virtual_pad; }
static int SDL_GetGamepadButton(SDL_Gamepad *pad, int button) { (void)button; return pad->held; }
static int SDL_GetGamepadAxis(SDL_Gamepad *pad, int axis) { (void)pad; (void)axis; return 0; }
static int pc_menu_split_players(void) { return split; }
#define SDL_free free
''' + source[start:end] + r'''
int main(void) {
    SDL_Gamepad *gamepads[PORT_COUNT];
    assert(sdl_gamepads(gamepads) == 3);
    assert(gamepads[0]->id == 3); /* touch first, recognised physical second */
    assert(gamepads[1]->id == 1 && gamepads[2]->id == 2);
    assert(port_gamepad(gamepads, 3, 0)->id == 3);
    gamepads[0]->held = 1; /* B held while a split-screen profile closes */
    assert(port_gamepad(gamepads, 1, 0)->id == 3);
    assert(port_gamepad(gamepads, 1, 1) == NULL);
    split = 0;
    assert(port_gamepad(gamepads, 1, 0)->id == 3);
    gamepads[0] = &pads[0]; pads[0].held = 0; split = 1;
    assert(port_gamepad(gamepads, 1, 0) == NULL); /* physical pad retains upstream behaviour */
    assert(port_gamepad(gamepads, 1, 1)->id == 1);
    return 0;
}
''')


def test_menu_coordinates():
    source = (ROOT / "port/linux/src/d3d8_gl.c").read_text()
    start = source.index("static void ui_point_from_window_on(")
    end = source.index("int halo_scoreboard_pointer_update(", start)
    compile_and_run('''
#include <assert.h>
#include <math.h>
#include <stddef.h>
#define TRUE 1
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
    test_controller_ports()
    test_menu_coordinates()
    test_keyboard_pointer()
    print("Touch tap/cancel, controller ports, menu-coordinate and profile keyboard checks passed.")
