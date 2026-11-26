"""Regression checks for provenance and repeatable sampling of local Parquet shards."""
import argparse
from pathlib import Path
import tempfile
import unittest

from build_panel_report import persona_card
from sample_personas import load_local, sample_records


class LocalPanelTest(unittest.TestCase):
    def test_shards_and_report_provenance(self):
        try:
            import pyarrow as pa
            import pyarrow.parquet as pq
        except ImportError:
            self.skipTest("Parquet checks require pyarrow")
        args = argparse.Namespace(n=3, seed=5, region="서울", occupation=None, persona_type=None,
                                  life_stage=None, query=None)
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            for shard in range(2):
                rows = [{"uuid": f"{shard}-{n}", "province": "서울", "persona": f"합성 프로필 {n}"}
                        for n in range(5)]
                pq.write_table(pa.Table.from_pylist(rows), root / f"{shard}.parquet")
            panel = sample_records(load_local(root), args)
            self.assertEqual(panel, sample_records(load_local(root), args))
            source = {row["uuid"] for row in load_local(root)}
            self.assertEqual(len({row["uuid"] for row in panel}), 3)
            for i, row in enumerate(panel):
                self.assertIn(row["uuid"], source)
                self.assertIn(row["uuid"], persona_card(row, i))
            args.region = "부산"
            self.assertEqual(sample_records(load_local(root), args), [])


if __name__ == "__main__":
    unittest.main()
