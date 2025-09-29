# test_measurement.py
# Unit tests for spectrum + signal detection

import unittest
from src.measurement.spectrum_icd import SpectrumICD

class TestSpectrumICD(unittest.TestCase):
    def setUp(self):
        self.icd = SpectrumICD(dummy=True)

    def test_connect(self):
        self.assertTrue(self.icd.connect())

    def test_set_params(self):
        self.icd.connect()
        self.assertTrue(self.icd.set_params())

    def test_get_trace(self):
        self.icd.connect()
        self.icd.set_params()
        trace = self.icd.get_trace()
        self.assertEqual(len(trace), self.icd.points)
        self.assertTrue(all(isinstance(x, float) for x in trace))

    def tearDown(self):
        self.icd.close()

if __name__ == "__main__":
    unittest.main()