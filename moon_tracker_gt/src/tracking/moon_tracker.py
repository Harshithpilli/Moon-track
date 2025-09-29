from skyfield.api import load, load_file, Topos
from datetime import datetime, timezone
import time
import os

class MoonTracker:
    def __init__(self, eph_path="data/de421.bsp", lat=0.0, lon=0.0, elev=0.0):
        # Make path relative to the module location
        module_dir = os.path.dirname(os.path.abspath(__file__))
        project_root = os.path.dirname(os.path.dirname(os.path.dirname(module_dir)))
        eph_path = os.path.join(project_root, "moon_tracker_gt", eph_path)
        self.eph = load_file(eph_path)
        self.ts = load.timescale()
        self.moon = self.eph['moon']
        self.observer = Topos(latitude_degrees=lat, longitude_degrees=lon, elevation_m=elev)

    def get_moon_position(self):
        t = self.ts.utc(datetime.now(timezone.utc))
        astrometric = (self.eph['earth'] + self.observer).at(t).observe(self.moon).apparent()
        alt, az, distance = astrometric.altaz()
        return {
            "utc": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC"),
            "azimuth_deg": round(az.degrees, 2),
            "elevation_deg": round(alt.degrees, 2),
            "distance_km": round(distance.km, 0)
        }

if __name__ == "__main__":
    tracker = MoonTracker()
    print("Starting Moon Tracker (Press Ctrl+C to stop)...\n")
    try:
        while True:
            pos = tracker.get_moon_position()
            print(f"[{pos['utc']}]  Az: {pos['azimuth_deg']}°  "
                  f"El: {pos['elevation_deg']}°  Dist: {pos['distance_km']} km")
            time.sleep(5)
    except KeyboardInterrupt:
        print("\nTracking stopped by user.")
