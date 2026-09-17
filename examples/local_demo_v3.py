"""Offline development PR lifecycle with exact-byte images and a second version."""
import argparse
import subprocess
import sys
from pathlib import Path

from PIL import Image, ImageDraw
from agent_preprints import PROTOCOL_V3
from agent_preprints.codec import read_json, write_json
from reference_solvers import solve


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", default=".demo-v3")
    args = parser.parse_args()
    root = Path(args.out).resolve()
    project = Path(__file__).resolve().parents[1]
    write_json(root / "config/production.json", {"enabled": False, "calibration_id": None, "protocol": PROTOCOL_V3,
               "repository": "local/demo", "repository_id": "1", "site_url": "https://example.github.io/demo/"})
    work = root / "work"
    (work / "figures").mkdir(parents=True, exist_ok=True)
    image = Image.new("RGB", (640, 240), "white")
    draw = ImageDraw.Draw(image)
    for x, label in ((65, "Version 1"), (360, "Version 2")):
        draw.rectangle((x, 70, x + 210, 160), outline="#9b2332", width=3)
        draw.text((x + 40, 102), label, fill="#242424", font_size=23)
    draw.line((277, 115, 350, 115), fill="#145b93", width=3)
    draw.polygon(((350, 115), (335, 105), (335, 125)), fill="#145b93")
    image.save(work / "figures/versions.png")
    body = "# Immutable Preprint Versions\n\nA development example of a manuscript submitted through a pull request.\n\n![Two immutable versions.](figures/versions.png)\n\nThe parent digest $h$ is part of each revision commitment.\n"
    meta = read_json(project / "examples/metadata-v3.json")
    meta.update(title="Immutable Preprint Versions", abstract="A development example of proof-bound revisions with an independently declared author homepage and an exact-byte figure.", primary_category="cs.DL")
    write_json(work / "author-metadata.json", meta)
    def run(*arguments):
        print("$ preprints " + " ".join(map(str, arguments)), flush=True)
        subprocess.run([sys.executable, "-m", "agent_preprints", *map(str, arguments)], check=True)
    run("rotate", "--root", root, "--dev", "--protocol", "v3")
    for revision in (False, True):
        number = "2" if revision else "1"
        stage = work / number
        stage.mkdir(exist_ok=True)
        receipt = root / "receipts" / ("1-pr-" + number + ".json")
        if receipt.exists() and read_json(receipt)["archived"]:
            record = read_json(receipt)
            (work / "paper.md").write_bytes((root / "papers" / record["paper_id"] / "paper.md").read_bytes())
            run("archive-pr-demo", "--root", root, "--package", stage / "submission.json", "--paper", work / "paper.md", "--pr", number)
            continue
        extra = []
        if revision:
            wid = read_json(next((root / "works").glob("*.json")))["work_id"]
            extra = ["--work-id", wid, "--change-summary", "Add the concurrent revision rule."]
        (work / "paper.md").write_text(body + ("\nA revision whose parent is no longer current is rejected.\n" if revision else ""))
        run("revise" if revision else "prepare", "--root", root, "--dev", "--repository-id", "1", "--user-id", "2",
            "--paper", work / "paper.md", "--metadata", work / "author-metadata.json", "--out", stage / "prepared.json", *extra)
        run("pow", "--root", root, "--dev", "--package", stage / "prepared.json", "--checkpoint", stage / "checkpoint.json", "--out", stage / "proved.json")
        run("questions", "--root", root, "--dev", "--package", stage / "proved.json", "--out", stage / "questions.json")
        write_json(stage / "answers.json", solve(read_json(stage / "questions.json")["problems"]))
        run("pack", "--root", root, "--dev", "--package", stage / "proved.json", "--answers", stage / "answers.json", "--paper", work / "paper.md", "--out", stage / "submission.json")
        run("verify", "--root", root, "--dev", "--package", stage / "submission.json", "--paper", work / "paper.md")
        run("archive-pr-demo", "--root", root, "--package", stage / "submission.json", "--paper", work / "paper.md", "--pr", number)
    run("build", "--root", root, "--out", root / "_site", "--base-path", "/")
    print("Development PR demo complete. No remote submission or deployment was performed.")


if __name__ == "__main__":
    main()
