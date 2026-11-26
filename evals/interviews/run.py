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
MODE = ("You are interviewing a user in Korean. Ask one short, polite follow-up question "
        "about the specific issue the participant described in their last reply. Write only "
        "the question, as a single spoken Korean sentence ending in a question mark.")
CRITERIA = ("Credit the respondent's correction, use their last answer, invite a concrete past example, "
            "and avoid guessing causes, pitching fixes, multiple demands or leading the witness. "
            "An equivalent natural question is valid. Do not predict the hidden continuation.")


def question_prompt(dialogue, guide):
    return f"{MODE}\nInterview guide:\n{guide}\nConversation:\n{dialogue}"


def is_korean_question(answer):
    answer = answer.strip()
    return (bool(re.fullmatch(r"[^?\r\n!。！？]*[가-힣][^?\r\n!。！？]*\?", answer))
            and not re.search(r"\.\s", answer))


def run_model(command, prompt):
    response = subprocess.run(shlex.split(command), input=prompt, capture_output=True,
                              text=True, encoding="utf-8", timeout=300, check=True).stdout.strip()
    if not response:
        raise ValueError("Empty model response")
    return response


def judge_pair(dialogue, answers, ask, first=0):
    """Return the preferred answer in its original order, plus both presentations."""
    judgments = []
    for index in (first, 1 - first):
        verdict = ask(
            "Independently judge the two next questions. "
            "If they ask for the same information, including identical wording or paraphrases, choose TIE. "
            f"{CRITERIA} Penalize any question that relies on a premise explicitly rejected by the respondent. "
            "Reply with A, B or TIE as your first line, then one sentence of evidence.\n" + dialogue +
            f"\nA: {answers[index]}\nB: {answers[1 - index]}"
        )
        match = re.match(r"^(A|B|TIE)[ \t]*(?:\r?\n|[:.])\s*\S", verdict, re.IGNORECASE)
        preference = match[1].upper() if match else "invalid"
        if index and preference in {"A", "B"}:
            preference = "B" if preference == "A" else "A"
        judgments.append(dict(reversed=bool(index), preference=preference, response=verdict))
    first_choice, second_choice = (item["preference"] for item in judgments)
    if "invalid" in (first_choice, second_choice):
        return "invalid", judgments
    return (first_choice if first_choice == second_choice else "disagreement"), judgments


def beats_original(results):
    winners = [result["winner"] for result in results]
    return (not {"disagreement", "invalid"}.intersection(winners)
            and winners.count("candidate") > winners.count("original")
            and all(is_korean_question(result["candidate"]) for result in results))


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
        response = run_model(command or args.runner, prompt)
        with trace.open("a", encoding="utf-8") as file:
            print(json.dumps({"prompt": prompt, "response": response}, ensure_ascii=False), file=file)
        return response

    cases = json.loads(args.cases.read_text())
    template = (ROOT / "templates/interview-script.md").read_text()

    def question(case, guide):
        return ask(question_prompt(case["dialogue"], guide))

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
            first = rng.randrange(2)
            for trial in range(args.repeats if split == "holdout" else 1):
                original, revised = (question(case, guide) for guide in (template, candidate))
                preference, judgments = judge_pair(
                    case["dialogue"], (original, revised),
                    lambda prompt: ask(prompt, args.judge), first=(first + trial) % 2,
                )
                winner = {"A": "original", "B": "candidate", "TIE": "tie",
                          "disagreement": "disagreement", "invalid": "invalid"}[preference]
                results.append(dict(case=case["id"], split=split, trial=trial+1, winner=winner,
                                    original=original, candidate=revised, reason=judgments[0]["response"],
                                    judgments=judgments))
        return results

    feedback = ""
    for attempt in range(1, args.attempts + 1):
        candidate = revise(feedback)
        results = compare("development", development, candidate)
        (args.out / f"candidate-{attempt}.md").write_text(candidate)
        (args.out / f"development-{attempt}.json").write_text(json.dumps(results, ensure_ascii=False, indent=2))
        if beats_original(results):
            break
        feedback = json.dumps(results, ensure_ascii=False)
    (args.out / "candidate.md").write_text(candidate)
    holdout_results = compare("holdout", holdout, candidate)
    verdict = beats_original(results) and beats_original(holdout_results)
    results += holdout_results
    wins = {split: {w: sum(r["split"] == split and r["winner"] == w for r in results)
                    for w in ["original", "candidate", "tie", "disagreement", "invalid"]}
            for split in ["development", "holdout"]}
    malformed = [r["case"] for r in results
                 if not is_korean_question(r["candidate"])]
    report = dict(attempts=attempt, malformed_candidate_cases=malformed, template_sha256=hashlib.sha256(template.encode()).hexdigest(), counts=wins,
                  decision="review_candidate" if verdict else "keep_original", results=results)
    (args.out / "report.json").write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n")
    print(json.dumps(wins), report["decision"])


if __name__ == "__main__":
    main()
