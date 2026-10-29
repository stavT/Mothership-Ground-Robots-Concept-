# Assumptions and open issues

This is a packaging concept. It is not a flight-qualified release, parachute, or landing system.

## Layout

Side-by-side was kept. Both rovers face forward and leave together. A fore-aft line is the smaller rectangle (about 681 × 286 mm against 468 × 537 mm) but the rear rover cannot leave forward without the front rover moving first, and an aft parachute bay blocks a rear door. The shared parachute stays one assembly. Individual parachutes were not substituted.

The pod planform is outside the published 300 mm attachment diameter. The corner radius is about 356 mm and the propeller-disk inner clearance is about 308 mm, so the pod footprint still sits under the disk circle. The disk solids are above the pod. The landing-gear tubes are a separate solid clash, described under Airframe.

## Mass

Robot kit mass and the aircraft empty weight and battery mass are manufacturer figures. Cell mass, parachute mass, release allowance, wiring, fasteners and the unallocated 0.20 kg are placeholders. Pod and adapter saddle masses are solid-PETG volume at the generic PETG density. They are not slicer masses. Simplified rovers, the battery envelope and the canopy are not weighed from their volume.

The result is over the 7.45 kg standard-battery allowance. The robot masses were not reduced. See `docs/VALIDATION.md` and `data/mass_budget.csv`.

Aircraft centre of gravity is not computed. The Dev-Kit mass table does not locate the empty weight. Payload centre of gravity is only as good as the part centroids of this approximate assembly.

## Airframe

The body is the official Quiver assembly. Red disks are propeller keep-out volumes. The STEP propellers stay at one blade angle. Official part colours are kept. The saddle, pins, and release block are still a concept around the real bottom plate.

The bottom 2112 plate is the real attach point, and it sits between the landing-gear legs. Those legs are 246 mm apart. The pod is 468 mm long, so the carried pod intersects the vertical tubes. One tube was measured at 1847 mm³ inside the pod. The pod was not shrunk to hide that. A pod on this plate has to be narrower than the leg gap, or the gear has to be redesigned. Neither change is in this model.

## Not designed

- Safe release altitude, inflation time, opening shock, descent rate, wind limit, safety factor, impact survival, or release timing. None of those numbers are in this model.
- A pyrotechnic cutter, a live release controller, or a flight command.
- A line-management scheme after landing. The ground scene keeps the lines across the exit. Their overlap with the rovers is reported rather than deleted.
- A manufacturer-compatible mate to the 2112 plate. The plate is the real solid. The saddle, lug and pins are a visual interface with a modelled gap except for the pins, which intentionally cross it.
- Hand access. The 25 mm side clearance and the wall windows show where a switch would have to be reached. They are not a demonstrated service procedure.
- Printability of the scaled display meshes. Uniform scale puts a 3 mm wall under the 1.2 mm FDM guide. Those STLs are display meshes. They are marked not flight hardware.

## Coordinate frame

Right-handed. X forward, Y left, Z up. Origin at the motor-pattern centre, Z = 0 on the landing-gear contact plane. Rover local Z = 0 is the wheel-contact plane. Pod local Z = 0 is the skid contact plane.
