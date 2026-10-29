"""Parachute display geometry.

No recovery system was selected. Mass is one placeholder allowance on the
packed envelope. The canopy, lines and load-path bar are visualisation only.
"""

from __future__ import annotations

import build123d as bd

from common import box, mass_match, rod, viz
from parameters import (
    CANOPY,
    CANOPY_DIAMETER_MM,
    CANOPY_HEIGHT_MM,
    CANOPY_WHITE,
    CHUTE_MAX_X,
    CHUTE_MIN_X,
    LINE_LENGTH_MM,
    MOVING,
    OUTER_LEN_MM,
    OUTER_WID_MM,
    PACKED_SIZE_MM,
    PARACHUTE_MASS_KG,
    POD_H_MM,
    SKID_H_MM,
)


def _chute_center():
    return ((CHUTE_MIN_X + CHUTE_MAX_X) / 2.0, 0.0, SKID_H_MM + 4.0)


def packed_parachute():
    sx, sy, sz = PACKED_SIZE_MM
    x, y, z = _chute_center()
    envelope = box(sx, sy, sz, x, y, z)
    mass_match(
        envelope,
        PARACHUTE_MASS_KG,
        "parachute-allowance",
        CANOPY,
        "packed_parachute_placeholder",
    )
    bag = box(sx + 8, sy + 8, sz + 6, x, y, z - 2)
    viz(bag, "viz_deployment_bag", CANOPY_WHITE)
    return [envelope, bag]


def lug_points(z=None):
    if z is None:
        z = POD_H_MM
    inset_x = 28.0
    inset_y = 28.0
    xs = (-OUTER_LEN_MM / 2.0 + inset_x, OUTER_LEN_MM / 2.0 - inset_x)
    ys = (-OUTER_WID_MM / 2.0 + inset_y, OUTER_WID_MM / 2.0 - inset_y)
    return [(x, y, z) for x in xs for y in ys]


def draped_lines(tangle=None):
    """Lines left across the exit path. Entanglement is unresolved."""
    if tangle is None:
        tangle = (OUTER_LEN_MM / 2.0 + 220.0, 0.0, 30.0)
    lines = []
    for start in lug_points(POD_H_MM - 4):
        line = rod(start, tangle, 1.6)
        viz(line, "viz_suspension_line", CANOPY_WHITE)
        lines.append(line)
    return lines


def deployed_canopy(pod_z: float = 0.0):
    """Canopy and lines above a pod whose skids are at pod_z."""
    ring_z = pod_z + POD_H_MM + LINE_LENGTH_MM
    confluence = (0.0, 0.0, pod_z + POD_H_MM + 180.0)
    lines = []
    for start in lug_points(pod_z + POD_H_MM):
        line = rod(start, confluence, 1.6)
        viz(line, "viz_bridle", CANOPY_WHITE)
        lines.append(line)
    riser = rod(confluence, (0, 0, ring_z), 2.4)
    viz(riser, "viz_load_path", "#f2c14e")
    lines.append(riser)
    radius = CANOPY_DIAMETER_MM / 2.0
    shell = bd.Cone(
        radius,
        80,
        CANOPY_HEIGHT_MM,
        align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN),
    )
    inner = bd.Pos(0, 0, 50) * bd.Cone(
        radius - 160,
        40,
        CANOPY_HEIGHT_MM - 120,
        align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN),
    )
    canopy = bd.Pos(0, 0, ring_z) * (shell - inner)
    viz(canopy, "viz_canopy", CANOPY)
    return [canopy, *lines]
