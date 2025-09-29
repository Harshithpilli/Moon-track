# gt_calculator.py
# Y-factor and G/T computation logic

import math
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")

class GTCalculator:
    def __init__(self, freq_hz=2.505e9):
        self.freq_hz = freq_hz  # Frequency in Hz
        self.k = 1.380649e-23   # Boltzmann constant (J/K)

    def compute_y_factor(self, phot_db, pcold_db):
        """Compute Y-factor (linear) from hot/cold powers in dB."""
        y_db = phot_db - pcold_db
        y_linear = 10 ** (y_db / 10)
        logging.info(f"Y-factor (dB): {y_db:.2f}, Y-factor (linear): {y_linear:.4f}")
        return y_linear

    def compute_gt(self, phot_db, pcold_db):
        """Compute G/T (dB/K) using Y-factor and system parameters."""
        y = self.compute_y_factor(phot_db, pcold_db)
        if y <= 1.0:
            logging.warning("Y-factor <= 1.0, invalid for G/T calculation.")
            return float('-inf')
        wavelength = 3e8 / self.freq_hz  # meters
        gt_linear = (8 * math.pi * wavelength) / (self.k * (y - 1))
        gt_db = 10 * math.log10(gt_linear)
        logging.info(f"G/T (dB/K): {gt_db:.2f}")
        return gt_db
if __name__ == "__main__":
    calc = GTCalculator(freq_hz=2.505e9)
    phot_db = 10.0   # Example hot value in dB
    pcold_db = 0.0   # Example cold value in dB
    y = calc.compute_y_factor(phot_db, pcold_db)
    gt = calc.compute_gt(phot_db, pcold_db)
    print(f"Y-factor (linear): {y:.4f}")
    print(f"G/T (dB/K): {gt:.2f}")