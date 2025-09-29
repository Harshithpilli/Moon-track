# signal_detector.py
# Finds hot/cold values from traces

import numpy as np

class SignalDetector:
    def __init__(self, smoothing_window=5, threshold_db=3.0):
        self.smoothing_window = smoothing_window
        self.threshold_db = threshold_db

    def smooth(self, trace):
        """Apply simple moving average smoothing to the trace."""
        if self.smoothing_window < 2:
            return np.array(trace)
        return np.convolve(trace, np.ones(self.smoothing_window)/self.smoothing_window, mode='same')

    def detect_hot_cold(self, trace, az, el, moon_az, moon_el, offset_deg=20):
        """
        Detect hot (on-moon) and cold (off-moon) values.
        - trace: list/array of power values (dB)
        - az, el: current pointing azimuth/elevation
        - moon_az, moon_el: moon azimuth/elevation
        - offset_deg: angular offset for cold measurement
        Returns: dict with 'hot', 'cold', 'delta_db'
        """
        trace = np.array(trace)
        smoothed = self.smooth(trace)
        # For demonstration, assume the trace peak is "hot" if pointing at moon, "cold" if offset
        pointing_error = np.sqrt((az - moon_az)**2 + (el - moon_el)**2)
        if pointing_error < 2.0:  # Within 2°: "hot"
            hot = np.max(smoothed)
            cold = np.median(smoothed)  # Use median as cold reference
        elif abs(pointing_error - offset_deg) < 2.0:  # Near offset: "cold"
            hot = np.median(smoothed)
            cold = np.min(smoothed)
        else:
            hot = np.max(smoothed)
            cold = np.min(smoothed)
        delta_db = hot - cold
        is_hot = delta_db > self.threshold_db
        return {
            "hot": float(hot),
            "cold": float(cold),
            "delta_db": float(delta_db),
            "is_hot": is_hot
        }
if __name__ == "__main__":
    # Example usage and printout
    detector = SignalDetector(smoothing_window=3, threshold_db=2.0)
    # Simulate a trace with a clear peak (hot)
    trace_hot = [1.0]*100 + [10.0] + [1.0]*100
    az, el = 180, 45
    moon_az, moon_el = 180, 45
    result_hot = detector.detect_hot_cold(trace_hot, az, el, moon_az, moon_el)
    print("Hot (on-moon) detection result:")
    print(result_hot)

    # Simulate a flat trace (cold)
    trace_cold = [1.0]*201
    az_off, el_off = 200, 45
    result_cold = detector.detect_hot_cold(trace_cold, az_off, el_off, moon_az, moon_el)
    print("\nCold (off-moon) detection result:")
    print(result_cold)