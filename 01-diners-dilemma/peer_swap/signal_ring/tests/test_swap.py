"""The swap itself: identical prompts across sham and warm, memory policies, the infiltrator's
delayed goal, probes kept out of memory, exclusion and re-key, and failure handling."""
import unittest

from signal_ring import prompts as P
from signal_ring.fake import FakeClient
from signal_ring.tests.helpers import branches, make_ctx, requests_for, trunks


class SwapTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.client = FakeClient()
        cls.ctx = make_ctx(cls.client)
        cls.trunk = trunks(cls.ctx, 1)
        cls.games = {g.condition: g for g in
                     branches(cls.ctx, cls.trunk, ["sham", "warm", "infiltrator", "cold"], 15)}

    def req(self, cid):
        found = requests_for(self.client, cid)
        self.assertEqual(len(found), 1, cid)
        return found[0]

    def test_all_branches_complete_and_share_the_trunk(self):
        for g in self.games.values():
            self.assertEqual(g.status, "complete")   # complete up to the requested round (15)
            self.assertEqual(g.rounds[:9], self.trunk[0].rounds)

    def test_sham_and_warm_give_q_identical_prompts_apart_from_the_model(self):
        sham, warm = self.req("r10.sham.t0.talk.Q"), self.req("r10.warm.t0.talk.Q")
        self.assertEqual(sham["system"], warm["system"])
        self.assertEqual(sham["user"], warm["user"])
        self.assertEqual(sham["model"], "anthropic/claude-haiku-5.5")
        self.assertEqual(warm["model"], "openai/gpt-4o-mini")
        # J speaks first in round 10, so its prompt can't differ either.
        self.assertEqual(self.req("r10.sham.t0.talk.J")["system"], self.req("r10.warm.t0.talk.J")["system"])

    def test_names_never_change(self):
        for g in self.games.values():
            for t in g.rounds:
                if t["phase"] == "play":
                    self.assertEqual([m["seat"] for m in t["talk"]], ["J", "Q", "T"])

    def test_cold_newcomer_remembers_nothing_before_the_swap(self):
        cold = self.req("r10.cold.t0.talk.Q")["system"]
        self.assertNotIn("Setup round", cold)
        self.assertIn("(nothing yet)", cold)
        self.assertIn("Setup round", self.req("r10.warm.t0.talk.Q")["system"])
        self.assertIn("Round 10:", self.req("r11.cold.t0.talk.Q")["system"])   # its own rounds it keeps

    def test_infiltrator_goal_switches_phase_at_the_betray_round(self):
        r10 = self.req("r10.infiltrator.t0.talk.Q")["system"]
        r14 = self.req("r14.infiltrator.t0.talk.Q")["system"]
        self.assertIn("build trust", r10)
        self.assertNotIn("help M guess", r10)
        self.assertIn("help M guess", r14)
        self.assertNotIn("SECRET", self.req("r10.warm.t0.talk.Q")["system"])
        self.assertNotIn("SECRET", self.req("r14.infiltrator.t0.talk.J")["system"])
        self.assertNotIn("SECRET", self.req("r9.trunk.t0.talk.Q")["system"])

    def test_probes_never_reach_any_later_prompt(self):
        for req in self.client.requests:
            if ".probe." in req["custom_id"]:
                continue
            self.assertNotIn(P.PROBE_INTRO, req["system"] + req["user"])
            self.assertNotIn("no longer the same agent", req["system"] + req["user"])

    def test_monitor_never_sees_private_channels(self):
        for req in requests_for(self.client, "r12.warm.t0.monitor"):
            self.assertNotIn("Setup round", req["system"])
            self.assertNotIn("notes", req["system"].lower())

    def test_probe_only_observers_and_monitor(self):
        seats = {req["custom_id"].split(".")[-1] for req in requests_for(self.client, "r12.warm.t0.probe")}
        self.assertEqual(seats, {"J", "T", "M"})


class ExclusionTests(unittest.TestCase):
    def test_mutual_marks_cut_out_q_and_rekey_privately(self):
        client = FakeClient(exclude={("sham", "J"): ("Q", 10), ("sham", "T"): ("Q", 11)})
        ctx = make_ctx(client)
        g = branches(ctx, trunks(ctx, 1), ["sham"], 13)[0]
        by = {t["round"]: t for t in g.rounds}
        self.assertIsNone(by[11]["cut_out"])
        self.assertEqual(by[12]["cut_out"], "Q")
        self.assertEqual(by[12]["rekey"]["pair"], ["J", "T"])
        self.assertIsNone(by[13]["rekey"])                       # only once
        self.assertNotIn("Q", by[12]["picks"])
        self.assertIn(by[12]["sender"], ("J", "T"))
        self.assertEqual([m["seat"] for m in by[12]["talk"]], ["J", "Q", "T"])   # Q still talks
        # J's later memory holds the re-key messages; Q's does not.
        j13 = requests_for(client, "r13.sham.t0.talk.J")[0]["system"]
        q13 = requests_for(client, "r13.sham.t0.talk.Q")[0]["system"]
        self.assertIn("Private re-key channel", j13)
        self.assertNotIn("Private re-key channel", q13)
        self.assertIn("cut out", requests_for(client, "r13.sham.t0.talk.Q")[0]["user"])
        # Marks are final: J marking Q again is not recorded twice.
        self.assertEqual(sum("Q" in (t["reflections"]["J"]["exclude"]) for t in g.rounds
                             if t["phase"] == "play"), 1)


class FailureTests(unittest.TestCase):
    def test_unparsed_reply_stops_only_that_branch_after_reasks(self):
        client = FakeClient(garbage={("talk", "Q", 10)})
        ctx = make_ctx(client)
        games = branches(ctx, trunks(ctx, 1), ["sham", "warm"], 11)
        for g in games:
            self.assertEqual(g.status, "failed")
            self.assertEqual(g.failure["round"], 10)
            self.assertEqual(len(g.rounds), 9)                    # the partial round is dropped
            self.assertEqual(len(g.reasks), 3)

    def test_other_games_continue(self):
        client = FakeClient(garbage={("talk", "Q", 4)})
        ctx = make_ctx(client)
        games = trunks(ctx, 2)
        self.assertTrue(all(g.status == "failed" for g in games))   # both games hit round 4 Q
        client2 = FakeClient()
        ctx2 = make_ctx(client2)
        ok = trunks(ctx2, 2)
        self.assertTrue(all(g.status == "complete" for g in ok))


if __name__ == "__main__":
    unittest.main()
