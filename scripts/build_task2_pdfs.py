"""Сборка PDF Task 2 для жюри.

    python scripts/build_task2_pdfs.py
"""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def main():
    for name in (
        "make_task2_pitch_assets.py",
        "build_jury_slides.py",
        "build_method_pdf.py",
    ):
        script = ROOT / "scripts" / name
        print(f"==> {name}")
        subprocess.check_call([sys.executable, str(script)], cwd=ROOT)
    print("Done: для_жюри/TASK2_presentation.pdf + TASK2_method_report.pdf")


if __name__ == "__main__":
    main()
