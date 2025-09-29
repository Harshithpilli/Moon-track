import unittest
from src.measurement.signal_detector import SignalDetector

class TestSignalDetector(unittest.TestCase):
    def setUp(self):
        self.detector = SignalDetector(smoothing_window=3, threshold_db=2.0)

    def test_hot_cold_detection_on_moon(self):
        # Simulate a trace with a clear peak (hot)
        trace = [1.0]*100 + [10.0] + [1.0]*100
        az, el = 180, 45
        moon_az, moon_el = 180, 45
        result = self.detector.detect_hot_cold(trace, az, el, moon_az, moon_el)
        self.assertTrue(result["is_hot"])
        self.assertGreater(result["delta_db"], 2.0)

    def test_hot_cold_detection_off_moon(self):
        # Simulate a flat trace (cold)
        trace = [1.0]*201
        az, el = 200, 45
        moon_az, moon_el = 180, 45
        result = self.detector.detect_hot_cold(trace, az, el, moon_az, moon_el)
        self.assertFalse(result["is_hot"])
        self.assertAlmostEqual(result["delta_db"], 0.0, delta=0.35)  # Allow small smoothing error

if __name__ == "__main__":
    unittest.main()