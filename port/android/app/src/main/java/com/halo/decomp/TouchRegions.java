package com.halo.decomp;

/** Xash-style floating movement and relative look, independent of Android events.
 * Behaviour reference: FWGS/xash3d-fwgs in_touch.c, d6b54aaf6c1d8518e08404a842f3f6ee02cef3cc.
 * OpenCE implementation: movement still feeds the SDL virtual gamepad.
 */
final class TouchRegions {
    static final int NONE = 0, MOVE = 1, LOOK = 2;
    private int moveFinger = -1, lookFinger = -1;
    private float startX, startY, lastLookX, lastLookY;
    float moveX, moveY, lookX, lookY;

    int down(int finger, float x, float y, int width, int height, float split, boolean moveRight) {
        if (finger < 0 || role(finger) != NONE || !point(x, y, width, height) ||
                x < 0 || x > width || y < 0 || y > height ||
                !Float.isFinite(split) || split < .2f || split > .8f) return NONE;
        boolean movement = moveRight ? x >= split * width : x < split * width;
        if (movement) {
            if (moveFinger >= 0) return NONE;
            moveFinger = finger; startX = x; startY = y; moveX = moveY = 0;
            return MOVE;
        }
        if (lookFinger >= 0) return NONE;
        lookFinger = finger; lastLookX = x; lastLookY = y; lookX = lookY = 0;
        return LOOK;
    }

    int motion(int finger, float x, float y, int width, int height, float sideZone, float forwardZone) {
        lookX = lookY = 0;
        if (!point(x, y, width, height)) return NONE;
        int role = role(finger);
        if (role == MOVE) {
            if (!Float.isFinite(sideZone) || !Float.isFinite(forwardZone) || sideZone <= 0 || forwardZone <= 0)
                return NONE;
            // Xash's _move uses the initial touch and independent screen fractions.
            moveX = clamp((x - startX) / (width * sideZone));
            moveY = clamp((y - startY) / (height * forwardZone));
        } else if (role == LOOK) {
            // Pixel deltas preserve OpenCE's existing swipe sensitivity and SDL path.
            lookX = x - lastLookX; lookY = y - lastLookY;
            lastLookX = x; lastLookY = y;
        }
        return role;
    }

    int up(int finger) {
        int role = role(finger);
        if (role == MOVE) { moveFinger = -1; moveX = moveY = 0; }
        else if (role == LOOK) { lookFinger = -1; lookX = lookY = 0; }
        return role;
    }

    void reset() { moveFinger = lookFinger = -1; moveX = moveY = lookX = lookY = 0; }
    private int role(int finger) {
        if (finger < 0) return NONE;
        return finger == moveFinger ? MOVE : finger == lookFinger ? LOOK : NONE;
    }
    private static boolean point(float x, float y, int width, int height) {
        return width > 0 && height > 0 && Float.isFinite(x) && Float.isFinite(y);
    }
    private static float clamp(float value) { return Math.max(-1f, Math.min(1f, value)); }
}
