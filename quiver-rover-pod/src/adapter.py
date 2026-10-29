"""Concept retention around the official bottom 2112 plate.

The plate itself is inside the Quiver assembly, at the pose from that model.
This file does not place a second copy. The saddle and pins are still a
concept. They are not a measured mate to the quick-release.
"""

from __future__ import annotations

from pathlib import Path

import build123d as bd
from cadgen import model, read_step

from common import box, mass_match, petg
from parameters import (
    BELLY_Z,
    INTERFACE_GAP_MM,
    MOVING,
    PLACED_PLATE_MM,
    PLATE_BOTTOM_Z,
    PLATE_THICK_MM,
    RELEASE_ALLOWANCE_KG,
)

ROOT = Path(__file__).resolve().parents[1]
PLATE_PATH = ROOT / "vendor/quiver/2112_attach_plate.step"


def load_plate():
    """Return the official plate, thin axis along Z, centred on the origin."""
    plate = read_step(PLATE_PATH)
    # As imported, the 16 mm thickness is the Y axis of the STEP bbox.
    plate = plate.rotate(bd.Axis.X, 90)
    center = plate.bounding_box().center()
    plate = bd.Pos(-center.X, -center.Y, -center.Z) * plate
    return plate


def saddle_solid():
    # Placed plate is 50 mm in X and 66 mm in Y. A 2 mm gap keeps the
    # concept frame off the official solid.
    outer = box(PLACED_PLATE_MM[0] + 30.0, PLACED_PLATE_MM[1] + 30.0, PLATE_THICK_MM, 0, 0, PLATE_BOTTOM_Z)
    hole = box(
        PLACED_PLATE_MM[0] + 2.0,
        PLACED_PLATE_MM[1] + 2.0,
        PLATE_THICK_MM + 4.0,
        0,
        0,
        PLATE_BOTTOM_Z - 2.0,
    )
    return outer - hole


def release_collar():
    # The bottom spacer fills the opening directly above the plate, from the
    # plate top up to the lower plate. This allowance sits beside that spacer.
    collar = box(36, 20, 10, 78, 0, BELLY_Z + 2.0)
    return mass_match(
        collar,
        RELEASE_ALLOWANCE_KG,
        "release-allowance",
        MOVING,
        "conceptual_release_collar",
    )


def pins(engaged: bool):
    z0 = PLATE_BOTTOM_Z - INTERFACE_GAP_MM - 4.0 if engaged else PLATE_BOTTOM_Z + 1.0
    length = 12.0
    solids = []
    for x in (-22.0, 22.0):
        pin = bd.Pos(x, 0, z0) * bd.Cylinder(
            3.0, length, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN)
        )
        petg(pin, "retention_pin", MOVING)
        solids.append(pin)
    return solids


def adapter_parts(engaged: bool):
    saddle = saddle_solid()
    petg(saddle, "adapter_saddle_placeholder", "#c5cad0")
    return [saddle, release_collar(), *pins(engaged)]


@model
def adapter_saddle():
    saddle = saddle_solid()
    petg(saddle, "adapter_saddle_placeholder", "#c5cad0")
    return saddle


@model
def adapter_engaged():
    return bd.Compound(children=adapter_parts(True), label="adapter_retained")


@model
def adapter_released():
    return bd.Compound(children=adapter_parts(False), label="adapter_released")


if __name__ == "__main__":
    adapter_engaged()
    size = load_plate().bounding_box().size
    print("plate", tuple(round(v, 2) for v in size))
