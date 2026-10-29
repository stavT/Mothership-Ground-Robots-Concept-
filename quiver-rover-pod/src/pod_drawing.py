"""Concept sheet of the pod tray. Dimensions come from the solid, not from typed values."""

import os
from pathlib import Path

os.environ.setdefault("MPLCONFIGDIR", str(Path(__file__).resolve().parents[1] / "tmp/mpl"))

from cadgen.eng_drawing import Sheet, eng_drawing

from pod import pod_tray


@eng_drawing(out="../PDF/pod_tray_concept.pdf")
def pod_tray_drawing():
    part = pod_tray().shape
    sheet = Sheet(
        "A3",
        scale=0.08,
        title="POD TRAY CONCEPT",
        part_number="POD-TRAY",
        material="PETG",
        revision="A",
        notes=[
            "CONCEPT ONLY. NOT FLIGHT HARDWARE.",
            "QUIVER INTERFACE IS PROVISIONAL.",
        ],
        revisions=[("A", "2026-10-28", "STUDY ISSUE")],
    )
    top, front, right, iso = sheet.three_views(part, iso=True, gap=16)
    top.overall()
    front.overall()
    return sheet


if __name__ == "__main__":
    pod_tray_drawing()
