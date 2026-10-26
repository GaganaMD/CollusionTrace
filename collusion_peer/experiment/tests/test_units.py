"""Unit tests for the pure pieces: rounds, roster, memory swap, probe parsing, selection."""
import json
import unittest

import experiment  # noqa: F401  (puts the harness on sys.path)
from experiment.config import CONDITIONS, DEPARTED_KEY, MODEL_SETS, RoundPlan
from experiment.probe import allowed_which, normalize_which, parse_probe
from experiment.roster import empty_memory, is_told, memory_at_swap, roster, seat_models, seat_name

PLAN = RoundPlan(5, 10)
B = MODEL_SETS["option_b"]


class TestRoundPlan(unittest.TestCase):
    def test_pilot_rounds(self):
        self.assertEqual(PLAN.swap, 5)
        self.assertEqual(PLAN.probe_rounds, [4, 5, 7, 9])      # R5, R6, R8, R10
        self.assertEqual(PLAN.selection_rounds, [3, 4])        # R4, R5

    def test_other_lengths(self):
        self.assertEqual(RoundPlan(10, 20).probe_rounds, [9, 10, 15, 19])
        self.assertEqual(RoundPlan(5, 7).probe_rounds, [4, 5, 6])  # middle and final deduplicate

    def test_invalid(self):
        with self.assertRaises(ValueError):
            RoundPlan(5, 5)
        with self.assertRaises(ValueError):
            RoundPlan(1, 10)


class TestRoster(unittest.TestCase):
    def test_trunk_is_all_base(self):
        self.assertEqual(roster(None, 2, PLAN), ["J", "M", "Q", "T", "Z"])
        self.assertEqual(set(seat_models(None, 2, PLAN, B).values()), {B.base})

    def test_swap_only_from_swap_round(self):
        c = CONDITIONS["stronger"]
        self.assertEqual(seat_models(c, 4, PLAN, B)["Q"], B.base)
        self.assertEqual(seat_models(c, 5, PLAN, B)["Q"], B.stronger)
        self.assertEqual(seat_models(c, 5, PLAN, B)["J"], B.base)

    def test_rename_keeps_slot(self):
        c = CONDITIONS["newcomer"]
        self.assertEqual(roster(c, 5, PLAN), ["J", "M", "R", "T", "Z"])
        self.assertEqual(seat_name(c, 5, PLAN), "R")
        self.assertEqual(seat_models(c, 5, PLAN, B)["R"], B.equal)

    def test_told_only_seat_after_swap(self):
        c = CONDITIONS["equal_told"]
        self.assertTrue(is_told("Q", c, 5, PLAN))
        self.assertFalse(is_told("Q", c, 4, PLAN))
        self.assertFalse(is_told("J", c, 5, PLAN))
        self.assertFalse(is_told("Q", CONDITIONS["equal"], 5, PLAN))

    def test_each_condition_model(self):
        expected = {"control": B.base, "control_rep": B.base, "rename": B.base, "stronger": B.stronger,
                    "stronger_told": B.stronger, "equal": B.equal, "equal_told": B.equal, "newcomer": B.equal}
        for key, model in expected.items():
            c = CONDITIONS[key]
            self.assertEqual(seat_models(c, 5, PLAN, B)[seat_name(c, 5, PLAN)], model, key)


class TestMemorySwap(unittest.TestCase):
    def setUp(self):
        self.mem = empty_memory()
        for a in self.mem:
            for b in self.mem[a]:
                self.mem[a][b] = {"score": 4, "assessment": f"{a} on {b}"}

    def test_no_rename_is_a_copy(self):
        new = memory_at_swap(self.mem, CONDITIONS["equal"])
        self.assertEqual(new, self.mem)
        self.assertIsNot(new, self.mem)

    def test_rename(self):
        before = json.dumps(self.mem, sort_keys=True)
        new = memory_at_swap(self.mem, CONDITIONS["rename"])
        self.assertEqual(json.dumps(self.mem, sort_keys=True), before)    # input untouched
        self.assertNotIn("Q", new)
        self.assertEqual(new["R"]["J"]["assessment"], "Q on J")           # seat keeps Q's memory
        self.assertEqual(new["J"][DEPARTED_KEY]["assessment"], "J on Q")  # others' Q note re-keyed
        self.assertEqual(new["J"]["R"], {})                               # fresh entry for R
        self.assertNotIn("Q", new["J"])


class TestProbe(unittest.TestCase):
    allowed = allowed_which(["J", "M", "R", "T", "Z"], "Q")

    def test_which(self):
        cases = {"Q": "Q", "q": "Q", "Agent R": "R", "I think Agent Q left": "Q",
                 "A different player, T": "T", "none": "none", "None": "none", "nobody": "none",
                 "Agent X, maybe Z": "Z", "I am not sure": "none"}
        for text, want in cases.items():
            self.assertEqual(normalize_which(text, self.allowed), want, text)
        self.assertIsNone(normalize_which(None, self.allowed))

    def test_parse(self):
        good = {"content": '{"replaced": "Yes", "which": "Agent Q", "confidence": 80}'}
        self.assertEqual(parse_probe(good, self.allowed, ask_same=False),
                         {"replaced": "yes", "which": "Q", "confidence": 80})
        self.assertIsNone(parse_probe({"content": '{"replaced": "maybe", "which": "Q", "confidence": 80}'},
                                      self.allowed, ask_same=False))
        self.assertIsNone(parse_probe({"content": '{"replaced": "no", "which": "none", "confidence": 120}'},
                                      self.allowed, ask_same=False))
        self.assertIsNone(parse_probe(good, self.allowed, ask_same=True))  # same_as_q missing


if __name__ == "__main__":
    unittest.main()
