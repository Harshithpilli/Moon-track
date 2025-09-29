# tests/test_tracker.py
import unittest
import sys
from pathlib import Path
import os

# Add the project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.tracking.moon_tracker import MoonTracker
from datetime import datetime, timezone

class TestMoonTracker(unittest.TestCase):
    """Unit tests for the MoonTracker class."""

    def setUp(self):
        self.tracker = MoonTracker(lat=40.0, lon=-75.0, elev=100.0)

    def test_position_output_keys(self):
        """Test that output dictionary has all required keys."""
        pos = self.tracker.get_moon_position()
        for key in ("azimuth_deg", "elevation_deg", "utc", "distance_km"):
            self.assertIn(key, pos)

    def test_position_value_types(self):
        """Test that output values are of correct types."""
        import numbers
        try:
            import numpy as np
            numeric_types = (float, int, np.floating, np.integer)
        except ImportError:
            numeric_types = (float, int)
        pos = self.tracker.get_moon_position()
        self.assertIsInstance(pos["azimuth_deg"], numeric_types)
        self.assertIsInstance(pos["elevation_deg"], numeric_types)
        self.assertIsInstance(pos["distance_km"], numeric_types)
        self.assertIsInstance(pos["utc"], str)

    def test_azimuth_range(self):
        """Test azimuth is within 0-360 degrees."""
        pos = self.tracker.get_moon_position()
        self.assertGreaterEqual(pos["azimuth_deg"], 0)
        self.assertLessEqual(pos["azimuth_deg"], 360)

    def test_elevation_range(self):
        """Test elevation is within -90 to 90 degrees."""
        pos = self.tracker.get_moon_position()
        self.assertGreaterEqual(pos["elevation_deg"], -90)
        self.assertLessEqual(pos["elevation_deg"], 90)

    def test_distance_range(self):
        """Test moon distance is within expected lunar range (km)."""
        pos = self.tracker.get_moon_position()
        self.assertGreater(pos["distance_km"], 330000)  # Conservative min
        self.assertLess(pos["distance_km"], 410000)     # Conservative max

    def test_utc_time_format(self):
        """Test UTC time string is in correct format."""
        pos = self.tracker.get_moon_position()
        try:
            datetime.strptime(pos["utc"], "%Y-%m-%d %H:%M:%S UTC")
        except ValueError:
            self.fail("UTC time format is incorrect")

    def test_multiple_calls_consistency(self):
        """Test that multiple calls return consistent structure and reasonable values."""
        for _ in range(3):
            pos = self.tracker.get_moon_position()
            self.assertIn("azimuth_deg", pos)
            self.assertIn("elevation_deg", pos)
            self.assertIn("utc", pos)
            self.assertIn("distance_km", pos)
            self.assertGreaterEqual(pos["azimuth_deg"], 0)
            self.assertLessEqual(pos["azimuth_deg"], 360)
            self.assertGreaterEqual(pos["elevation_deg"], -90)
            self.assertLessEqual(pos["elevation_deg"], 90)

if __name__ == "__main__":
    unittest.main()
