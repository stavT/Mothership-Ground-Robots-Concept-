# Source and provenance

Retrieved 2026-10-28. Geometry units are millimetres. Mass units are kilograms.

## Aircraft

Standard battery configuration from the [Dev-Kit engineering report](https://arrowair.com/quiver/Engineering-Reports/Dev-Kit-Engineering-Report):

| Item | Value | Check |
| --- | --- | --- |
| MTOW | 25.00 kg | stated limit |
| Empty weight | 9.65 kg | stated, battery excluded |
| Standard battery | 14S 20 Ah, 7.90 kg | stated |
| Payload allowance | 7.45 kg | 25.00 − 9.65 − 7.90 |

The long-endurance 30 Ah row is 11.40 kg and leaves 3.95 kg. The public "5–8 kg" line is that spread, not the standard-config allowance. A PT2 note that prints "5,030 kg" of remaining payload is a units error in that note (it is about 5 kg on the heavy battery) and is not used here.

Published airframe size, from the [PT2 engineering report](https://arrowair.com/quiver/Engineering-Reports/PT2-Engineering-Report): unfolded 930 × 930 mm with propellers still folded, overall height 640 mm, attachment space 400 mm high and 300 mm in diameter. The 930 mm figure is interpreted here as the bounding width of the four motor housings. That interpretation is not a fusion-model measurement.

Propulsion: Hobbywing XRotor X6 Plus, 790 g including the MFP 24×8.0 propeller, 69.4 mm motor diameter, 30 mm arm tube. Four units are 3.16 kg, which matches the Dev-Kit propulsion line. The airframe body is mass-matched to 9.65 − 3.16 = 6.49 kg. Subsystem masses in the Dev-Kit table are mostly still TBD, so there is no aircraft centre-of-gravity solution.

Official solid: `vendor/quiver/2112_attach_plate.step` from [project-quiver](https://github.com/Arrow-air/project-quiver) commit `65f46e31681abdd8263119dc28d586d3d82ec971` (2026-10-24). SHA-256 `776bdb825010e2ae61a114ef3930059b9b8db2345885f9795ee000255eeecda0`. Licence CERN-OHL-S. See `vendor/quiver/README.md`. Placed size after rotating the thin axis onto Z: 66 × 50 × 16 mm. The pose on this airframe is an assumption. The saddle around it is not a measured mate.

The airframe in the scenes is the official assembly, `vendor/project-quiver`, which is [project-quiver](https://github.com/Arrow-air/project-quiver) commit `65f46e31681abdd8263119dc28d586d3d82ec971` (2026-10-24). `src/quiver/assembly.py` places 44 STEP files and the generated tubes. CERN-OHL-S applies to that tree. This study does not modify it. A copy of the 2112 plate also remains at `vendor/quiver/2112_attach_plate.step` for the standalone size check.

Their frame has X to the right and Y forward. The study rotates the assembly −90° about Z and lifts it 547.89 mm so the foam sleeves sit on Z = 0. In that pose the bottom 2112 plate underside is at Z = 376.89 mm. The published 400 mm attachment height is the clearance figure, not this measured face.

Payload software contract: [PAYLOAD_SPEC.md](https://github.com/Arrow-air/quiver-sdk/blob/main/PAYLOAD_SPEC.md) at quiver-sdk commit `4572d0c80fef17a50a0288b33458ab1a1c2db699`. That document is electrical and software. It does not define the mechanical plate.

## Robots

Selected configuration: **UGV Rover PT PI5 ROS2 Kit** (pan-tilt, Raspberry Pi host included, ROS 2 Humble, D500 lidar, OAK-D Lite, 160° camera). Product page and wiki, retrieved 2026-10-28:

- https://www.waveshare.com/ugv-rover-ros2-kit.htm
- https://www.waveshare.com/wiki/UGV_Rover_PI_ROS2

| Published | Value |
| --- | --- |
| Size L×W×H | 230.42 × 252.40 × 254.53 mm |
| Mass | 2251 ± 5 g |
| Tyres | Ø80 mm, width 42.5 mm on the product page (the wiki prints 42 mm) |
| Ground clearance | 25 mm |
| Battery | 18650 × 3, not included |

The 2251 g figure is shared by the Pi 4 and Pi 5 rows. It does not include the cells. This study adds 3 × 48 g as a placeholder cell mass, 0.144 kg, and does not treat 2.251 kg as a ready-to-run mass. Ready mass used here is 2.395 kg each.

Axis assignment is inferred. Three 80 mm tyres fit along 252.40 mm with a 6 mm gap and overlap if forced along 230.42 mm. Fore-aft is therefore 252.40 mm and lateral is 230.42 mm. No wheelbase drawing was found. No Waveshare CAD was found, and none is redistributed. The rover solid is approximate reference geometry inside that envelope. Its chassis carries the 2.251 kg by a tuned density. The solid volume is not an aluminium mass.

## Parachute

No recovery-system datasheet was selected. Packed size, canopy diameter, line length and the 0.85 kg allowance are placeholders. The canopy is a display shell, not a fabric model and not a descent calculation.

## Toolchain

cadgen 0.8.2, pinned, with build123d and Open CASCADE via the plugin at `~/.cursor/plugins/local/text-to-cad`. The launcher could not be written to `~/.local/bin` from this environment. Commands use `uvx --from cadgen==0.8.2`.
