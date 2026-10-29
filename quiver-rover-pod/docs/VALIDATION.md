# Validation

Geometry checks are static interference and bounding-box checks. They do not validate separation dynamics, parachute inflation, strength, stability, or landing.

Official plate size after placement rotation: (66.0, 50.0, 16.0) mm. Expected (66.0, 50.0, 16.0). Match.

## Bounding boxes

| Scene | Size X×Y×Z mm |
| --- | --- |
| flight | 1476 × 1768 × 742 |
| flight_rigid | 1347 × 1695 × 742 |
| cutaway | 1476 × 1768 × 742 |
| exploded | 1347 × 1695 × 2356 |
| separated | 1476 × 1768 × 2174 |
| descent | 2500 × 2500 × 4598 |
| ground | 934 × 1298 × 310 |
| empty_carrier | 1476 × 1768 × 742 |

## Clearance

Robot-to-robot overlap in flight: 0.0 mm³.
robot_1_approximate overlap with pod: 0.0 mm³.
robot_2_approximate overlap with pod: 0.0 mm³.
Retention pins overlap the pod lug by 226.2 mm³. That crossing of the 0.5 mm gap is the conceptual engagement.
One vertical landing-gear tube overlaps the carried pod by 1846.6 mm³. The four tubes are 246 mm apart across the pod's long axis and the pod is 468 mm long, so the pod occupies the space the legs pass through. A boolean of the whole Quiver assembly was not used: some imported solids are not positively oriented.
Carried skid height: 66.9 mm. Pod height without lug: 297.5 mm.
Pod corner radius 356 mm versus propeller-disk inner clearance 308 mm. Planform intrusion 49 mm. The disk solids sit above the pod; this is not a solid intersection.
Outer pod 468 × 537 mm. Fore-aft alternative would be 681 × 286 mm.

## Ground exit

Exited robots overlap each other: 0.0 mm³.
robot_1_approximate overlap with open pod: 0.0 mm³.
robot_2_approximate overlap with open pod: 0.0 mm³.
Suspension-line overlap with the exited robots: 1922.7 mm³. Non-zero means the drawn lines still cross the robots. That snag is unresolved; the lines are not removed to hide it.

## Mass

Aircraft reference mass from assigned densities: 0.205 kg. The Quiver STEP assembly is not weighed from its volume. Empty 9.65 kg plus battery 7.90 kg stays the manufacturer total. The figure above is only the concept saddle, pins, and release allowance, plus any density the imported files already carry.
Pod assembly excluding the parachute allowance: 4.272 kg (solid PETG volume, not a slicer result).
Parachute allowance recovered on the packed envelope: 0.850 kg (placeholder 0.85 kg).
New adapter hardware on the aircraft (saddle, pins, release allowance): 0.205 kg.
Imported 2112 plate solid is carried with no density of its own, so this ledger does not add a second plate mass on top of the 9.65 kg empty weight. Its placed size is 66 × 50 × 16 mm.

See data/mass_budget.csv for the ledger. Solid-volume PETG is an upper bound for a printed shell, not a slicer mass.

Display scale 0.1152 brings the 1476 mm propeller span to 170 mm. A 3 mm wall becomes 0.35 mm, below the 1.2 mm FDM wall guide.
Descending pod group: 10.192 kg.
Carried payload including the adapter that stays on the aircraft and the fastener allowance: 10.447 kg.
Allowance 7.45 kg. Margin -2.997 kg.
Takeoff mass 27.997 kg against MTOW 25.00 kg.
OVERWEIGHT against the standard-battery allowance. Robot masses were not reduced.

## Rebuild

Parameter edits rebuild through `cadgen run src/exports.py`. The engine replays unchanged bodies.
