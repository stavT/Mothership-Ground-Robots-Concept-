# Quiver rover pod

Engineering notes for the study in the repository root. Pictures, the demo, and the mass summary are in the [root README](../README.md).

Frame: millimetres, right-handed, X forward, Y left, Z up. Origin at the motor-pattern centre. Z = 0 is the landing-gear contact plane. Masses are kilograms.

## Open a scene

`cadgen run src/scenes.py` prints a local viewer link. The id is stable. The token rotates.

Scene ids:

| Scene | Id |
| --- | --- |
| Flight | `e63a05e7-ed4e-5af3-81de-ef57b12410cd` |
| Cutaway | `8ee1d2cf-e741-591c-9c0d-5286288e1e7b` |
| Exploded | `57376a86-f9de-57b3-8984-45d64aa810cf` |
| Separated, parachute still packed | `e8cf280a-8d0c-58b3-8329-e711a141f003` |
| Descent, aircraft omitted | `8dda1ec7-3068-504a-a977-57e3e47de4ff` |
| Ground exit | `f96bff9d-5129-55b5-81c1-11a80d53bee9` |
| Empty carrier | `539c267d-a410-5a4b-8c06-a7c1e39ef138` |

The closed pod has a revolute joint named `ramp` and a sequence `open_ramp`.

## Rebuild

From this directory. `cadgen` 0.8.2 is pinned. The `~/.local/bin/cadgen` launcher was not writable here, so the command is `uvx`.

```bash
cd "/Users/maytalsaar-tsechansky/Desktop/Cad Fun/quiver-rover-pod"
uvx --no-config --managed-python --python 3.13 --from cadgen==0.8.2 cadgen run src/exports.py
uvx --no-config --managed-python --python 3.13 --from cadgen==0.8.2 cadgen run src/checks.py
MPLCONFIGDIR="$PWD/tmp/mpl" uvx --no-config --managed-python --python 3.13 --from cadgen==0.8.2 cadgen run src/pod_drawing.py
```

Edit `src/parameters.py`. Do not copy dimensions into the part scripts.

## Layout of the source

| File | Contents |
| --- | --- |
| `src/parameters.py` | Dimensions, masses, colours, scene offsets |
| `src/aircraft.py` | Official Quiver assembly, framed into this study |
| `src/robot.py` | One rover, instanced twice |
| `src/adapter.py` | Official 2112 plate plus a provisional saddle |
| `src/pod.py` | Tray, walls, ramp, skids, lugs |
| `src/parachute.py` | Packed envelope and display canopy |
| `src/scenes.py` | The seven states |
| `src/exports.py` | STEP, GLB, XBF, STL, 3MF |
| `src/checks.py` | Clearance and the mass ledger |
| `src/pod_drawing.py` | Tray concept sheet |

## Outputs

- `GLB/` and `XBF/` for the seven states
- `STEP/flight_rigid.step` plus individual custom parts
- `STL/` and `3MF/` display meshes, scaled to fit a 180 mm cube, labelled not flight hardware
- `PDF/pod_tray_concept.pdf`
- `previews/`
- `data/mass_budget.csv`, `data/bom.csv`
- `docs/PROVENANCE.md`, `docs/LAYOUT.md`, `docs/ASSUMPTIONS.md`, `docs/VALIDATION.md`
- `vendor/quiver/2112_attach_plate.step` under CERN-OHL-S

## Mass, short form

Standard-battery allowance is 7.45 kg. Carried payload in this study is 10.447 kg. Margin is −2.997 kg. Takeoff is 27.997 kg against a 25.00 kg MTOW. The rover kit masses were not reduced. Pod mass is solid PETG volume, not a slicer result. Detail is in `docs/VALIDATION.md`.
