package com.halo.decomp;

/** libmain's SDL virtual controller; IDs 0..14 are SDL gamepad buttons,
 * 15/16 are the left/right triggers. No keyboard events enter profile text. */
final class TouchInput {
    static native void button(int button, boolean down);
    static native void move(float x, float y);
    static native void reset();
    static native int mode();
    private TouchInput() {}
}
