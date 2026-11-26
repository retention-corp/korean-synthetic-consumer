import unittest

from run import beats_original, is_korean_question, judge_pair


class QuestionFormatTest(unittest.TestCase):
    def test_only_one_question(self):
        self.assertTrue(is_korean_question("지난번에 0.5kg을 넣고 나서 어떻게 하셨어요?"))
        self.assertFalse(is_korean_question("타이밍이 어려웠군요. 지난번에는 어떻게 하셨어요?"))


class JudgePairTest(unittest.TestCase):
    def test_prefers_the_same_answer_in_both_positions(self):
        calls = []

        def ask(prompt):
            calls.append(prompt)
            label = "A" if prompt.endswith("A: first?\nB: second?") else "B"
            return label + "\nThe answer asks about past behavior."

        preference, judgments = judge_pair("dialogue", ("first?", "second?"), ask, first=1)

        self.assertEqual(preference, "A")
        self.assertTrue(calls[0].endswith("A: second?\nB: first?"))
        self.assertTrue(calls[1].endswith("A: first?\nB: second?"))
        self.assertEqual([judgment["reversed"] for judgment in judgments], [True, False])

    def test_disagreement_blocks_a_candidate_even_with_more_wins(self):
        preference, _ = judge_pair("dialogue", ("first?", "second?"), lambda _: "A\nEvidence.")
        self.assertEqual(preference, "disagreement")
        results = [dict(winner="candidate", candidate="지난번에 어떻게 하셨어요?")] * 2
        self.assertTrue(beats_original(results))
        self.assertFalse(beats_original(results + [dict(winner=preference, candidate="어떻게 하셨어요?")]))

    def test_missing_evidence_fails(self):
        preference, judgments = judge_pair("dialogue", ("first?", "second?"), lambda _: "A")
        self.assertEqual(preference, "invalid")
        self.assertEqual([judgment["response"] for judgment in judgments], ["A", "A"])

    def test_evidence_after_punctuation(self):
        for separator in (":", "."):
            with self.subTest(separator=separator):
                preference, _ = judge_pair("dialogue", ("same?", "same?"),
                                           lambda _: f"TIE{separator} Same question.")
                self.assertEqual(preference, "TIE")


if __name__ == "__main__":
    unittest.main()
