"""Shared shape helpers. Geometry is millimetres."""

from __future__ import annotations

import build123d as bd
from bd_materials import metals, plastics


def volume_mm3(shape) -> float:
    value = shape.volume
    return float(value() if callable(value) else value)


def tag(shape, label: str, color: str, material=None):
    if material is not None:
        shape.material = material
    shape.color = color
    shape.label = label
    return shape


def mass_match(shape, mass_kg: float, name: str, color: str, label: str):
    volume = volume_mm3(shape)
    if volume <= 0:
        raise RuntimeError(f"{name} has no volume")
    density = mass_kg / (volume * 1e-9)
    shape.material = metals.custom_metal(name, density=density)
    shape.color = color
    shape.label = label
    return shape


def petg(shape, label: str, color: str):
    shape.material = plastics.petg()
    shape.color = color
    shape.label = label
    return shape


def viz(shape, label: str, color: str, transparent: bool = True):
    shape.material = metals.custom_metal(label, density=1.0, transparent=transparent)
    try:
        shape.material.pbr = shape.material.pbr.override(transmission=1, opacity=0.28)
    except Exception:
        pass
    shape.color = color
    shape.label = label
    return shape


def box(sx, sy, sz, x, y, z):
    """Box centred in X and Y, bottom at z."""
    solid = bd.Box(sx, sy, sz, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN))
    return bd.Pos(x, y, z) * solid


def rod(p0, p1, radius: float):
    start = bd.Vector(*p0)
    end = bd.Vector(*p1)
    axis = end - start
    length = axis.length
    if length <= 0:
        raise RuntimeError("rod length is zero")
    cyl = bd.Cylinder(
        radius,
        length,
        align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN),
    )
    return cyl.located(bd.Plane(origin=start, z_dir=axis).location)


def fuse(parts):
    solid = parts[0]
    for part in parts[1:]:
        solid = solid + part
    return solid
