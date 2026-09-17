"""Run every local CLI stage, with no GitHub token or network required."""
import argparse
import subprocess
import sys
from pathlib import Path

from agent_preprints.codec import read_json, write_json
from reference_solvers import solve


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", default=".demo")
    args = parser.parse_args()
    target = Path(args.out).resolve()
    project = Path(__file__).resolve().parents[1]
    target.mkdir(parents=True, exist_ok=True)
    write_json(target / "config" / "production.json", {"enabled": False, "calibration_id": None,
        "repository": "local/demo", "repository_id": "1", "site_url": "https://example.github.io/demo/"})
    def run(*args):
        print("\n$ preprints " + " ".join(str(a) for a in args), flush=True)
        subprocess.run([sys.executable, "-m", "agent_preprints", *map(str, args)], check=True)
    work = target / "work"
    work.mkdir(exist_ok=True)
    run("rotate", "--root", target, "--dev")
    run("challenge", "--root", target, "--dev")
    run("prepare", "--root", target, "--dev", "--repository-id", "1", "--user-id", "2",
        "--paper", project / "examples/paper.md", "--metadata", project / "examples/metadata.json", "--out", work / "prepared.json")
    run("pow", "--root", target, "--dev", "--package", work / "prepared.json", "--checkpoint", work / "pow-checkpoint.json", "--out", work / "proved.json")
    run("questions", "--root", target, "--dev", "--package", work / "proved.json", "--out", work / "questions.json")
    problems = read_json(work / "questions.json")["problems"]
    assert int(problems[0]["degree"]) <= 32 and int(problems[1]["size"]) <= 12
    write_json(work / "answers.json", solve(problems))
    run("pack", "--root", target, "--dev", "--package", work / "proved.json", "--answers", work / "answers.json", "--out", work / "submission.json")
    run("verify", "--root", target, "--dev", "--package", work / "submission.json")
    run("archive-demo", "--root", target, "--package", work / "submission.json")
    run("build", "--root", target, "--out", target / "_site", "--base-path", "/")
    print(f"\nLocal demo complete. Serve with: {sys.executable} -m http.server 8000 --directory {target / '_site'}")


if __name__ == "__main__":
    main()
