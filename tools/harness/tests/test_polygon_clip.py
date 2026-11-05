"""The real convex_hull2d_intersect and convex_polygon2d_clip_to_plane (source/math/geometry.c): a corner of a portal's
outline lying on a clip line, with the corner before it a rounding error behind, makes no NaN corner (0/0 at the
crossing), which spread through the portal walk and left whole clusters undrawn for a frame (the level flashing)."""

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from harness import CHECK_FAILED, build, constant, function, inline, mutated, read, run  # noqa: E402

CASES = ["shared-corners-a", "shared-corners-b", "ordinary-clip"]

# a fault and the case that must catch it
# Historical portal captures are positive tests. Their rare 0/0 is not
# reproducible on every compiler, so use a deterministic NaN injection to
# prove the production corner guard is still required.
NEGATIVE_CONTROLS = {
    "nan-guard-removed": (("if (scale != scale) scale = 0.f;\n", ""), "nan-corner", True),
    "no-clip": (("result_count = convex_polygon2d_clip_to_plane(", "result_count = 0 * convex_polygon2d_clip_to_plane("),
                "shared-corners-a", False),
}

HELPERS = ["square_root", "magnitude_squared2d", "magnitude2d", "scale_vector2d", "normalize2d", "dot_product2d",
           "vector_from_points2d", "point_from_line2d", "plane2d_from_points", "plane2d_distance_to_point"]


def generated(fault=None, force_nan=False):
    real_math = read("source/math/real_math.h")
    geometry = read("source/math/geometry.c")
    code = "#define CLIP_BUFFER_SIZE %d\n" % constant(geometry, "CLIP_BUFFER_SIZE")
    code += "\n".join(inline(real_math, name) for name in HELPERS) + "\n"
    intersect = function(geometry, "vector_intersect_plane2d")
    if force_nan:
        # Simulate the floating-point 0/0 observed at real portal corners.
        # Only the fixture's x=0 crossing is affected; clip code stays real.
        intersect = mutated(intersect, "{\n\treturn", "{\n\tif (point->x == 0.f) return NAN;\n\treturn")
    code += "static " + intersect + "\n"
    clip = "static " + function(geometry, "convex_polygon2d_clip_to_plane") + "\n"
    hull = "static " + function(geometry, "convex_hull2d_intersect") + "\n"
    if fault:
        before, after = fault
        if before in clip:
            clip = mutated(clip, before, after)
        else:
            hull = mutated(hull, before, after)
    return (("under_test.inc", code + clip + hull),)


@pytest.mark.parametrize("case", CASES)
def test_case(case):
    status, output = run(build("polygon_clip", generated()), case)
    assert status == 0, output


def test_nan_guard_on_forced_degenerate_crossing():
    status, output = run(build("polygon_clip", generated(force_nan=True)), "nan-corner")
    assert status == 0, output


@pytest.mark.parametrize("control", NEGATIVE_CONTROLS)
def test_negative_control(control):
    fault, case, force_nan = NEGATIVE_CONTROLS[control]
    status, output = run(build("polygon_clip", generated(fault, force_nan=force_nan)), case)
    assert status == CHECK_FAILED, f"the clip with a fault ({control}) passed '{case}': the test cannot see it"
