"""Central parameters for the Quiver rover-pod concept.

Units: millimetres and kilograms. Frame: right-handed, X forward, Y left, Z up.
Origin: motor-pattern centre, Z = 0 on the landing-gear contact plane.

Published numbers are named in docs/PROVENANCE.md. Every other number is an
explicit assumption. Do not treat a tuned density as a material property.
"""

from __future__ import annotations

import math

# --- retrieved configuration -------------------------------------------------
# Dev-Kit standard battery row. 25.00 - 9.65 - 7.90 = 7.45 exactly.
MTOW_KG = 25.00
EMPTY_MASS_KG = 9.65
BATTERY_MASS_KG = 7.90
PAYLOAD_ALLOWANCE_KG = MTOW_KG - EMPTY_MASS_KG - BATTERY_MASS_KG  # 7.45

# Hobbywing X6 Plus, MFP 24×8.0, mass includes the propeller.
MOTOR_MASS_KG = 0.790
MOTOR_DIAMETER_MM = 69.4
MOTOR_HEIGHT_MM = 40.3
ARM_TUBE_DIAMETER_MM = 30.0
PROP_DIAMETER_IN = 24.0
PROP_DIAMETER_MM = PROP_DIAMETER_IN * 25.4  # 609.6
PROP_RADIUS_MM = PROP_DIAMETER_MM / 2.0

# Published envelope. The CAD model below replaces these as the airframe.
UNFOLDED_SPAN_MM = 930.0  # props still folded; not the span of the STEP assembly
OVERALL_HEIGHT_MM = 640.0

# Measured from vendor/project-quiver @ 65f46e3. Their frame is X right,
# Y forward, Z up. This study rotates -90° about Z, then lifts the foam
# sleeves onto Z = 0. Motor centres land on the diagonals at ±433 mm.
QUIVER_LIFT_MM = 547.89
MOTOR_OFFSET_MM = 433.0
MOTOR_RADIUS_MM = math.hypot(MOTOR_OFFSET_MM, MOTOR_OFFSET_MM)
PROP_INNER_CLEARANCE_MM = MOTOR_RADIUS_MM - PROP_RADIUS_MM
PROP_PLANE_Z = 53.8 + QUIVER_LIFT_MM

# Standalone 2112 STEP after the thin axis is turned onto Z: 66 × 50 × 16.
# In this frame the bottom plate's long axis follows Y, so the placed
# footprint is 50 × 66 × 16. Underside was Z = -171 before the lift.
PLATE_SIZE_MM = (66.0, 50.0, 16.0)
PLACED_PLATE_MM = (50.0, 66.0, 16.0)
PLATE_THICK_MM = PLATE_SIZE_MM[2]
PLATE_BOTTOM_Z = -171.0 + QUIVER_LIFT_MM  # 376.89
BELLY_Z = PLATE_BOTTOM_Z + PLATE_THICK_MM  # top of the bottom interface plate
BODY_GAP_MM = 0.2

# Selected robot: UGV Rover PT PI5 ROS2 Kit. Batteries are not in the 2251 g.
ROBOT_LEN_MM = 252.40  # fore-aft; axis assignment is inferred, see PROVENANCE
ROBOT_WID_MM = 230.42
ROBOT_HGT_MM = 254.53
ROBOT_KIT_MASS_KG = 2.251
CELL_MASS_KG = 0.048  # placeholder, not a Waveshare figure
CELLS_PER_ROBOT = 3
ROBOT_BATTERY_MASS_KG = CELL_MASS_KG * CELLS_PER_ROBOT  # 0.144
ROBOT_READY_MASS_KG = ROBOT_KIT_MASS_KG + ROBOT_BATTERY_MASS_KG  # 2.395
TIRE_DIAMETER_MM = 80.0
TIRE_WIDTH_MM = 42.5  # product page; the wiki prints 42 mm
GROUND_CLEARANCE_MM = 25.0
CAMERA_FOV_DEG = 160.0
NON_PT_ROS2_HEIGHT_MM = 153.55  # same kit family without the pan-tilt

# --- pod packaging -----------------------------------------------------------
GAP_Y_MM = 20.0
CLEAR_SIDE_MM = 25.0
CLEAR_FORE_MM = 30.0
CLEAR_AFT_MM = 30.0
CHUTE_BAY_LEN_MM = 150.0
WALL_MM = 3.0
RAIL_MM = 16.0
SKID_H_MM = 25.0
SKID_W_MM = 18.0
HEADROOM_MM = 15.0
ROOF_T_MM = 3.0
FLOOR_T_MM = 4.0
RAMP_LEN_MM = 180.0
RAMP_T_MM = 4.0
LUG_H_MM = 12.0
INTERFACE_GAP_MM = 0.5
GEAR_MARGIN_MM = 90.0
WHEEL_DEPICTED_GAP_MM = 0.2

ROBOT_CENTER_Y = GAP_Y_MM / 2.0 + ROBOT_WID_MM / 2.0
INNER_WID_MM = 2.0 * (ROBOT_CENTER_Y + ROBOT_WID_MM / 2.0 + CLEAR_SIDE_MM)
BAY_LEN_MM = ROBOT_LEN_MM + CLEAR_FORE_MM + CLEAR_AFT_MM
INNER_LEN_MM = BAY_LEN_MM + CHUTE_BAY_LEN_MM
OUTER_WID_MM = INNER_WID_MM + 2.0 * WALL_MM
OUTER_LEN_MM = INNER_LEN_MM + 2.0 * WALL_MM
POD_H_MM = SKID_H_MM + ROBOT_HGT_MM + HEADROOM_MM + ROOF_T_MM

INNER_MIN_X = -OUTER_LEN_MM / 2.0 + WALL_MM
CHUTE_MIN_X = INNER_MIN_X
CHUTE_MAX_X = CHUTE_MIN_X + CHUTE_BAY_LEN_MM
ROBOT_AFT_X = CHUTE_MAX_X + CLEAR_AFT_MM
ROBOT_CENTER_X = ROBOT_AFT_X + ROBOT_LEN_MM / 2.0

LUG_TOP_WORLD = PLATE_BOTTOM_Z - INTERFACE_GAP_MM
CARRIED_POD_Z = LUG_TOP_WORLD - LUG_H_MM - POD_H_MM

GEAR_X = OUTER_LEN_MM / 2.0 + GEAR_MARGIN_MM
GEAR_Y = OUTER_WID_MM / 2.0 + GEAR_MARGIN_MM

AXLE_X = ROBOT_LEN_MM / 2.0 - TIRE_DIAMETER_MM / 2.0
AXLES_X = (-AXLE_X, 0.0, AXLE_X)
WHEEL_Y = ROBOT_WID_MM / 2.0 - TIRE_WIDTH_MM / 2.0

RAMP_OPEN_DEG = math.degrees(math.acos(-SKID_H_MM / RAMP_LEN_MM))

# Rejected fore-aft package, same clearances, chute at the aft end.
FORE_AFT_WID_MM = ROBOT_WID_MM + 2.0 * CLEAR_SIDE_MM + 2.0 * WALL_MM
FORE_AFT_LEN_MM = 2.0 * ROBOT_LEN_MM + GAP_Y_MM + CHUTE_BAY_LEN_MM + 2.0 * WALL_MM

# --- parachute display placeholders (not a recovery-system selection) --------
PARACHUTE_MASS_KG = 0.85
PACKED_SIZE_MM = (130.0, 110.0, 80.0)
CANOPY_DIAMETER_MM = 2500.0
CANOPY_HEIGHT_MM = 800.0
LINE_LENGTH_MM = 3500.0
SEPARATION_MM = 1500.0  # illustrative gap from belly plane to pod roof

# Allowances. Not computed from CAD volume.
RELEASE_ALLOWANCE_KG = 0.12
WIRING_KG = 0.08
FASTENER_ALLOWANCE_KG = 0.05
UNALLOCATED_KG = 0.20

# Aircraft reference proportions (approximate).
BODY_L_MM = 460.0
BODY_W_MM = 320.0
BODY_Z = BELLY_Z + BODY_GAP_MM
BODY_TOP_Z = OVERALL_HEIGHT_MM
BODY_H_MM = BODY_TOP_Z - BODY_Z
ARM_Z = 520.0
# Inferred 20 Ah envelope: PT2 30 Ah box is 333 mm long; length scaled by 7.90/11.20.
BATTERY_ENVELOPE_MM = (235.0, 251.0, 103.0)

# Display derivative. 170 mm leaves margin inside a 180 mm cube.
FLIGHT_SPAN_MM = 2.0 * (MOTOR_OFFSET_MM + PROP_RADIUS_MM)
DISPLAY_SCALE = 170.0 / FLIGHT_SPAN_MM
DISPLAY_MARK = "DISPLAY MODEL — NOT FLIGHT HARDWARE"

# Colours.
AIRFRAME = "#2c3138"
POD = "#d5d8dc"
POD_DARK = "#b7bcc2"
ROBOT_1 = "#2f6fed"
ROBOT_2 = "#2e8b57"
MOVING = "#e07a2f"
CANOPY = "#ff6a00"
CANOPY_WHITE = "#f4f1ea"
KEEPOUT = "#e23b3b"
BATTERY = "#3d4a3a"
TIRE = "#1a1a1a"
APPROX = "#8e97a3"

PROPULSION_MASS_KG = 4.0 * MOTOR_MASS_KG
AIRFRAME_MATCH_KG = EMPTY_MASS_KG - PROPULSION_MASS_KG


def pod_corner_radius_mm() -> float:
    return math.hypot(OUTER_LEN_MM / 2.0, OUTER_WID_MM / 2.0)


def _audit() -> None:
    if abs(PAYLOAD_ALLOWANCE_KG - 7.45) > 1e-9:
        raise RuntimeError("payload allowance drifted from 7.45 kg")
    side_gap = INNER_WID_MM / 2.0 - (ROBOT_CENTER_Y + ROBOT_WID_MM / 2.0)
    if abs(side_gap - CLEAR_SIDE_MM) > 1e-6:
        raise RuntimeError(f"side clearance is {side_gap}, expected {CLEAR_SIDE_MM}")
    robot_fore = ROBOT_CENTER_X + ROBOT_LEN_MM / 2.0
    inner_fore = OUTER_LEN_MM / 2.0 - WALL_MM
    if abs((inner_fore - robot_fore) - CLEAR_FORE_MM) > 1e-6:
        raise RuntimeError("fore clearance does not match CLEAR_FORE_MM")
    if CARRIED_POD_Z < 40.0:
        raise RuntimeError(f"carried ground clearance only {CARRIED_POD_Z:.1f} mm")
    if RAMP_LEN_MM <= SKID_H_MM:
        raise RuntimeError("ramp cannot reach the ground")
    if pod_corner_radius_mm() <= PROP_INNER_CLEARANCE_MM:
        raise RuntimeError("expected the pod footprint to violate the prop-disk circle")


_audit()
