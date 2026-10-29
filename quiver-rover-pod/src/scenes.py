"""Presentation states. Each function is its own document, not one stacked model."""

from __future__ import annotations

import build123d as bd
from cadgen import model

from adapter import adapter_parts
from aircraft import aircraft_released, aircraft_shape
from common import box, rod, viz
from parachute import deployed_canopy, draped_lines, packed_parachute
from parameters import (
    CARRIED_POD_Z,
    PLATE_BOTTOM_Z,
    LUG_H_MM,
    OUTER_LEN_MM,
    POD_H_MM,
    ROBOT_CENTER_X,
    ROBOT_CENTER_Y,
    ROBOT_LEN_MM,
    SEPARATION_MM,
    SKID_H_MM,
)
from pod import pod, pod_cutaway, pod_open, pod_parts
from robot import robot_1, robot_2

EXIT_X = OUTER_LEN_MM / 2.0 + 180.0 + ROBOT_LEN_MM / 2.0 + 30.0


def _scale():
    cube = box(100, 100, 100, 0, 0, 0)
    viz(cube, "viz_scale_100mm", "#111111", transparent=False)
    bar = box(500, 12, 12, 360, 0, 0)
    viz(bar, "viz_scale_500mm", "#111111", transparent=False)
    return bd.Pos(0, -980, 0) * bd.Compound(children=[cube, bar], label="scale_reference")


def _robots(z, x):
    blue = bd.Pos(x, ROBOT_CENTER_Y, z) * robot_1().shape
    green = bd.Pos(x, -ROBOT_CENTER_Y, z) * robot_2().shape
    blue.label = "robot_1_approximate"
    green.label = "robot_2_approximate"
    return blue, green


def _flight(viz_on: bool, cutaway: bool):
    craft = aircraft_shape(engaged=True, viz_on=viz_on)
    pod_shape = (pod_cutaway() if cutaway else pod()).shape
    pod_shape = bd.Pos(0, 0, CARRIED_POD_Z) * pod_shape
    pod_shape.label = "transport_pod"
    robots = _robots(CARRIED_POD_Z + SKID_H_MM, ROBOT_CENTER_X)
    return bd.Compound(
        children=[craft, pod_shape, *robots, _scale()],
        label="flight_cutaway" if cutaway else "flight",
    )


@model
def flight():
    return _flight(True, False)


@model
def flight_rigid():
    return _flight(False, False)


@model
def cutaway():
    return _flight(True, True)


@model
def exploded():
    craft = aircraft_shape(engaged=True, viz_on=False, with_adapter=False)
    adapter = bd.Pos(0, 0, 780) * bd.Compound(children=adapter_parts(True), label="adapter_retained")
    structure = [
        part
        for part in pod_parts("closed")
        if "parachute" not in (part.label or "") and "deployment" not in (part.label or "")
    ]
    pod_shape = bd.Pos(0, 0, 1200) * bd.Compound(children=structure, label="transport_pod")
    chute = bd.Pos(0, 0, 1750) * bd.Compound(children=packed_parachute(), label="packed_parachute")
    blue, green = _robots(2100, 0)
    blue = bd.Pos(-220, 180, 0) * blue
    green = bd.Pos(220, -180, 0) * green
    return bd.Compound(
        children=[craft, adapter, pod_shape, chute, blue, green, _scale()],
        label="exploded",
    )


@model
def separated():
    craft = aircraft_shape(engaged=False, viz_on=True)
    pod_z = PLATE_BOTTOM_Z - SEPARATION_MM - POD_H_MM - LUG_H_MM
    pod_shape = bd.Pos(0, 0, pod_z) * pod().shape
    pod_shape.label = "transport_pod"
    robots = _robots(pod_z + SKID_H_MM, ROBOT_CENTER_X)
    marker = rod(
        (OUTER_LEN_MM, 0, PLATE_BOTTOM_Z - SEPARATION_MM),
        (OUTER_LEN_MM, 0, PLATE_BOTTOM_Z),
        3,
    )
    viz(marker, "viz_separation_1500mm", "#f2c14e")
    return bd.Compound(
        children=[craft, pod_shape, *robots, marker, _scale()],
        label="separated_payload",
    )


@model
def descent():
    pod_shape = pod().shape
    pod_shape.label = "transport_pod"
    robots = _robots(SKID_H_MM, ROBOT_CENTER_X)
    canopy = deployed_canopy(0.0)
    return bd.Compound(children=[pod_shape, *robots, *canopy, _scale()], label="parachute_descent")


@model
def ground():
    pod_shape = pod_open().shape
    pod_shape.label = "transport_pod_open"
    blue, green = _robots(0.0, EXIT_X)
    lines = draped_lines((EXIT_X, 0.0, 40.0))
    return bd.Compound(
        children=[pod_shape, blue, green, *lines, _scale()],
        label="ground_exit",
    )


@model
def empty_carrier():
    return bd.Compound(
        children=[aircraft_released().shape, _scale()],
        label="empty_carrier",
    )


if __name__ == "__main__":
    for scene in (flight, cutaway, exploded, separated, descent, ground, empty_carrier):
        handle = scene()
        print(f"{scene.__name__} {handle.id} {handle.url}")
