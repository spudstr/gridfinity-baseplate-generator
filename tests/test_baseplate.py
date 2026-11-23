"""Tests for make_baseplate.py. Standard library only.

Run:  python -m unittest discover -s tests -v
"""
import os
import struct
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SCRIPT = ROOT / "make_baseplate.py"
sys.path.insert(0, str(ROOT))

import make_baseplate as mb  # noqa: E402


class GeometryTests(unittest.TestCase):
    def assert_plate(self, cols, rows, pitch=42.0):
        tris = mb.build(cols, rows, pitch)
        bad, vol, size = mb.check(tris)
        self.assertEqual(bad, 0, "mesh must be watertight")
        self.assertGreater(vol, 0, "normals must face outward")
        self.assertAlmostEqual(size[0], cols * pitch, places=3)
        self.assertAlmostEqual(size[1], rows * pitch, places=3)
        self.assertAlmostEqual(size[2], 4.65, places=3)
        return vol

    def test_standard_sizes_are_watertight_and_exact(self):
        for cols, rows in [(1, 1), (2, 3), (3, 3), (4, 4), (2, 5), (6, 6)]:
            with self.subTest(cols=cols, rows=rows):
                self.assert_plate(cols, rows)

    def test_each_middle_row_adds_the_same_volume(self):
        # Rows without rounded plate corners are identical, so adding one
        # more middle row must always add exactly the same plastic.
        v2, v3, v4 = (self.assert_plate(3, r) for r in (2, 3, 4))
        self.assertAlmostEqual(v4 - v3, v3 - v2, places=3)
        self.assertGreater(v3 - v2, 0)

    def test_custom_cell_size(self):
        self.assert_plate(3, 3, pitch=50.8)
        self.assert_plate(2, 2, pitch=30.0)

    def test_rejects_too_small_cell(self):
        with self.assertRaises(ValueError):
            mb.build(1, 1, 5.0)


class CommandLineTests(unittest.TestCase):
    def run_script(self, *args):
        return subprocess.run([sys.executable, str(SCRIPT), *args],
                              capture_output=True, text=True, cwd=ROOT)

    def stl_triangles(self, path):
        data = Path(path).read_bytes()
        n = struct.unpack("<I", data[80:84])[0]
        self.assertEqual(len(data), 84 + 50 * n, "binary STL length must match header")
        return n

    def test_writes_requested_file(self):
        with tempfile.TemporaryDirectory() as tmp:
            out = os.path.join(tmp, "plate.stl")
            r = self.run_script("2", "3", out)
            self.assertEqual(r.returncode, 0, r.stderr)
            self.assertIn("bad edges 0", r.stdout)
            self.assertIn("84.00 x 126.00 x 4.65 mm", r.stdout)
            self.assertGreater(self.stl_triangles(out), 0)

    def test_inch_cell_size(self):
        with tempfile.TemporaryDirectory() as tmp:
            out = os.path.join(tmp, "plate.stl")
            r = self.run_script("3", "3", out, "--cell", "2in")
            self.assertEqual(r.returncode, 0, r.stderr)
            self.assertIn("152.40 x 152.40 x 4.65 mm", r.stdout)
            self.assertIn("not compatible", r.stdout)

    def test_bad_input_gives_clean_error(self):
        for args in (["1", "1", "--cell", "5"], ["0", "3"], ["3", "3", "--cell", "abc"]):
            with self.subTest(args=args):
                r = self.run_script(*args)
                self.assertEqual(r.returncode, 2)
                self.assertNotIn("Traceback", r.stderr)


class ExampleFileTests(unittest.TestCase):
    def test_committed_examples_match_generator(self):
        for cols in (3, 4):
            path = ROOT / "output" / f"gridfinity_baseplate_{cols}x{cols}.stl"
            with self.subTest(path=path.name):
                data = path.read_bytes()
                n = struct.unpack("<I", data[80:84])[0]
                self.assertEqual(n, len(mb.build(cols, cols)))


if __name__ == "__main__":
    unittest.main()
