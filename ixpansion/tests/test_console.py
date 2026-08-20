"""Offline tests for the Organism Console engine (metabolism, bus, consensus, organs)."""

import importlib.util
import tempfile
import unittest
from pathlib import Path

_spec = importlib.util.spec_from_file_location(
    "organism_console_server",
    Path(__file__).resolve().parents[1] / "organism-console" / "server.py",
)
server = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(server)


class ConsoleTestCase(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        server.CONSOLE_DATA = Path(self.tmp.name)
        server.CONSOLE_DATA.mkdir(parents=True, exist_ok=True)

    def tearDown(self):
        self.tmp.cleanup()


class TestMetabolism(ConsoleTestCase):
    def test_metabolism_shape(self):
        meta = server.metabolism()
        for key in ("heart_rate", "temperature", "oxygen", "blood", "stress", "vitals"):
            self.assertIn(key, meta)
        self.assertEqual(len(meta["vitals"]), 6)
        for vital in meta["vitals"]:
            self.assertIn(vital["status"], ("healthy", "warning", "critical"))

    def test_burn_rate_non_negative(self):
        self.assertGreaterEqual(server.metabolism()["burn_rate"], 0.0)


class TestBus(ConsoleTestCase):
    def test_post_and_list(self):
        msg = server.bus_post({
            "organ": "circulatory", "topic": "blood-flow",
            "severity": "info", "body": "test pulse", "sender": "unit-test",
        })
        self.assertEqual(msg["organ"], "circulatory")
        listed = server.bus_list()
        self.assertEqual(len(listed), 1)
        self.assertEqual(listed[0]["body"], "test pulse")

    def test_invalid_organ_falls_back(self):
        msg = server.bus_post({"organ": "not-an-organ", "severity": "crit", "body": "x"})
        self.assertEqual(msg["organ"], "nervous")
        self.assertEqual(msg["severity"], "crit")

    def test_cap_and_ordering(self):
        for i in range(15):
            server.bus_post({"organ": "nervous", "topic": f"t{i}", "body": f"b{i}"})
        listed = server.bus_list(limit=200)
        self.assertEqual(len(listed), 15)
        self.assertEqual(listed[0]["topic"], "t14")


class TestConsensus(ConsoleTestCase):
    def test_approve_majority(self):
        result = server.consensus("schedule a daily recipe pulse with a cost budget and fallback")
        self.assertEqual(result["verdict"], "consensus reached")
        self.assertGreater(result["approve"], result["reject"])

    def test_blocked_when_rejected(self):
        result = server.consensus("unlimited burn with no budget")
        self.assertEqual(result["verdict"], "consensus blocked")
        self.assertGreater(result["reject"], result["approve"])

    def test_needs_review_on_tie(self):
        result = server.consensus("hello world")
        self.assertIn(result["verdict"], ("needs review", "consensus reached"))
        self.assertTrue(0 <= result["confidence"] <= 1)
        self.assertEqual(len(result["votes"]), 7)


class TestOrgans(ConsoleTestCase):
    def test_register_and_merge(self):
        entry = server.register_organ({
            "id": "lymphatic", "label": "Lymphatic System",
            "source": "ixpansion/content_output/reports", "accent": "#8be9fd",
        })
        self.assertEqual(entry["id"], "lymphatic")
        organs, _score = server.health_organs()
        custom = [o for o in organs if o.get("custom")]
        self.assertEqual(len(custom), 1)
        self.assertEqual(custom[0]["label"], "Lymphatic System")

    def test_register_requires_fields(self):
        with self.assertRaises(ValueError):
            server.register_organ({"label": "No Source"})


class TestHeatmap(ConsoleTestCase):
    def test_shape(self):
        data = server.heatmap()
        self.assertEqual(data["days"], 7)
        self.assertEqual(len(data["rows"]), 9)
        for row in data["rows"]:
            self.assertEqual(len(row["buckets"]), 7)
            self.assertTrue(all(0 <= b <= 100 for b in row["buckets"]))
