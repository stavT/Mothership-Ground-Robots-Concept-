# Layout

Frame and numbers live in `src/parameters.py`.

## Choice

|  | Side-by-side (used) | Fore-aft (rejected) |
| --- | --- | --- |
| Plan | 468 × 537 mm | 681 × 286 mm |
| Exit | both rovers forward, 20 mm apart | rear rover blocked by the front rover |
| Parachute | aft bay, roof left clear for the adapter | an aft bay consumes the rear door |
| Attachment diameter 300 mm | exceeded | exceeded |
| Gear clearance | gear is 90 mm outside the pod corners | the longer body closes that gap |

Side-by-side is the arrangement that gives both rovers a clear forward path and keeps the parachute off the attachment face. It is not the smallest rectangle.

## Carried position

Skids are about 74 mm above the ground plane. The pod roof and lug meet the hanging 2112 plate with a 0.5 mm modelled gap. Pins cross that gap in the retained state and sit up inside the saddle when released. Separation in the separated scene is an illustrative 1500 mm from the belly plane to the pod roof, marked by a yellow bar. It is not a release trajectory.

## Exit

The ramp hinge is the forward lower edge. The open angle is the angle that puts the ramp tip on the ground. Chassis stops are on the ramp and swing out with it. The ground scene places both rovers ahead of the open ramp, still side by side, so they do not cross. Lines from the corner lugs are drawn into that corridor anyway.

## Exploded stack

Bottom to top, same parts as the closed assembly, not copies with different geometry:

1. Aircraft reference, adapter removed.
2. Adapter, retained pose, lifted to Z = 780 mm.
3. Pod structure, parachute removed, lifted to Z = 1200 mm.
4. Packed parachute envelope, Z = 1750 mm.
5. Rover 1 (blue) and rover 2 (green), Z = 2100 mm, offset in plan so they do not stack on each other.

## What the colours mean

| Colour | Part |
| --- | --- |
| Dark gray | Aircraft reference |
| Light gray | Pod structure |
| Blue / green | Rover 1 / rover 2 |
| Orange | Ramp, stops, pins, release allowance |
| Orange and white | Parachute display |
| Translucent red | Propeller disks and sensor keep-outs |

Approximate reference parts are labelled `approximate` in the model tree. Anything labelled `viz_` is a display solid or curve, not a manufactured part. The canopy is a shell. The lines are thin cylinders.
