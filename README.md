# Moon Tracker G/T Measurement Tool

[![Python](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

A Python-based tool for lunar tracking and G/T (gain-to-noise-temperature) computation using Y-factor methods.  

**Features**:
- 🌙 **Skyfield tracking**: computes Azimuth/Elevation/Time for the Moon  
- 📡 **Spectrum analyzer ICD interface**: SCPI over IP/Port  
- 🔍 **Signal detection**: extracts hot/cold values from traces  
- 📊 **G/T calculation**: implements Y-factor computation  
- 🖥️ **PyQt5 GUI**: simple and extensible interface  

---

## 📂 Project Structure

- `moon_tracker_gt/data/de421.bsp` — Ephemeris file (required for skyfield)  
- `moon_tracker_gt/src/` — Source code  
  - `tracking/moon_tracker.py` — Computes Az/El/Time using skyfield  
  - `measurement/spectrum_icd.py` — Spectrum Analyzer ICD interface (IP/Port/SCPI)  
  - `measurement/signal_detector.py` — Finds hot/cold values from traces  
  - `computation/gt_calculator.py` — Y-factor and G/T computation logic  
  - `gui/main_window.py` — PyQt5 GUI module  
  - `main.py` — Entry point  
- `moon_tracker_gt/tests/` — Unit tests for each module  
- `requirements.txt` — Python dependencies  
- `config.yaml` — Configuration (IP, port, frequency, etc.)  

---

## ⚙️ Setup

1. Clone the repository:
   ```bash
   git clone https://github.com/Harshithpilli/Moon-track.git
   cd Moon-track
2. Install dependencies:
   ```bash
   pip install -r moon_tracker_gt/requirements.txt
3. Edit moon_tracker_gt/config.yaml to match your hardware/network setup.
4. Place the de421.bsp ephemeris file in moon_tracker_gt/data/ (replace the placeholder if needed).

## 🖥️ Usage

Run the application:
```bash
python moon_tracker_gt/src/main.py
```
## 🧪 Testing

Run unit tests with:
```bash
pytest moon_tracker_gt/tests
```

## 📦 Dependencies

Core packages:

skyfield

PyQt5

numpy

scipy

pytest

## 🤝 Contributing

Pull requests are welcome.
For major changes, please open an issue first to discuss what you’d like to change.

## Note 
To get the signal powers and readings , connect to any Spectrum Analyzer using LAN Connection.
After connecting, you have to configure the settings in both Spectrum Analyzer and config.yaml file present in the folder(moon_tracker_gt), as per requirements..


