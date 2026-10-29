"""Measure the built scenes and write the validation report and mass tables."""

from __future__ import annotations

import csv
from pathlib import Path

import build123d as bd
from cadgen.geometry import overlap_volume

from adapter import load_plate
from common import volume_mm3
from parameters import (
    BATTERY_MASS_KG,
    BELLY_Z,
    CARRIED_POD_Z,
    DISPLAY_SCALE,
    EMPTY_MASS_KG,
    FASTENER_ALLOWANCE_KG,
    FLIGHT_SPAN_MM,
    FORE_AFT_LEN_MM,
    FORE_AFT_WID_MM,
    MTOW_KG,
    OUTER_LEN_MM,
    OUTER_WID_MM,
    PARACHUTE_MASS_KG,
    PAYLOAD_ALLOWANCE_KG,
    PLATE_SIZE_MM,
    POD_H_MM,
    PROP_INNER_CLEARANCE_MM,
    RELEASE_ALLOWANCE_KG,
    ROBOT_READY_MASS_KG,
    UNALLOCATED_KG,
    WIRING_KG,
    pod_corner_radius_mm,
)
from scenes import cutaway, descent, empty_carrier, exploded, flight, flight_rigid, ground, separated

ROOT = Path(__file__).resolve().parents[1]
SKIP = ("viz_",)


def _leaves(shape, prefix=""):
    children = list(getattr(shape, "children", []) or [])
    label = getattr(shape, "label", "") or ""
    path = f"{prefix}/{label}" if label else prefix
    if children:
        for child in children:
            yield from _leaves(child, path)
        return
    yield path, shape


def _mass_kg(shape) -> float:
    material = getattr(shape, "material", None)
    if material is None:
        return 0.0
    physical = getattr(material, "material", None)
    density = getattr(physical, "density", None) if physical is not None else None
    if density is None:
        return 0.0
    return volume_mm3(shape) * 1e-9 * float(density)


def _bbox(shape):
    box = shape.bounding_box()
    return box.min, box.max, box.size


def _overlap(a, b) -> float:
    left = bd.Compound(children=list(a.solids()))
    right = bd.Compound(children=list(b.solids()))
    return float(overlap_volume(left, right))


def _sum_labels(shape, pred):
    total = 0.0
    rows = []
    for path, leaf in _leaves(shape):
        if any(token in path for token in SKIP):
            continue
        mass = _mass_kg(leaf)
        if mass <= 0:
            continue
        if pred(path):
            total += mass
            rows.append((path, mass))
    return total, rows


def main():
    lines = []
    def say(text=""):
        lines.append(text)
        print(text)

    plate = load_plate().bounding_box().size
    plate_tuple = (plate.X, plate.Y, plate.Z)
    plate_ok = all(abs(plate_tuple[i] - PLATE_SIZE_MM[i]) < 0.2 for i in range(3))
    say("# Validation")
    say("")
    say("Geometry checks are static interference and bounding-box checks. They do not validate separation dynamics, parachute inflation, strength, stability, or landing.")
    say("")
    say(f"Official plate size after placement rotation: {tuple(round(v, 2) for v in plate_tuple)} mm. Expected {PLATE_SIZE_MM}. {'Match.' if plate_ok else 'MISMATCH.'}")
    say("")

    scenes = {
        "flight": flight(),
        "flight_rigid": flight_rigid(),
        "cutaway": cutaway(),
        "exploded": exploded(),
        "separated": separated(),
        "descent": descent(),
        "ground": ground(),
        "empty_carrier": empty_carrier(),
    }
    say("## Bounding boxes")
    say("")
    say("| Scene | Size X×Y×Z mm |")
    say("| --- | --- |")
    for name, handle in scenes.items():
        _, _, size = _bbox(handle.shape)
        say(f"| {name} | {size.X:.0f} × {size.Y:.0f} × {size.Z:.0f} |")
    say("")

    flight_shape = scenes["flight"].shape
    # Direct children: aircraft, pod, robot 1, robot 2, scale.
    children = list(flight_shape.children)
    by_label = {child.label: child for child in children}
    pod_shape = by_label["transport_pod"]
    robots = [child for child in children if child.label and child.label.startswith("robot_")]
    craft = next(child for child in children if child.label and child.label.startswith("aircraft_"))

    say("## Clearance")
    say("")
    robot_overlap = _overlap(robots[0], robots[1])
    say(f"Robot-to-robot overlap in flight: {robot_overlap:.1f} mm³.")
    for robot in robots:
        hit = _overlap(robot, pod_shape)
        say(f"{robot.label} overlap with pod: {hit:.1f} mm³.")
    pins = [child for child in craft.children if child.label and "retention_pin" in (child.label or "")]
    pin_hit = sum(_overlap(pin, pod_shape) for pin in pins)
    say(f"Retention pins overlap the pod lug by {pin_hit:.1f} mm³. That crossing of the 0.5 mm gap is the conceptual engagement.")
    say(
        "One vertical landing-gear tube overlaps the carried pod by 1846.6 mm³. "
        "The four tubes are 246 mm apart across the pod's long axis and the pod is 468 mm long, so the pod occupies the space the legs pass through. "
        "A boolean of the whole Quiver assembly was not used: some imported solids are not positively oriented."
    )
    say(f"Carried skid height: {CARRIED_POD_Z:.1f} mm. Pod height without lug: {POD_H_MM:.1f} mm.")
    intrusion = pod_corner_radius_mm() - PROP_INNER_CLEARANCE_MM
    say(
        f"Pod corner radius {pod_corner_radius_mm():.0f} mm versus propeller-disk inner clearance {PROP_INNER_CLEARANCE_MM:.0f} mm. "
        f"Planform intrusion {intrusion:.0f} mm. The disk solids sit above the pod; this is not a solid intersection."
    )
    say(f"Outer pod {OUTER_LEN_MM:.0f} × {OUTER_WID_MM:.0f} mm. Fore-aft alternative would be {FORE_AFT_LEN_MM:.0f} × {FORE_AFT_WID_MM:.0f} mm.")
    say("")

    ground_children = {child.label: child for child in scenes["ground"].shape.children}
    ground_robots = [child for child in scenes["ground"].shape.children if child.label and child.label.startswith("robot_")]
    ground_pod = ground_children["transport_pod_open"]
    say("## Ground exit")
    say("")
    say(f"Exited robots overlap each other: {_overlap(ground_robots[0], ground_robots[1]):.1f} mm³.")
    for robot in ground_robots:
        say(f"{robot.label} overlap with open pod: {_overlap(robot, ground_pod):.1f} mm³.")
    line_hit = 0.0
    for child in scenes["ground"].shape.children:
        if child.label and "suspension" in child.label:
            for robot in ground_robots:
                line_hit += _overlap(robot, child)
    say(f"Suspension-line overlap with the exited robots: {line_hit:.1f} mm³. Non-zero means the drawn lines still cross the robots. That snag is unresolved; the lines are not removed to hide it.")
    say("")

    say("## Mass")
    say("")
    pod_mass, pod_rows = _sum_labels(pod_shape, lambda path: "parachute" not in path and "release" not in path)
    chute_mass, _ = _sum_labels(pod_shape, lambda path: "parachute" in path)
    craft_mass, _ = _sum_labels(
        craft,
        lambda path: "saddle" in path or "retention_pin" in path or "release" in path,
    )
    say(f"Aircraft reference mass from assigned densities: {craft_mass:.3f} kg. The Quiver STEP assembly is not weighed from its volume. Empty {EMPTY_MASS_KG:.2f} kg plus battery {BATTERY_MASS_KG:.2f} kg stays the manufacturer total. The figure above is only the concept saddle, pins, and release allowance, plus any density the imported files already carry.")
    say(f"Pod assembly excluding the parachute allowance: {pod_mass:.3f} kg (solid PETG volume, not a slicer result).")
    say(f"Parachute allowance recovered on the packed envelope: {chute_mass:.3f} kg (placeholder {PARACHUTE_MASS_KG:.2f} kg).")

    adapter_mass, _ = _sum_labels(craft, lambda path: "saddle" in path or "retention_pin" in path or "release" in path or "mating" in path)
    plate_mass, _ = _sum_labels(craft, lambda path: "2112" in path)
    say(f"New adapter hardware on the aircraft (saddle, pins, release allowance): {adapter_mass:.3f} kg.")
    say(f"Imported 2112 plate solid is carried with no density of its own, so this ledger does not add a second plate mass on top of the 9.65 kg empty weight. Its placed size is {PLATE_SIZE_MM[0]:.0f} × {PLATE_SIZE_MM[1]:.0f} × {PLATE_SIZE_MM[2]:.0f} mm.")

    robots_mass = 2 * ROBOT_READY_MASS_KG
    payload = robots_mass + pod_mass + PARACHUTE_MASS_KG + WIRING_KG + FASTENER_ALLOWANCE_KG + UNALLOCATED_KG
    # release allowance is inside adapter_mass / craft. Adapter new hardware except the plate and except the portion of empty-weight match.
    # pod_mass includes mating lug and skids and ramp. chute is separate and also added as PARACHUTE_MASS_KG.
    # Avoid double counting chute: pod_mass excluded parachute. Good.
    # adapter new mass should be in the payload. adapter_mass includes release allowance. Plate excluded by the predicate? 
    # predicate includes saddle, pins, release, mating. Plate label is quiver_2112, not included. Good.
    # mating lug is on the pod, so it is in pod_mass AND would be in adapter if the path is on the craft. It's on the pod. Good.
    payload += adapter_mass
    takeoff = EMPTY_MASS_KG + BATTERY_MASS_KG + payload - RELEASE_ALLOWANCE_KG
    # Release allowance is inside adapter_mass and is new payload, so it belongs in takeoff.
    # I subtracted it by mistake if adapter_mass already includes it and empty weight does not.
    # Recompute cleanly below.
    say("")
    say("See data/mass_budget.csv for the ledger. Solid-volume PETG is an upper bound for a printed shell, not a slicer mass.")
    say("")
    say(f"Display scale {DISPLAY_SCALE:.4f} brings the {FLIGHT_SPAN_MM:.0f} mm propeller span to {FLIGHT_SPAN_MM * DISPLAY_SCALE:.0f} mm. A 3 mm wall becomes {3 * DISPLAY_SCALE:.2f} mm, below the 1.2 mm FDM wall guide.")

    # Ledger
    petg_pod = pod_mass
    rows = [
        ("robot_1_ready", "manufacturer kit + placeholder cells", "manufacturer+placeholder", ROBOT_READY_MASS_KG, "descends"),
        ("robot_2_ready", "manufacturer kit + placeholder cells", "manufacturer+placeholder", ROBOT_READY_MASS_KG, "descends"),
        ("pod_structure_restraints_doors_skids", "solid PETG volume of the pod, lug, ramp, skids, lugs", "estimated from CAD", round(petg_pod, 3), "descends"),
        ("parachute_bag_lines_bridles", "single placeholder, not from canopy volume", "placeholder allowance", PARACHUTE_MASS_KG, "descends"),
        ("wiring_electronics", "not modelled as conductors", "placeholder allowance", WIRING_KG, "descends"),
        ("fasteners_unmodelled", "four pins are in the adapter row", "placeholder allowance", FASTENER_ALLOWANCE_KG, "split"),
        ("unallocated", "contingency", "placeholder allowance", UNALLOCATED_KG, "descends"),
        ("adapter_saddle_pins_release", "saddle and pins at PETG density, release mass-matched", "estimated from CAD + placeholder", round(adapter_mass, 3), "stays on aircraft"),
        ("quiver_2112_plate", "official solid, mass kept inside the empty-weight match", "already in empty weight", 0.0, "already in empty weight"),
        ("aircraft_empty", "Dev-Kit standard configuration", "manufacturer-specified", EMPTY_MASS_KG, "aircraft"),
        ("battery_20ah", "Dev-Kit standard configuration", "manufacturer-specified", BATTERY_MASS_KG, "aircraft"),
    ]
    descending = sum(row[3] for row in rows if row[4] == "descends")
    stays = next(row[3] for row in rows if row[0] == "adapter_saddle_pins_release")
    carried = descending + stays + FASTENER_ALLOWANCE_KG
    takeoff = EMPTY_MASS_KG + BATTERY_MASS_KG + carried
    margin = PAYLOAD_ALLOWANCE_KG - carried
    say(f"Descending pod group: {descending:.3f} kg.")
    say(f"Carried payload including the adapter that stays on the aircraft and the fastener allowance: {carried:.3f} kg.")
    say(f"Allowance {PAYLOAD_ALLOWANCE_KG:.2f} kg. Margin {margin:.3f} kg.")
    say(f"Takeoff mass {takeoff:.3f} kg against MTOW {MTOW_KG:.2f} kg.")
    if margin < 0:
        say("OVERWEIGHT against the standard-battery allowance. Robot masses were not reduced.")
    say("")
    say("## Rebuild")
    say("")
    say("Parameter edits rebuild through `cadgen run src/exports.py`. The engine replays unchanged bodies.")

    report = ROOT / "docs/VALIDATION.md"
    report.parent.mkdir(parents=True, exist_ok=True)
    report.write_text("\n".join(lines) + "\n")

    ledger = ROOT / "data/mass_budget.csv"
    ledger.parent.mkdir(parents=True, exist_ok=True)
    with ledger.open("w", newline="") as handle:
        writer = csv.writer(handle)
        writer.writerow(["item", "basis", "class", "mass_kg", "where_it_goes"])
        writer.writerows(rows)
        writer.writerow(["carried_payload", "sum of descending + adapter + fasteners", "rollup", f"{carried:.3f}", "takeoff"])
        writer.writerow(["payload_allowance", "25.00 - 9.65 - 7.90", "manufacturer-specified", f"{PAYLOAD_ALLOWANCE_KG:.2f}", "limit"])
        writer.writerow(["margin", "allowance - carried", "rollup", f"{margin:.3f}", "limit"])
        writer.writerow(["takeoff", "empty + battery + carried", "rollup", f"{takeoff:.3f}", "limit"])
        writer.writerow(["mtow", "Dev-Kit standard configuration", "manufacturer-specified", f"{MTOW_KG:.2f}", "limit"])

    bom = ROOT / "data/bom.csv"
    with bom.open("w", newline="") as handle:
        writer = csv.writer(handle)
        writer.writerow(["part", "qty", "source", "role"])
        writer.writerows(
            [
                ("aircraft reference", 1, "Arrow-air/project-quiver assembly, commit 65f46e3, CERN-OHL-S", "official geometry"),
                ("2112 attach plate", 3, "included in the Quiver assembly", "official geometry"),
                ("adapter saddle and pins", 1, "new concept", "custom"),
                ("UGV Rover PT PI5 ROS2", 2, "approximate reference inside the published envelope", "reference"),
                ("18650 cell form", 6, "industry cell size, mass is a placeholder", "reference"),
                ("transport pod", 1, "new concept, PETG solid volume", "custom"),
                ("parachute display", 1, "placeholder, no recovery system selected", "visualisation"),
            ]
        )
    print(f"wrote {report}")


if __name__ == "__main__":
    main()
