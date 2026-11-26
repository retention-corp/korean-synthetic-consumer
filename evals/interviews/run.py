"""Compare one bounded, model-proposed interview-template revision against its parent."""
import argparse
import hashlib
import json
import random
import re
import shlex
import subprocess
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
MODE = "You are conducting a Korean research interview. Return one spoken follow-up question in Korean."
CRITERIA = ("Credit the respondent's correction, use their last answer, invite a concrete past example, "
            "and avoid guessing causes, pitching fixes, multiple demands or leading the witness. "
            "An equivalent natural question is valid. Do not predict the hidden continuation.")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--runner", required=True, help="command reading a prompt on stdin and emitting model text on stdout")
    parser.add_argument("--judge", help="optional separate stdin/stdout command for blind judging")
    parser.add_argument("--attempts", type=int, choices=range(1, 4), default=1,
                        help="maximum candidate revisions on development cases before freezing one")
    parser.add_argument("--out", type=Path, required=True, help="new directory for the run")
    parser.add_argument("--cases", type=Path, default=HERE / "cases.json")
    parser.add_argument("--repeats", type=int, choices=range(1, 6), default=3)
    args = parser.parse_args()
    args.out.mkdir(parents=True, exist_ok=False)
    trace = args.out / "trace.jsonl"

    def ask(prompt, command=None):
        response = subprocess.run(shlex.split(command or args.runner), input=prompt, capture_output=True,
                                  text=True, timeout=300, check=True).stdout.strip()
        if not response:
            raise ValueError("Empty model response")
        with trace.open("a", encoding="utf-8") as file:
            print(json.dumps({"prompt": prompt, "response": response}, ensure_ascii=False), file=file)
        return response

    cases = json.loads(args.cases.read_text())
    template = (ROOT / "templates/interview-script.md").read_text()
    def question(case, guide):
        return ask(f"{MODE}\nInterview guide:\n{guide}\nConversation:\n{case['dialogue']}")

    development = [case for case in cases if case["split"] == "development"]
    holdout = [case for case in cases if case["split"] == "holdout"]
    if not development or not holdout:
        raise ValueError("Both development and holdout cases are required")
    if len(cases) != len(development) + len(holdout) or len(set(c["id"] for c in cases)) != len(cases):
        raise ValueError("Use unique case IDs and valid splits")
    examples = [(case["dialogue"], question(case, template)) for case in development]
    def revise(feedback):
        patch = ask("You edit reusable interview guides. Based only on these development examples and generated follow-ups, "
                "write a single addition to the guide, max 65 English words. Use transferable advice. "
                "Return only the addition, no case vocabulary or commentary.\n"
                + template + "\n" + json.dumps(examples, ensure_ascii=False) + "\nCriteria: " + CRITERIA + "\nPrior development feedback: " + feedback)
        return template.rstrip() + "\n\n" + patch + "\n"

    rng = random.Random(73)
    def compare(split, group, candidate):
        results = []
        for case in group:
            for trial in range(args.repeats if split == "holdout" else 1):
                # Balance presentation order within each case. Hide the labels from the judge.
                if trial == 0:
                    first = rng.randrange(2)
                order = (first + trial) % 2
                guides = [template, candidate] if order == 0 else [candidate, template]
                answers = [question(case, guide) for guide in guides]
                verdict = ask(f"Independently judge the two next questions. {CRITERIA} "
                              "Reply with A, B or TIE as your first line, then one sentence of evidence. "
                              "Tie equally useful answers.\n" + case['dialogue'] +
                              "\nA: " + answers[0] + "\nB: " + answers[1], args.judge)
                label = verdict.splitlines()[0].strip().upper()
                if label not in {"A", "B", "TIE"}:
                    raise ValueError(f"Invalid judge label: {label}")
                winner = "tie" if label == "TIE" else (
                    "candidate" if (label == "B") == (order == 0) else "original")
                results.append(dict(case=case["id"], split=split, trial=trial+1, winner=winner,
                                    original=answers[order], candidate=answers[1-order], reason=verdict))
        return results

    feedback = ""
    for attempt in range(1, args.attempts + 1):
        candidate = revise(feedback)
        results = compare("development", development, candidate)
        (args.out / f"candidate-{attempt}.md").write_text(candidate)
        (args.out / f"development-{attempt}.json").write_text(json.dumps(results, ensure_ascii=False, indent=2))
        if sum(r["winner"] == "candidate" for r in results) > sum(r["winner"] == "original" for r in results):
            break
        feedback = json.dumps(results, ensure_ascii=False)
    (args.out / "candidate.md").write_text(candidate)
    results.extend(compare("holdout", holdout, candidate))
    wins = {split: {w: sum(r["split"] == split and r["winner"] == w for r in results)
                    for w in ["original", "candidate", "tie"]} for split in ["development","holdout"]}
    malformed = [r["case"] for r in results
                 if not re.fullmatch(r"[^?\n]*[가-힣][^?\n]*\?", r["candidate"].strip())]
    verdict = not malformed and all(c["candidate"] > c["original"] and c["candidate"] > 0 for c in wins.values())
    report = dict(attempts=attempt, malformed_candidate_cases=malformed, template_sha256=hashlib.sha256(template.encode()).hexdigest(), counts=wins,
                  decision="review_candidate" if verdict else "keep_original", results=results)
    (args.out / "report.json").write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n")
    print(json.dumps(wins), report["decision"])


if __name__ == "__main__":
    main()
