"""Write the files the concept study keeps."""

from __future__ import annotations

from pathlib import Path

from cadgen import export, model

from adapter import adapter_saddle
from aircraft import aircraft_shape
from parameters import DISPLAY_MARK, DISPLAY_SCALE
from pod import bridle_lug, pod_ramp, pod_skid, pod_tray, pod_wall
from robot import robot_1
from scenes import cutaway, descent, empty_carrier, exploded, flight, flight_rigid, ground, separated

ROOT = Path(__file__).resolve().parents[1]


def _dst(*parts):
    path = ROOT.joinpath(*parts)
    path.parent.mkdir(parents=True, exist_ok=True)
    return path


def _write(handle, *paths):
    for path in paths:
        path.parent.mkdir(parents=True, exist_ok=True)
    export(handle, *paths)
    print(f"{handle.id} {handle.url}")


@model
def display_aircraft():
    shape = aircraft_shape(engaged=True, viz_on=False).scale(DISPLAY_SCALE)
    shape.label = f"{DISPLAY_MARK} aircraft"
    return shape


@model
def display_tray():
    shape = pod_tray().shape.scale(DISPLAY_SCALE)
    shape.label = f"{DISPLAY_MARK} pod_tray"
    return shape


@model
def display_robot():
    shape = robot_1().shape.scale(DISPLAY_SCALE)
    shape.label = f"{DISPLAY_MARK} robot_1"
    return shape


def main():
    _write(flight(), _dst("GLB/flight.glb"), _dst("XBF/flight.xbf"))
    _write(flight_rigid(), _dst("STEP/flight_rigid.step"), _dst("XBF/flight_rigid.xbf"))
    _write(cutaway(), _dst("GLB/cutaway.glb"), _dst("XBF/cutaway.xbf"))
    _write(exploded(), _dst("GLB/exploded.glb"), _dst("XBF/exploded.xbf"))
    _write(separated(), _dst("GLB/separated.glb"), _dst("XBF/separated.xbf"))
    _write(descent(), _dst("GLB/descent.glb"), _dst("XBF/descent.xbf"))
    _write(ground(), _dst("GLB/ground.glb"), _dst("XBF/ground.xbf"))
    _write(empty_carrier(), _dst("GLB/empty_carrier.glb"), _dst("XBF/empty_carrier.xbf"))
    _write(pod_tray(), _dst("STEP/pod_tray.step"))
    _write(pod_ramp(), _dst("STEP/pod_ramp.step"))
    _write(pod_wall(), _dst("STEP/pod_wall.step"))
    _write(pod_skid(), _dst("STEP/pod_skid.step"))
    _write(adapter_saddle(), _dst("STEP/adapter_saddle.step"))
    _write(bridle_lug(), _dst("STEP/bridle_lug.step"))
    _write(
        display_tray(),
        _dst("STL/display_pod_tray_NOT_FLIGHT_HARDWARE.stl"),
        _dst("3MF/display_pod_tray_NOT_FLIGHT_HARDWARE.3mf"),
    )
    _write(display_aircraft(), _dst("STL/display_aircraft_NOT_FLIGHT_HARDWARE.stl"))
    _write(display_robot(), _dst("STL/display_robot_1_NOT_FLIGHT_HARDWARE.stl"))


if __name__ == "__main__":
    main()
