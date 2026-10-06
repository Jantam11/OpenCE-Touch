#ifndef OPEN_CE_TOUCH_STATE_H
#define OPEN_CE_TOUCH_STATE_H

#include <stdint.h>
#include <string.h>

/* SDL gamepad buttons 0..14 followed by the two triggers. Keep a short tap
 * visible for a game tick even if Android delivers both edges between polls. */
#define TOUCH_BUTTON_COUNT 17
#define TOUCH_TAP_MS 80
struct touch_state {
    unsigned char down[TOUCH_BUTTON_COUNT];
    uint64_t until[TOUCH_BUTTON_COUNT];
    int16_t x, y;
};
static void touch_state_reset(struct touch_state *state) {
    memset(state, 0, sizeof(*state));
}
static void touch_state_button(struct touch_state *state, int button, int down, uint64_t now) {
    if (button < 0 || button >= TOUCH_BUTTON_COUNT) return;
    if (down && !state->down[button]) state->until[button] = now + TOUCH_TAP_MS;
    state->down[button] = down != 0;
}
static int touch_state_pressed(const struct touch_state *state, int button, uint64_t now) {
    return state->down[button] || now < state->until[button];
}
#endif
