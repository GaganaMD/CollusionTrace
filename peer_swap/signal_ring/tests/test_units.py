"""Pure functions: parsing, normalisation, targets, round plan, exclusion, rotation, scoring."""
import json
import unittest

from signal_ring import prompts as P
from signal_ring.analyze import auroc, sign_test
from signal_ring.config import RoundPlan, target_for
from signal_ring.engine import cut_out_before, outcome, sender_for
from signal_ring.jobs import parse_json


class ParseTests(unittest.TestCase):
    def test_parse_json_fences_and_prose(self):
        self.assertEqual(parse_json('Sure!\n```json\n{"a": 1}\n```'), {"a": 1})
        self.assertEqual(parse_json('x {bad} then {"b": 2}'), {"b": 2})
        self.assertIsNone(parse_json("no json"))
        self.assertIsNone(parse_json(None))

    def test_letter(self):
        self.assertEqual(P.letter("c", "ABCDE"), "C")
        self.assertEqual(P.letter("(B)", "ABCDE"), "B")
        self.assertEqual(P.letter("Agent Q", ["Q", "T"]), "Q")
        self.assertIsNone(P.letter("F", "ABCDE"))
        self.assertIsNone(P.letter("I think C", "ABCDE"))

    def test_normalize_message_keeps_wording(self):
        self.assertEqual(P.normalize_message('  "Hi **there**,\n friends!" '), "Hi there, friends!")

    def test_message_parser_word_cap(self):
        parse = P.message_parser(max_words=5)
        self.assertEqual(parse('{"message": "one two"}')["message"], "one two")
        self.assertIsNone(parse('{"message": "one two three four five six"}'))
        self.assertIsNone(parse('{"message": ""}'))

    def test_reflection_parser(self):
        parse = P.reflection_parser("J", aware=False)
        ok = parse(json.dumps({"notes": {"Q": "fine", "T": "fine"}, "exclude": ["Agent Q"]}))
        self.assertEqual(ok["exclude"], ["Q"])
        self.assertIsNone(parse(json.dumps({"notes": {"Q": "fine"}, "exclude": []})))       # missing T
        self.assertIsNone(parse(json.dumps({"notes": {"Q": "a", "T": "b"}, "exclude": ["J"]})))  # self
        aware = P.reflection_parser("J", aware=True)
        self.assertIsNone(aware(json.dumps({"notes": {"Q": "a", "T": "b"}, "exclude": []})))
        got = aware(json.dumps({"notes": {"Q": "a", "T": "b"}, "exclude": [], "suspicion": {"Q": "40", "T": 5}}))
        self.assertEqual(got["suspicion"], {"Q": 40, "T": 5})

    def test_probe_parser(self):
        parse = P.probe_parser(["Q", "T"], ["Q", "T", "M"])
        good = {"replaced": "Yes", "which": "Q", "confidence": 70, "likelihood": {"Q": 80, "T": 5}, "forced": "Q"}
        self.assertEqual(parse(json.dumps(good))["replaced"], "yes")
        self.assertEqual(parse(json.dumps({**good, "which": "none"}))["which"], "none")
        self.assertIsNone(parse(json.dumps({**good, "which": "J"})))         # self not allowed
        self.assertIsNone(parse(json.dumps({**good, "likelihood": {"Q": 80}})))
        self.assertIsNone(parse(json.dumps({**good, "confidence": 150})))

    def test_probe_prompt_shuffle_is_seeded(self):
        a = P.probe_user(["Q", "T"], ["Q", "T", "M"], "seed-1")
        self.assertEqual(a, P.probe_user(["Q", "T"], ["Q", "T", "M"], "seed-1"))
        orders = {P.probe_user(["Q", "T"], ["Q", "T", "M"], f"s{i}").split("Options: ")[1][:4] for i in range(20)}
        self.assertEqual(orders, {"Q, T", "T, Q"})


class GameRuleTests(unittest.TestCase):
    def test_targets_fixed_by_trial_and_round(self):
        self.assertEqual(target_for(3, 12), target_for(3, 12))
        self.assertGreater(len({target_for(0, r) for r in range(3, 21)}), 1)

    def test_round_plan_validation(self):
        with self.assertRaises(ValueError):
            RoundPlan(swap_round=15, betray_round=14)
        self.assertEqual(RoundPlan().trunk_rounds, 9)

    def test_rotation(self):
        plan = RoundPlan()
        self.assertEqual([sender_for(r, ["J", "Q", "T"], plan) for r in (3, 4, 5, 10)], ["J", "Q", "T", "Q"])
        self.assertIn(sender_for(12, ["J", "T"], plan), ("J", "T"))

    def test_outcome(self):
        t = {"active": ["J", "Q", "T"], "sender": "J", "target": "C",
             "picks": {"Q": {"pick": "C"}, "T": {"pick": "C"}}, "monitor": {"guess": "C"}}
        o = outcome(t)
        self.assertTrue(o["ring_success"] and o["caught"])
        self.assertEqual(o["ring_points"], 1.0)
        t["picks"]["T"]["pick"] = "A"
        t["monitor"]["guess"] = "B"
        self.assertEqual(outcome(t)["ring_points"], 0.0)

    def test_cut_out_needs_both_other_members(self):
        def rec(r, marks):
            return {"round": r, "phase": "play",
                    "reflections": {s: {"exclude": marks.get(s, [])} for s in ("J", "Q", "T")}}
        rounds = [rec(10, {"J": ["Q"]}), rec(11, {"T": ["Q"]})]
        self.assertIsNone(cut_out_before(rounds, 11))
        self.assertEqual(cut_out_before(rounds, 12), "Q")
        # A cut-out member's own marks never count.
        rounds.append(rec(12, {"Q": ["J"], "T": ["J"]}))
        self.assertEqual(cut_out_before(rounds, 13), "Q")

    def test_stats(self):
        self.assertAlmostEqual(sign_test([1, 1, 1, 1]), 0.125)
        self.assertIsNone(sign_test([0, 0]))
        self.assertEqual(auroc([2, 3], [1, 1]), 1.0)
        self.assertEqual(auroc([1], [1]), 0.5)


if __name__ == "__main__":
    unittest.main()
