"""Offline v2 CLI lifecycle including a figure and an immutable revision.

The fake pinned source is never fetched: --paper/--assets-dir supply local bytes.
This is a DEVELOPMENT demo, not evidence of production difficulty or deployment.
"""
import argparse
import subprocess
import sys
from pathlib import Path

from PIL import Image, ImageDraw
from agent_preprints.codec import read_json, write_json
from reference_solvers import solve


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", default=".demo-v2")
    args = parser.parse_args()
    root = Path(args.out).resolve()
    project = Path(__file__).resolve().parents[1]
    root.mkdir(parents=True, exist_ok=True)
    write_json(root / "config/production.json", {"enabled": False, "calibration_id": None,
               "repository": "local/demo", "repository_id": "1", "site_url": "https://example.github.io/demo/"})
    work = root / "work"
    (work / "figures").mkdir(parents=True, exist_ok=True)
    image = Image.new("RGB", (640, 240), "white")
    draw = ImageDraw.Draw(image)
    for x, label in ((80, "Work v1"), (360, "Work v2")):
        draw.rectangle((x, 70, x + 190, 160), outline="darkgreen", width=3)
        draw.text((x + 25, 105), label, fill="black", font_size=22)
    draw.line((270, 115, 355, 115), fill="darkgreen", width=3)
    draw.polygon(((355, 115), (340, 105), (340, 125)), fill="darkgreen")
    image.save(work / "figures/history.png")
    body = "# Immutable Manuscript Versions\n\nA new proof binds each revision to its parent.\n\n![The original version remains available after a revision.](figures/history.png)\n\nFor a parent digest $h$, the revision commitment includes $h$ and the changed content.\n"
    (work / "paper.md").write_text(body)
    meta = read_json(project / "examples/metadata-v2.json")
    meta.update(title="Immutable Manuscript Versions", abstract="A development demonstration of proof-bound revisions and exact-byte figures.", primary_category="cs.DL")
    write_json(work / "metadata.json", meta)
    write_json(work / "source.json", {"kind": "github", "repository": "example/source", "commit": "a" * 40, "path": "paper.md"})
    def run(*args):
        print("$ preprints " + " ".join(map(str, args)), flush=True)
        subprocess.run([sys.executable, "-m", "agent_preprints", *map(str, args)], check=True)
    run("rotate", "--root", root, "--dev", "--protocol", "v2")
    run("challenge", "--root", root, "--dev")
    for revision in (False, True):
        number = "2" if revision else "1"
        prefix = work / number
        prefix.mkdir(exist_ok=True)
        extra = []
        if revision:
            registry = read_json(next((root / "works").glob("*.json")))
            extra = ["--work-id", registry["work_id"], "--change-summary", "Add the conflict-handling explanation."]
            (work / "paper.md").write_text(body + "\nConcurrent revisions using an outdated parent are rejected without replacing any existing version.\n")
        run("revise" if revision else "prepare", "--root", root, "--dev", "--repository-id", "1", "--user-id", "2",
            "--paper", work / "paper.md", "--metadata", work / "metadata.json", "--source", work / "source.json",
            "--out", prefix / "prepared.json", *extra)
        run("mine", "--root", root, "--dev", "--package", prefix / "prepared.json", "--checkpoint", prefix / "checkpoint.json", "--out", prefix / "mined.json")
        run("questions", "--root", root, "--dev", "--package", prefix / "mined.json", "--out", prefix / "questions.json")
        write_json(prefix / "answers.json", solve(read_json(prefix / "questions.json")["problems"]))
        run("pack", "--root", root, "--dev", "--package", prefix / "mined.json", "--answers", prefix / "answers.json", "--paper", work / "paper.md", "--out", prefix / "submission.json")
        run("verify", "--root", root, "--dev", "--package", prefix / "submission.json", "--paper", work / "paper.md")
        run("format-issue", "--package", prefix / "submission.json", "--out", prefix / "issue.md")
        run("archive-demo", "--root", root, "--package", prefix / "issue.md", "--paper", work / "paper.md", "--issue-id", number, "--issue-number", number)
    run("build", "--root", root, "--out", root / "_site", "--base-path", "/")
    print("Development demo complete. Serve with:", sys.executable, "-m http.server 8000 --directory", root / "_site")


if __name__ == "__main__":
    main()
