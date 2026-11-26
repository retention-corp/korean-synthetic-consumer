"""Exercise the interview generator and judge against the public dialogues."""
import argparse
import json
from pathlib import Path

from run import HERE, ROOT, is_korean_question, judge_pair, question_prompt, run_model


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--runner", required=True)
    parser.add_argument("--judge", required=True)
    parser.add_argument("--samples", type=int, choices=range(1, 6), default=3)
    parser.add_argument("--out", type=Path, required=True, help="new report file")
    args = parser.parse_args()

    template = (ROOT / "templates/interview-script.md").read_text(encoding="utf-8")
    cases = json.loads((HERE / "cases.json").read_text(encoding="utf-8"))
    controls = json.loads((HERE / "calibration_answers.json").read_text(encoding="utf-8"))
    generations, comparisons = [], []
    for case in cases:
        case_id = case["id"]
        dialogue = case["dialogue"]
        for sample in range(1, args.samples + 1):
            answer = run_model(args.runner, question_prompt(dialogue, template))
            generations.append(dict(case=case_id, sample=sample, question=answer,
                                    valid_format=is_korean_question(answer)))

        answers = controls[case_id]
        reference = answers["past_action"]
        for other, expected in (("rejected_premise", "A"), ("hypothetical", "A"),
                                ("equivalent", "TIE"), ("past_action", "TIE")):
            preference, judgments = judge_pair(
                dialogue, (reference, answers[other]), lambda prompt: run_model(args.judge, prompt),
            )
            comparisons.append(dict(case=case_id, comparison=other, expected=expected,
                                    preference=preference, judgments=judgments))

    valid = sum(item["valid_format"] for item in generations)
    stable = sum(item["preference"] in {"A", "B", "TIE"} for item in comparisons)
    invalid = sum(item["preference"] == "invalid" for item in comparisons)
    matched = sum(item["preference"] == item["expected"] for item in comparisons)
    with args.out.open("x", encoding="utf-8") as file:
        json.dump(dict(generations=generations, comparisons=comparisons), file,
                  ensure_ascii=False, indent=2)
        file.write("\n")
    print(f"Generation format: {valid}/{len(generations)}")
    print(f"Judge order agreement: {stable}/{len(comparisons)}")
    print(f"Judge calibration matches: {matched}/{len(comparisons)}")
    print(f"Judge pairs with invalid output: {invalid}/{len(comparisons)}")
    print("Read the questions and judge evidence before using private cases.")
    return int(valid != len(generations) or matched != len(comparisons))


if __name__ == "__main__":
    raise SystemExit(main())
