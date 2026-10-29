"""Approximate Waveshare UGV Rover PT PI ROS2 reference.

The published envelope is the constraint. Internal splits are not a
manufacturer drawing. Mass is assigned to the chassis so the kit mass is the
published 2.251 kg; the solid is not an aluminium shell.
"""

from __future__ import annotations

import math

import build123d as bd
from cadgen import model

from common import box, mass_match, tag, viz
from parameters import (
    APPROX,
    AXLES_X,
    CAMERA_FOV_DEG,
    GROUND_CLEARANCE_MM,
    NON_PT_ROS2_HEIGHT_MM,
    ROBOT_1,
    ROBOT_2,
    ROBOT_BATTERY_MASS_KG,
    ROBOT_HGT_MM,
    ROBOT_KIT_MASS_KG,
    ROBOT_LEN_MM,
    ROBOT_WID_MM,
    TIRE,
    TIRE_DIAMETER_MM,
    TIRE_WIDTH_MM,
    WHEEL_DEPICTED_GAP_MM,
    WHEEL_Y,
)


def _wheel(x: float, y: float, driven: bool):
    radius = TIRE_DIAMETER_MM / 2.0
    center_z = radius + WHEEL_DEPICTED_GAP_MM
    solid = bd.Cylinder(
        radius,
        TIRE_WIDTH_MM,
        align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.CENTER),
    )
    solid = solid.located(bd.Plane(origin=(x, y, center_z), z_dir=(0, 1, 0)).location)
    # Density stays negligible: the kit mass lives on the chassis.
    return tag(solid, "wheel_driven" if driven else "wheel_idler", TIRE if driven else "#3a3a3a")


def robot_shape(suffix: str, color: str, flip_y: bool = False):
    half_l = 100.0
    chassis_w = ROBOT_WID_MM - 2.0 * TIRE_WIDTH_MM - 2.0
    chassis = box(2 * half_l, chassis_w, 95.0, 0, 0, GROUND_CLEARANCE_MM)
    mass_match(chassis, ROBOT_KIT_MASS_KG, f"rover-kit-{suffix}", color, "chassis_approximate")

    cells = box(70.0, 54.0, 18.0, -70.0, 0.0, 120.2)
    mass_match(
        cells,
        ROBOT_BATTERY_MASS_KG,
        f"18650-pack-{suffix}",
        "#22262b",
        "battery_cells_18650_form",
    )

    lidar = bd.Pos(20, 0, 122) * bd.Cylinder(
        26, 31, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN)
    )
    tag(lidar, "lidar_d500_placeholder", APPROX)

    neck = bd.Pos(40, 0, NON_PT_ROS2_HEIGHT_MM) * bd.Cylinder(
        16, 40, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN)
    )
    head_z = NON_PT_ROS2_HEIGHT_MM + 40.0
    head_h = ROBOT_HGT_MM - head_z
    head = box(64.0, 48.0, head_h, 55.0, 0.0, head_z)
    tag(neck, "pan_tilt_neck_approximate", color)
    tag(head, "pan_tilt_head_approximate", color)

    camera = box(18.0, 28.0, 16.0, 96.0, 0.0, head_z + head_h * 0.45)
    tag(camera, "oak_camera_placeholder", "#111111")

    half = math.radians(CAMERA_FOV_DEG / 2.0)
    reach = 18.0
    wedge = bd.Pos(108, 0, head_z + head_h * 0.55) * bd.extrude(
        bd.Polygon(
            (0, 0),
            (reach * math.cos(half), reach * math.sin(half)),
            (reach * math.cos(half), -reach * math.sin(half)),
        ),
        6,
    )
    viz(wedge, "viz_camera_fov", "#f0d78c")

    switch = bd.Cylinder(5, 8, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.CENTER))
    switch = switch.located(
        bd.Plane(origin=(-15, chassis_w / 2.0 + 3.0, 100), z_dir=(0, 1, 0)).location
    )
    tag(switch, "power_switch_approximate", "#e07a2f")
    port = bd.Cylinder(4, 8, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.CENTER))
    port = port.located(
        bd.Plane(origin=(12, chassis_w / 2.0 + 3.0, 78), z_dir=(0, 1, 0)).location
    )
    tag(port, "charge_port_approximate", "#111111")

    wheels = []
    for axle in AXLES_X:
        driven = axle != 0.0
        wheels.append(_wheel(axle, WHEEL_Y, driven))
        wheels.append(_wheel(axle, -WHEEL_Y, driven))

    contact = box(140, 70, 0.4, 0, 0, 0.2)
    viz(contact, "viz_wheel_contact_plane", "#88a0b8")

    pad = 3.0
    envelope = bd.Pos(0, 0, 40) * _wire_box(ROBOT_LEN_MM + 2 * pad, ROBOT_WID_MM + 2 * pad, ROBOT_HGT_MM - 40)
    viz(envelope, "viz_bounding_envelope", APPROX)

    parts = [chassis, cells, lidar, neck, head, camera, wedge, switch, port, contact, envelope, *wheels]
    assembly = bd.Compound(children=parts, label=f"robot_{suffix}_approximate")
    if flip_y:
        assembly = assembly.mirror(bd.Plane.XZ)
        assembly.label = f"robot_{suffix}_approximate"
    return assembly


def _wire_box(sx, sy, sz):
    t = 1.2
    z0 = 0.0
    edges = []
    for z in (z0, sz):
        edges.append(box(sx, t, t, 0, sy / 2, z))
        edges.append(box(sx, t, t, 0, -sy / 2, z))
        edges.append(box(t, sy, t, sx / 2, 0, z))
        edges.append(box(t, sy, t, -sx / 2, 0, z))
    for x in (-sx / 2, sx / 2):
        for y in (-sy / 2, sy / 2):
            edges.append(box(t, t, sz, x, y, z0))
    solid = edges[0]
    for edge in edges[1:]:
        solid = solid + edge
    return solid


@model
def robot_1():
    return robot_shape("1", ROBOT_1, flip_y=False)


@model
def robot_2():
    return robot_shape("2", ROBOT_2, flip_y=True)


if __name__ == "__main__":
    robot_1()
    robot_2()
