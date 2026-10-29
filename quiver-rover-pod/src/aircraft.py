"""Project Quiver PT3, the official build123d assembly.

vendor/project-quiver is Arrow-air/project-quiver @ 65f46e31681a, CERN-OHL-S.
That package is the mechanical master. This module only frames it:

- Their X is right and their Y is forward. A -90° rotation about Z makes
  X forward and Y left.
- Their foam sleeves bottom at Z = -547.89. The lift puts that contact on Z = 0.

Propeller disks are keep-out volumes added here. The STEP propellers are one
blade position, not the swept circle. The saddle and pins are still the
concept retention; the three 2112 plates stay inside the official assembly.
"""

from __future__ import annotations

import sys
from pathlib import Path

import build123d as bd
from cadgen import model

from adapter import adapter_parts
from common import viz
from parameters import KEEPOUT, MOTOR_OFFSET_MM, PROP_PLANE_Z, PROP_RADIUS_MM

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "vendor/project-quiver/src"))

from quiver.assembly import make_assembly  # noqa: E402


def _prop_sweeps():
    disks = []
    corners = ((1, -1), (1, 1), (-1, -1), (-1, 1))
    for sx, sy in corners:
        sweep = bd.Pos(sx * MOTOR_OFFSET_MM, sy * MOTOR_OFFSET_MM, PROP_PLANE_Z) * bd.Cylinder(
            PROP_RADIUS_MM,
            4,
            align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.CENTER),
        )
        viz(sweep, f"viz_prop_sweep_{sx}_{sy}", KEEPOUT)
        disks.append(sweep)
    return disks


@model
def official_quiver():
    assembly = make_assembly()
    if assembly is None:
        raise RuntimeError("Quiver assembly loaded no parts")
    assembly.label = "quiver_pt3"
    # Rotate about Z first, then lift. Z is the rotation axis, so the
    # foam contact rises by the full lift.
    return bd.Location((0, 0, -assembly.bounding_box().min.Z), (0, 0, -90)) * assembly


def aircraft_shape(engaged: bool = True, viz_on: bool = True, with_adapter: bool = True):
    parts = [official_quiver().shape]
    if with_adapter:
        parts.extend(adapter_parts(engaged))
    if viz_on:
        parts.extend(_prop_sweeps())
    return bd.Compound(children=parts, label="aircraft_quiver_pt3")


@model
def aircraft():
    return aircraft_shape(True, True)


@model
def aircraft_released():
    return aircraft_shape(False, True)


@model
def aircraft_rigid():
    return aircraft_shape(True, False)


if __name__ == "__main__":
    handle = aircraft()
    box = handle.shape.bounding_box()
    print("size", tuple(round(v, 1) for v in box.size))
    print(handle.id, handle.url)
