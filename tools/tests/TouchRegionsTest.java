package com.halo.decomp;

public final class TouchRegionsTest {
    private static void require(boolean value) { if (!value) throw new AssertionError(); }
    private static void near(float actual, float expected) { require(Math.abs(actual-expected) < .0001f); }
    public static void main(String[] args) {
        TouchRegions r = new TouchRegions();
        // Two independently owned fingers; crossing the divider never reassigns one.
        require(r.down(17, 100, 100, 1000, 500, .5f, false) == TouchRegions.MOVE);
        require(r.down(29, 800, 200, 1000, 500, .5f, false) == TouchRegions.LOOK);
        require(r.down(30, 200, 300, 1000, 500, .5f, false) == TouchRegions.NONE);
        require(r.down(31, 900, 300, 1000, 500, .5f, false) == TouchRegions.NONE);
        require(r.down(17, 700, 100, 1000, 500, .5f, false) == TouchRegions.NONE);
        require(r.motion(17, 130, 85, 1000, 500, .06f, .06f) == TouchRegions.MOVE);
        near(r.moveX, .5f); near(r.moveY, -.5f);
        r.motion(17, 130, 85, 1000, 500, .06f, .06f);
        near(r.moveX, .5f); near(r.moveY, -.5f); // held displacement stays active
        r.motion(29, 400, 230, 1000, 500, .06f, .06f);
        near(r.lookX, -400); near(r.lookY, 30);
        r.motion(29, 400, 230, 1000, 500, .06f, .06f);
        near(r.lookX, 0); near(r.lookY, 0); // look never drifts while held still
        r.motion(17, 900, 800, 1000, 500, .06f, .06f);
        near(r.moveX, 1); near(r.moveY, 1);
        require(r.up(31) == TouchRegions.NONE); near(r.moveX, 1);
        require(r.up(29) == TouchRegions.LOOK); near(r.moveX, 1);
        require(r.up(17) == TouchRegions.MOVE); near(r.moveX, 0); near(r.moveY, 0);
        // Each new press gets a new floating origin, including after cancellation.
        require(r.down(40, 250, 150, 1000, 500, .5f, false) == TouchRegions.MOVE);
        near(r.moveX, 0); r.reset();
        require(r.motion(40, 300, 300, 1000, 500, .06f, .06f) == TouchRegions.NONE);
        near(r.moveX, 0);
        // Divider boundaries, handedness and proportional travel across resolutions.
        require(r.down(0, 500, 100, 1000, 500, .5f, false) == TouchRegions.LOOK); r.reset();
        require(r.down(0, 300, 100, 1000, 500, .3f, true) == TouchRegions.MOVE);
        r.motion(0, 250, 125, 1000, 500, .1f, .1f); near(r.moveX, -.5f); near(r.moveY, .5f); r.reset();
        require(r.down(0, 600, 200, 2000, 1000, .3f, true) == TouchRegions.MOVE);
        r.motion(0, 500, 250, 2000, 1000, .1f, .1f); near(r.moveX, -.5f); near(r.moveY, .5f); r.reset();
        require(r.down(0, 299, 100, 1000, 500, .3f, true) == TouchRegions.LOOK); r.reset();
        // Invalid/unknown events cannot create motion, take ownership or divide by zero.
        require(r.down(-1, 100, 100, 1000, 500, .5f, false) == TouchRegions.NONE);
        require(r.down(0, Float.NaN, 100, 1000, 500, .5f, false) == TouchRegions.NONE);
        require(r.down(0, 100, 100, 0, 500, .5f, false) == TouchRegions.NONE);
        require(r.down(0, 100, 100, 1000, 500, .9f, false) == TouchRegions.NONE);
        require(r.down(0, -1, 100, 1000, 500, .5f, false) == TouchRegions.NONE);
        require(r.down(0, 100, 100, 1000, 500, .5f, false) == TouchRegions.MOVE);
        require(r.motion(0, 200, 100, 1000, 500, 0, .06f) == TouchRegions.NONE);
        require(r.motion(0, Float.POSITIVE_INFINITY, 100, 1000, 500, .06f, .06f) == TouchRegions.NONE);
        near(r.moveX, 0);
        System.out.println("Screen-region ownership, movement, look, boundaries and reset checks passed.");
    }
}
