# quiver-pod-drop

27-second film of the Quiver rover-pod concept study. A Project Quiver carrier lets go of one pod. The pod descends under one parachute, the ramp meets the ground, and two Waveshare rovers sit ahead of it. The end sheet states the study result: takeoff 27.997 kg against a 25.00 kg limit. This is not flight hardware.

The stills are the scene exports from the CAD study (`flight`, `cutaway`, `separated`, `descent`, `ground`, `empty_carrier`). This repo does not redistribute the Quiver STEP tree. The 2112 plate in that study stays under CERN-OHL-S in the CAD project.

## Preview

```bash
npx hyperframes preview
```

Render, after the preview looks right:

```bash
npx hyperframes render
```

## Sound

Two bundled effects: a whoosh on the release, a bass impact on the ground cut. There is no music bed. Catalog music needs the HeyGen CLI (`https://developers.heygen.com/cli`, then `heygen auth login --oauth`).

## Numbers on the end sheet

From the concept mass ledger. Standard-battery allowance is 7.45 kg. Carried payload in the study is 10.447 kg. Margin is −2.997 kg. Takeoff is 27.997 kg. MTOW is 25.00 kg.
