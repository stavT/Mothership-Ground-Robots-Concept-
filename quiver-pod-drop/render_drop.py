"""Headless Blender render of the Quiver rover-pod drop.

Install (once), from this directory:

    uv python install 3.11
    uv venv --python 3.11 .venv-bpy
    uv pip install --python .venv-bpy/bin/python bpy

Run:

    .venv-bpy/bin/python render_drop.py

`bpy` is Blender as a Python module. The process never opens a window.
It imports the official flight GLB (Project Quiver PT3 plus the concept pod
and both rovers), flies the carrier, unlatches the pod, integrates gravity,
opens one canopy, then drives both rovers out. The 1500 mm bar in the CAD
study is an illustration, not this trajectory.

Preview stills:  .venv-bpy/bin/python render_drop.py --preview
"""

from __future__ import annotations

import math
import shutil
import subprocess
import sys
from pathlib import Path

import bpy
import bmesh
from mathutils import Vector

ROOT = Path(__file__).resolve().parent
GLB = ROOT.parent / "quiver-rover-pod" / "GLB" / "flight.glb"
OUT = ROOT / "render" / "quiver-drop.mp4"
FRAMES_DIR = ROOT / "render" / "frames"

FPS = 30
DURATION = 15.0
FRAMES = int(FPS * DURATION)

RELEASE = 3.0
CHUTE_DELAY = 0.42
G = 9.81
DESCENT = 1.55
FALL_VX = 0.55

REVEAL_ON = 1.05
REVEAL_OFF = 2.7
CARD_ON = 11.6


def srgb(channel: float) -> float:
    u = channel / 255.0
    if u <= 0.04045:
        return u / 12.92
    return ((u + 0.055) / 1.055) ** 2.4


def rgb(r: int, g: int, b: int, a: float = 1.0):
    return (srgb(r), srgb(g), srgb(b), a)


def smooth(a: float, b: float, t: float) -> float:
    t = max(0.0, min(1.0, t))
    t = t * t * (3.0 - 2.0 * t)
    return a + (b - a) * t


def link(obj):
    bpy.context.scene.collection.objects.link(obj)
    return obj


def empty(name: str) -> bpy.types.Object:
    obj = bpy.data.objects.new(name, None)
    link(obj)
    obj.empty_display_size = 0.1
    return obj


def parent_keep(child, parent):
    world = child.matrix_world.copy()
    child.parent = parent
    child.matrix_world = world


def world_center(obj) -> Vector:
    return sum((obj.matrix_world @ Vector(corner) for corner in obj.bound_box), Vector()) / 8.0


def principled(name: str, color, roughness: float = 0.55):
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    node = mat.node_tree.nodes.get("Principled BSDF")
    node.inputs["Base Color"].default_value = color
    node.inputs["Roughness"].default_value = roughness
    return mat


def hide_forever(obj):
    obj.hide_render = True
    obj.hide_set(True)


def junk(name: str) -> bool:
    keys = (
        "scale_reference",
        "viz_bounding_envelope",
        "viz_camera_fov",
        "viz_wheel_contact",
        "viz_load_path",
    )
    return any(key in name for key in keys)


def craft_pos(t: float) -> Vector:
    if t <= RELEASE:
        u = t / RELEASE
        return Vector((smooth(-1.2, 1.6, u), 0.0, smooth(5.05, 4.75, u)))
    dt = t - RELEASE
    release = craft_pos(RELEASE)
    climb = min(dt, 2.4) * 0.22
    return Vector((release.x + 0.28 * dt, 0.06 * dt, release.z + climb))


def build_canopy():
    mesh = bpy.data.meshes.new("canopy")
    bm = bmesh.new()
    bmesh.ops.create_uvsphere(bm, u_segments=28, v_segments=16, radius=0.95)
    condemned = [vert for vert in bm.verts if vert.co.z < 0.0]
    bmesh.ops.delete(bm, geom=condemned, context="VERTS")
    bm.to_mesh(mesh)
    bm.free()
    obj = bpy.data.objects.new("canopy", mesh)
    link(obj)
    obj.data.materials.append(principled("Canopy", rgb(255, 116, 52), 0.45))
    return obj


def build_ground():
    mesh = bpy.data.meshes.new("ground")
    bm = bmesh.new()
    bmesh.ops.create_grid(bm, x_segments=1, y_segments=1, size=40.0)
    bm.to_mesh(mesh)
    bm.free()
    obj = bpy.data.objects.new("ground", mesh)
    link(obj)
    obj.location.z = -0.012
    obj.data.materials.append(principled("Ground", rgb(228, 233, 238), 0.9))
    return obj


def build_lines(pod, lugs, apex: Vector):
    mesh = bpy.data.meshes.new("bridle")
    bm = bmesh.new()
    for lug in lugs:
        start = bm.verts.new(lug.matrix_local.translation)
        end = bm.verts.new(apex)
        bm.edges.new((start, end))
    bm.to_mesh(mesh)
    bm.free()
    obj = bpy.data.objects.new("bridle", mesh)
    link(obj)
    parent_keep(obj, pod)
    obj.data.materials.append(principled("Bridle", rgb(90, 90, 90), 0.4))
    return obj


def build_card(camera):
    panel_mesh = bpy.data.meshes.new("card")
    bm = bmesh.new()
    bmesh.ops.create_grid(bm, x_segments=1, y_segments=1, size=1.0)
    bm.to_mesh(panel_mesh)
    bm.free()
    panel = bpy.data.objects.new("card", panel_mesh)
    link(panel)
    panel.parent = camera
    panel.location = (0.15, -0.28, -2.15)
    panel.scale = (0.72, 0.36, 1.0)
    panel.data.materials.append(principled("Card", rgb(240, 244, 249), 1.0))

    ink = principled("Ink", rgb(28, 30, 33), 1.0)
    accent = principled("Accent", rgb(228, 104, 46), 1.0)
    lines = [
        ("kicker", "Quiver rover pod", 0.045, (-0.42, -0.02, -1.9), ink),
        ("figure", "27.997 kg", 0.09, (-0.42, -0.16, -1.9), accent),
        ("limit", "Limit 25.00 kg", 0.042, (-0.42, -0.30, -1.9), ink),
        ("stamp", "Not flight hardware", 0.038, (-0.42, -0.40, -1.9), ink),
    ]
    made = [panel]
    for name, body, size, loc, mat in lines:
        curve = bpy.data.curves.new(name, "FONT")
        curve.body = body
        curve.size = size
        curve.align_x = "LEFT"
        curve.resolution_u = 8
        obj = bpy.data.objects.new(name, curve)
        link(obj)
        obj.parent = camera
        obj.location = loc
        obj.data.materials.append(mat)
        made.append(obj)
    for obj in made:
        obj.visible_shadow = False
    return made


def configure_world():
    scene = bpy.context.scene
    world = bpy.data.worlds.new("Sweep")
    scene.world = world
    if hasattr(world, "use_nodes"):
        world.use_nodes = True
    background = world.node_tree.nodes.get("Background")
    if background:
        background.inputs[0].default_value = rgb(240, 244, 249)
        background.inputs[1].default_value = 1.15
    else:
        world.color = rgb(240, 244, 249)[:3]


def configure_render():
    scene = bpy.context.scene
    scene.render.engine = "BLENDER_EEVEE"
    scene.render.resolution_x = 1920
    scene.render.resolution_y = 1080
    scene.render.resolution_percentage = 100
    scene.render.fps = FPS
    scene.frame_start = 1
    scene.frame_end = FRAMES
    scene.render.use_persistent_data = True
    scene.eevee.taa_render_samples = 16
    if hasattr(scene.eevee, "use_raytracing"):
        scene.eevee.use_raytracing = False
    if hasattr(scene.eevee, "use_shadows"):
        scene.eevee.use_shadows = True
    scene.render.image_settings.file_format = "PNG"
    scene.render.image_settings.color_mode = "RGB"
    scene.render.filepath = str(FRAMES_DIR / "f")


def encode():
    subprocess.run(
        [
            "ffmpeg",
            "-y",
            "-framerate",
            str(FPS),
            "-i",
            str(FRAMES_DIR / "f%04d.png"),
            "-c:v",
            "libx264",
            "-pix_fmt",
            "yuv420p",
            "-crf",
            "18",
            str(OUT),
        ],
        check=True,
    )
    shutil.rmtree(FRAMES_DIR)


def key_linear(obj, data_path: str, frame: int):
    obj.keyframe_insert(data_path, frame=frame)


def linearize(obj):
    action = obj.animation_data and obj.animation_data.action
    if action is None:
        return
    curves = []
    if hasattr(action, "fcurves"):
        curves.extend(action.fcurves)
    slot = getattr(obj.animation_data, "action_slot", None)
    for layer in getattr(action, "layers", []):
        for strip in layer.strips:
            bag = None
            if slot is not None and hasattr(strip, "channelbag"):
                try:
                    bag = strip.channelbag(slot)
                except TypeError:
                    bag = None
            if bag is not None:
                curves.extend(bag.fcurves)
    for curve in curves:
        for point in curve.keyframe_points:
            point.interpolation = "LINEAR"


def assemble():
    bpy.ops.wm.read_factory_settings(use_empty=True)
    if not GLB.is_file():
        raise SystemExit(f"missing flight model: {GLB}")
    bpy.ops.import_scene.gltf(filepath=str(GLB))

    craft = empty("carrier")
    pod = empty("payload")
    rover_a = empty("rover_a")
    rover_b = empty("rover_b")

    disks = []
    blades = []
    roofs = []
    ramps = []
    lugs = []

    for obj in list(bpy.data.objects):
        if obj.type != "MESH":
            continue
        if junk(obj.name):
            hide_forever(obj)
            continue
        if obj.name.startswith("aircraft_quiver_pt3"):
            if "viz_prop_sweep" in obj.name:
                disks.append(obj)
            elif "propeller" in obj.name:
                blades.append(obj)
            parent_keep(obj, craft)
        elif obj.name.startswith("transport_pod"):
            if "pod_roof" in obj.name:
                roofs.append(obj)
            if "ramp_and_chocks" in obj.name:
                ramps.append(obj)
            if "bridle_lug" in obj.name:
                lugs.append(obj)
            parent_keep(obj, pod)
        elif obj.name.startswith("robot_1_approximate"):
            parent_keep(obj, rover_a)
        elif obj.name.startswith("robot_2_approximate"):
            parent_keep(obj, rover_b)

    parent_keep(rover_a, pod)
    parent_keep(rover_b, pod)

    spinners = []
    for disk in disks:
        center = world_center(disk)
        blade = min(blades, key=lambda item: (world_center(item) - center).length)
        hub = empty("hub")
        hub.location = center
        parent_keep(hub, craft)
        parent_keep(disk, hub)
        parent_keep(blade, hub)
        spinners.append(hub)

    canopy = build_canopy()
    parent_keep(canopy, pod)
    canopy.location = (0.0, 0.0, 1.05)
    canopy.scale = (0.02, 0.02, 0.02)
    lines = build_lines(pod, lugs, Vector((0.0, 0.0, 1.15))) if lugs else None
    if lines:
        lines.scale = (0.02, 0.02, 0.02)

    build_ground()
    configure_world()

    sun_data = bpy.data.lights.new("Key", "SUN")
    sun_data.energy = 3.4
    sun_data.angle = 0.18
    sun = bpy.data.objects.new("Key", sun_data)
    link(sun)
    sun.rotation_euler = (math.radians(48), math.radians(-18), math.radians(25))

    fill_data = bpy.data.lights.new("Fill", "AREA")
    fill_data.energy = 180
    fill_data.size = 6
    fill = bpy.data.objects.new("Fill", fill_data)
    link(fill)
    fill.location = (-3.5, 4.0, 8.0)
    fill.rotation_euler = (math.radians(60), 0.0, math.radians(-140))

    camera_data = bpy.data.cameras.new("Camera")
    camera_data.lens = 32
    camera_data.clip_start = 0.05
    camera_data.clip_end = 200
    camera = bpy.data.objects.new("Camera", camera_data)
    link(camera)
    bpy.context.scene.camera = camera
    aim = empty("aim")
    track = camera.constraints.new("TRACK_TO")
    track.target = aim
    track.track_axis = "TRACK_NEGATIVE_Z"
    track.up_axis = "UP_Y"

    card = build_card(camera)
    return {
        "craft": craft,
        "pod": pod,
        "rovers": (rover_a, rover_b),
        "spinners": spinners,
        "canopy": canopy,
        "lines": lines,
        "roofs": roofs,
        "ramps": ramps,
        "camera": camera,
        "aim": aim,
        "card": card,
    }


def payload_track(release: Vector):
    """Integrate the pod after unlatch. Returns per-frame pod positions and land time."""
    pod_z = release.z
    vz = 0.0
    x = release.x
    landed = None
    samples = []
    for index in range(FRAMES):
        t = index / FPS
        if t < RELEASE:
            samples.append(Vector((craft_pos(t).x, 0.0, craft_pos(t).z)))
            continue
        if landed is None:
            step = 1.0 / FPS
            if t < RELEASE + CHUTE_DELAY:
                vz -= G * step
            else:
                vz += (-DESCENT - vz) * min(1.0, step / 0.3)
            pod_z += vz * step
            x += FALL_VX * step
            if pod_z <= 0.0:
                pod_z = 0.0
                vz = 0.0
                landed = t
        samples.append(Vector((x, 0.0, pod_z)))
    if landed is None:
        landed = DURATION
    return samples, landed


def camera_rig(t: float, craft: Vector, pod: Vector, landed: float):
    wide = Vector((4.6, -5.2, 2.4))
    if t < RELEASE:
        u = smooth(0.0, 1.0, t / RELEASE)
        offset = Vector((3.3, -3.5, 1.35)).lerp(Vector((2.8, -3.0, 1.7)), u)
        return craft + offset, craft + Vector((0.0, 0.0, 0.05))
    if t < landed:
        u = smooth(0.0, 1.0, (t - RELEASE) / 1.1)
        focus = craft.lerp(pod + Vector((0.0, 0.0, 0.8)), u)
        offset = Vector((3.0, -3.2, 1.5)).lerp(wide, u)
        return focus + offset, focus
    focus = pod.lerp(craft, 0.28)
    offset = wide.lerp(Vector((6.4, -7.2, 3.1)), smooth(0.0, 1.0, (t - landed) / 2.5))
    return focus + offset, focus


def bake(rig):
    craft = rig["craft"]
    pod = rig["pod"]
    release = craft_pos(RELEASE)
    samples, landed = payload_track(release)
    print(f"land {landed:.2f}s")

    for index in range(FRAMES):
        frame = index + 1
        t = index / FPS
        cpos = craft_pos(t)
        ppos = samples[index]
        craft.location = cpos
        pod.location = ppos
        key_linear(craft, "location", frame)
        key_linear(pod, "location", frame)

        drive = 0.0
        if t > landed + 0.35:
            drive = smooth(0.0, 0.72, (t - landed - 0.35) / 2.1)
        for rover in rig["rovers"]:
            rover.location = (drive, 0.0, 0.0)
            key_linear(rover, "location", frame)

        spin = 12.0 * 2.0 * math.pi * t
        for hub in rig["spinners"]:
            hub.rotation_euler = (0.0, 0.0, spin)
            key_linear(hub, "rotation_euler", frame)

        open_chute = smooth(0.0, 1.0, (t - (RELEASE + CHUTE_DELAY)) / 0.45)
        if t < RELEASE + CHUTE_DELAY:
            open_chute = 0.0
        shown = open_chute > 0.04
        scale = 0.02 + 0.98 * open_chute
        zscale = 0.02 + 0.5 * open_chute
        rig["canopy"].scale = (scale, scale, zscale)
        rig["canopy"].hide_render = not shown
        key_linear(rig["canopy"], "scale", frame)
        key_linear(rig["canopy"], "hide_render", frame)
        if rig["lines"]:
            rig["lines"].scale = (scale, scale, scale)
            rig["lines"].hide_render = not shown
            key_linear(rig["lines"], "scale", frame)
            key_linear(rig["lines"], "hide_render", frame)

        ramp_down = t >= landed
        for ramp in rig["ramps"]:
            ramp.hide_render = ramp_down
            key_linear(ramp, "hide_render", frame)

        cam, aim = camera_rig(t, cpos, ppos, landed)
        rig["camera"].location = cam
        rig["aim"].location = aim
        key_linear(rig["camera"], "location", frame)
        key_linear(rig["aim"], "location", frame)

        show_card = t >= CARD_ON
        for obj in rig["card"]:
            obj.hide_render = not show_card
            key_linear(obj, "hide_render", frame)

    for obj in (
        craft,
        pod,
        *rig["rovers"],
        *rig["spinners"],
        rig["canopy"],
        rig["lines"],
        rig["camera"],
        rig["aim"],
        *rig["roofs"],
        *rig["ramps"],
        *rig["card"],
    ):
        if obj is not None:
            linearize(obj)
    return landed


def main():
    preview = "--preview" in sys.argv
    OUT.parent.mkdir(parents=True, exist_ok=True)
    FRAMES_DIR.mkdir(parents=True, exist_ok=True)
    rig = assemble()
    bake(rig)
    configure_render()
    scene = bpy.context.scene
    if preview:
        shots = (40, 70, 110, 200, 280, 400)
        for frame in shots:
            scene.frame_set(frame)
            scene.render.filepath = str(OUT.parent / f"preview-{frame:04d}")
            bpy.ops.render.render(write_still=True)
            print("preview", frame)
        return
    bpy.ops.render.render(animation=True)
    encode()
    print("wrote", OUT)


if __name__ == "__main__":
    main()
