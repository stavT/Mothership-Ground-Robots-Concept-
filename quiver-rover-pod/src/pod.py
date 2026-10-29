"""Detachable transport pod. Custom rigid parts use generic PETG density.

Side-by-side bays, parachute bay aft, ramp at the forward face. The ramp
joint is the retained mechanism; chocks are fused to the ramp so they leave
the bay with it.
"""

from __future__ import annotations

import build123d as bd
from cadgen import model
from cadgen.ap242 import configuration_sequence, mechanism_state

from common import box, fuse, petg, rod
from parachute import lug_points, packed_parachute
from parameters import (
    AXLE_X,
    CHUTE_MAX_X,
    CLEAR_FORE_MM,
    INNER_WID_MM,
    MOVING,
    OUTER_LEN_MM,
    OUTER_WID_MM,
    POD,
    POD_DARK,
    POD_H_MM,
    RAMP_LEN_MM,
    RAMP_OPEN_DEG,
    RAMP_T_MM,
    ROBOT_CENTER_X,
    ROBOT_CENTER_Y,
    ROBOT_LEN_MM,
    ROOF_T_MM,
    SKID_H_MM,
    SKID_W_MM,
    TIRE_WIDTH_MM,
    WALL_MM,
    WHEEL_Y,
    LUG_H_MM,
)


def _rail_frame():
    z = SKID_H_MM
    h = 12.0
    t = 14.0
    length = OUTER_LEN_MM
    width = OUTER_WID_MM
    rails = [
        box(length, t, h, 0, width / 2 - t / 2, z),
        box(length, t, h, 0, -(width / 2 - t / 2), z),
        box(t, width, h, length / 2 - t / 2, 0, z),
        box(t, width, h, -(length / 2 - t / 2), 0, z),
        box(80, t, h, CHUTE_MAX_X - 70, 0, z),
    ]
    return fuse(rails)


def _pockets():
    plates = []
    x = ROBOT_CENTER_X
    for sign in (1.0, -1.0):
        center = sign * ROBOT_CENTER_Y
        for local in (WHEEL_Y, -WHEEL_Y):
            plates.append(
                box(ROBOT_LEN_MM + 16, TIRE_WIDTH_MM + 8, 3, x, center + local, SKID_H_MM - 3)
            )
    return fuse(plates)


def tray_solid():
    return _rail_frame() + _pockets()


def _opening(length, height, thick):
    plate = bd.Box(length, thick, height, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN))
    window = bd.Pos(0, 0, height * 0.22) * bd.Box(
        length * 0.62,
        thick + 4,
        height * 0.48,
        align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN),
    )
    return plate - window


def side_wall(side: float):
    height = POD_H_MM - SKID_H_MM
    wall = _opening(OUTER_LEN_MM - 8, height, WALL_MM)
    y = side * (OUTER_WID_MM / 2.0 - WALL_MM / 2.0)
    return bd.Pos(0, y, SKID_H_MM) * wall


def aft_wall():
    height = POD_H_MM - SKID_H_MM
    wall = _opening(OUTER_WID_MM - 28, height, WALL_MM)
    wall = wall.rotate(bd.Axis.Z, 90)
    x = -OUTER_LEN_MM / 2.0 + WALL_MM / 2.0
    return bd.Pos(x, 0, SKID_H_MM) * wall


def bulkhead():
    from parameters import CHUTE_MAX_X

    height = POD_H_MM - SKID_H_MM - 20
    plate = bd.Box(
        WALL_MM,
        INNER_WID_MM - 10,
        height,
        align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN),
    )
    return bd.Pos(CHUTE_MAX_X, 0, SKID_H_MM + 8) * plate


def header():
    """Front panel above the ramp."""
    z = SKID_H_MM + RAMP_LEN_MM
    height = POD_H_MM - z
    plate = bd.Box(
        WALL_MM,
        INNER_WID_MM,
        height,
        align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN),
    )
    x = OUTER_LEN_MM / 2.0 - WALL_MM / 2.0
    return bd.Pos(x, 0, z) * plate


def roof_solid():
    length = OUTER_LEN_MM
    width = OUTER_WID_MM
    plate = bd.Box(length, width, ROOF_T_MM, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN))
    # Leave the parachute bay visible from above and keep a centre pad.
    hole = bd.Pos(-OUTER_LEN_MM * 0.22, 0, -1) * bd.Box(
        OUTER_LEN_MM * 0.28,
        OUTER_WID_MM * 0.55,
        ROOF_T_MM + 4,
        align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN),
    )
    roof = plate - hole
    return bd.Pos(0, 0, POD_H_MM - ROOF_T_MM) * roof


def mating_lug():
    lug = box(58, 42, LUG_H_MM, 0, 0, POD_H_MM)
    return lug


def skid_solid(side: float):
    y = side * (OUTER_WID_MM / 2.0 - 12.0)
    return box(OUTER_LEN_MM - 10, SKID_W_MM, SKID_H_MM, 0, y, 0)


def ramp_solid():
    hx = OUTER_LEN_MM / 2.0
    plate = box(RAMP_T_MM, INNER_WID_MM - 6, RAMP_LEN_MM, hx - RAMP_T_MM / 2.0, 0, SKID_H_MM)
    chocks = []
    inner = hx - RAMP_T_MM
    for sign in (1.0, -1.0):
        chock = box(14, 36, 18, inner - 6.5, sign * ROBOT_CENTER_Y, SKID_H_MM + 2)
        chocks.append(chock)
    return fuse([plate, *chocks])


def _lugs():
    parts = []
    for x, y, z in lug_points(POD_H_MM - 2):
        # lug_points returns the roof height; drop the lug onto the roof edge.
        parts.append(box(18, 18, 16, x, y, POD_H_MM - 14))
    return parts


def _place_ramp(ramp, angle: float):
    if angle == 0:
        return ramp
    axis = bd.Axis((OUTER_LEN_MM / 2.0, 0, SKID_H_MM), (0, 1, 0))
    return ramp.rotate(axis, angle)


def pod_parts(mode: str = "closed"):
    """mode: closed, cutaway, open."""
    tray = tray_solid()
    petg(tray, "pod_tray", POD)
    left = side_wall(1)
    right = side_wall(-1)
    aft = aft_wall()
    wall = bulkhead()
    top_header = header()
    roof = roof_solid()
    lug = mating_lug()
    left_skid = skid_solid(1)
    right_skid = skid_solid(-1)
    ramp = ramp_solid()
    for solid, label in (
        (left, "pod_wall_left"),
        (right, "pod_wall_right"),
        (aft, "pod_wall_aft"),
        (wall, "chute_bulkhead"),
        (top_header, "front_header"),
        (roof, "pod_roof"),
        (lug, "provisional_mating_lug"),
        (left_skid, "landing_skid_left"),
        (right_skid, "landing_skid_right"),
        (ramp, "ramp_and_chocks"),
    ):
        petg(solid, label, POD_DARK if "skid" in label or label == "chute_bulkhead" else POD)
    petg(lug, "provisional_mating_lug", MOVING)
    petg(ramp, "ramp_and_chocks", MOVING)

    lugs = []
    for solid in _lugs():
        petg(solid, "bridle_lug_placeholder", MOVING)
        lugs.append(solid)

    parts = [tray, left, aft, wall, top_header, lug, left_skid, right_skid, *lugs]
    if mode != "cutaway":
        parts.append(right)
        parts.append(roof)
    angle = RAMP_OPEN_DEG if mode == "open" else 0.0
    parts.append(_place_ramp(ramp, angle))
    if mode != "open":
        parts.extend(packed_parachute())
    else:
        # Packed canopy stays in the bay after landing. Lines are added by the scene.
        parts.extend(packed_parachute())
    return parts


def _with_joint(parts):
    tray = parts[0]
    ramp = next(part for part in parts if part.label == "ramp_and_chocks")
    hinge = bd.Axis((OUTER_LEN_MM / 2.0, 0, SKID_H_MM), (0, 1, 0))
    bd.RevoluteJoint("ramp", tray, axis=hinge, angular_range=(0, 110))
    bd.RigidJoint(
        "ramp",
        ramp,
        bd.Plane(origin=hinge.position, z_dir=hinge.direction).location,
    )
    tray.joints["ramp"].connect_to(ramp.joints["ramp"], angle=0)
    assembly = bd.Compound(children=parts, label="transport_pod")
    mechanism_state(assembly, "closed", ramp=0)
    mechanism_state(assembly, "open", ramp=RAMP_OPEN_DEG)
    configuration_sequence(assembly, "open_ramp", [(0, "closed"), (2.5, "open")])
    return assembly


@model
def pod():
    return _with_joint(pod_parts("closed"))


@model
def pod_cutaway():
    return bd.Compound(children=pod_parts("cutaway"), label="transport_pod_cutaway")


@model
def pod_open():
    return bd.Compound(children=pod_parts("open"), label="transport_pod_open")


@model
def pod_tray():
    solid = tray_solid()
    petg(solid, "pod_tray", POD)
    return solid


@model
def pod_ramp():
    solid = ramp_solid()
    petg(solid, "ramp_and_chocks", MOVING)
    return solid


@model
def pod_wall():
    solid = side_wall(1)
    petg(solid, "pod_wall_left", POD)
    return solid


@model
def pod_skid():
    solid = skid_solid(1)
    petg(solid, "landing_skid_left", POD_DARK)
    return solid


@model
def bridle_lug():
    solid = box(18, 18, 16, 0, 0, 0)
    petg(solid, "bridle_lug_placeholder", MOVING)
    return solid


if __name__ == "__main__":
    pod()
    pod_open()
