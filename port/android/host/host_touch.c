/* Touch controls are an SDL gamepad, never a text keyboard. All SDL joystick
 * changes run through its Update callback; Android only writes the snapshot. */
#include "host.h"
#include "touch_state.h"
#include <SDL3/SDL.h>
#include <jni.h>
#include <pthread.h>

static pthread_mutex_t touch_lock = PTHREAD_MUTEX_INITIALIZER;
static struct touch_state touch;
static SDL_Joystick *touch_joystick;
static SDL_JoystickID touch_id;
static int touch_ready;

static void SDLCALL touch_update(void *unused) {
    struct touch_state state;
    Uint64 now = SDL_GetTicks();
    int button;
    (void)unused;
    if (!touch_joystick) return;
    pthread_mutex_lock(&touch_lock);
    state = touch;
    pthread_mutex_unlock(&touch_lock);
    for (button = 0; button < 15; button++)
        SDL_SetJoystickVirtualButton(touch_joystick, button, touch_state_pressed(&state, button, now));
    SDL_SetJoystickVirtualAxis(touch_joystick, SDL_GAMEPAD_AXIS_LEFTX, state.x);
    SDL_SetJoystickVirtualAxis(touch_joystick, SDL_GAMEPAD_AXIS_LEFTY, state.y);
    SDL_SetJoystickVirtualAxis(touch_joystick, SDL_GAMEPAD_AXIS_LEFT_TRIGGER,
        touch_state_pressed(&state, 15, now) ? 32767 : -32768);
    SDL_SetJoystickVirtualAxis(touch_joystick, SDL_GAMEPAD_AXIS_RIGHT_TRIGGER,
        touch_state_pressed(&state, 16, now) ? 32767 : -32768);
}

void host_touch_initialize(void) {
    SDL_VirtualJoystickDesc desc;
    if (touch_id || !(SDL_WasInit(SDL_INIT_GAMEPAD) & SDL_INIT_GAMEPAD)) return;
    SDL_INIT_INTERFACE(&desc);
    desc.type = SDL_JOYSTICK_TYPE_GAMEPAD;
    desc.name = "OpenCE Touch Controls";
    desc.naxes = SDL_GAMEPAD_AXIS_COUNT;
    desc.nbuttons = 15;
    desc.axis_mask = (1u << SDL_GAMEPAD_AXIS_COUNT) - 1;
    desc.button_mask = (1u << 15) - 1;
    desc.Update = touch_update;
    touch_id = SDL_AttachVirtualJoystick(&desc);
    touch_joystick = touch_id ? SDL_OpenJoystick(touch_id) : NULL;
    if (!touch_joystick) {
        if (touch_id) SDL_DetachVirtualJoystick(touch_id);
        touch_id = 0;
        host_logf(HOST_LOG_ERROR, "touch gamepad: %s", SDL_GetError());
        return;
    }
    /* No callback can write through a null handle; OpenJoystick may pump. */
    SDL_SetJoystickVirtualAxis(touch_joystick, SDL_GAMEPAD_AXIS_LEFT_TRIGGER, -32768);
    SDL_SetJoystickVirtualAxis(touch_joystick, SDL_GAMEPAD_AXIS_RIGHT_TRIGGER, -32768);
    pthread_mutex_lock(&touch_lock);
    touch_ready = 1;
    pthread_mutex_unlock(&touch_lock);
    host_logf(HOST_LOG_INFO, "touch gamepad ready (%u)", (unsigned)touch_id);
}

JNIEXPORT void JNICALL Java_com_halo_decomp_TouchInput_button(JNIEnv *env, jclass cls, jint button, jboolean down) {
    (void)env; (void)cls;
    pthread_mutex_lock(&touch_lock);
    touch_state_button(&touch, button, down, SDL_GetTicks());
    pthread_mutex_unlock(&touch_lock);
}
JNIEXPORT void JNICALL Java_com_halo_decomp_TouchInput_move(JNIEnv *env, jclass cls, jfloat x, jfloat y) {
    (void)env; (void)cls;
    x = SDL_clamp(x, -1.0f, 1.0f); y = SDL_clamp(y, -1.0f, 1.0f);
    pthread_mutex_lock(&touch_lock);
    touch.x = (Sint16)(x * 32767); touch.y = (Sint16)(y * 32767);
    pthread_mutex_unlock(&touch_lock);
}
JNIEXPORT void JNICALL Java_com_halo_decomp_TouchInput_reset(JNIEnv *env, jclass cls) {
    (void)env; (void)cls;
    pthread_mutex_lock(&touch_lock);
    touch_state_reset(&touch);
    pthread_mutex_unlock(&touch_lock);
}
JNIEXPORT jint JNICALL Java_com_halo_decomp_TouchInput_mode(JNIEnv *env, jclass cls) {
    int ready;
    (void)env; (void)cls;
    pthread_mutex_lock(&touch_lock); ready = touch_ready; pthread_mutex_unlock(&touch_lock);
    return (SDL_GetHintBoolean("OPEN_CE_TOUCH_MENUS", true) ? 1 : 0) |
        (SDL_GetHintBoolean("OPEN_CE_TOUCH_KEYBOARD", false) ? 2 : 0) | (ready ? 4 : 0);
}
