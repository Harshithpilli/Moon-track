from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QFormLayout, QLabel,
    QPushButton, QLineEdit, QMessageBox, QCheckBox, QFileDialog, QGroupBox, QTabWidget
)
from PyQt5.QtCore import QTimer
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

from tracking.moon_tracker import MoonTracker
from measurement.spectrum_icd import SpectrumICD
from measurement.signal_detector import SignalDetector
from computation.gt_calculator import GTCalculator

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Moon Tracker G/T Measurement")
        self.resize(1000, 700)
        self.statusBar().showMessage("Ready")

        self.tracker = MoonTracker(lat=40.0, lon=-75.0, elev=100.0)
        self.spectrum = SpectrumICD(dummy=True)
        self.detector = SignalDetector(smoothing_window=3, threshold_db=2.0)
        self.gtcalc = GTCalculator(freq_hz=2.505e9)
        self.connected = False
        self.tracking_live = True
        self.measurement_live = True

        # --- Tabs ---
        self.tabs = QTabWidget()
        self.setCentralWidget(self.tabs)

        # --- Main Tab (Tracking, Spectrum, Results) ---
        main_tab = QWidget()
        main_layout = QVBoxLayout()

        # Moon Tracking Section
        tracking_group = QGroupBox("Moon Tracking")
        tracking_form = QFormLayout()
        self.az_label = QLabel("--")
        self.el_label = QLabel("--")
        self.utc_label = QLabel("--")
        self.tracking_status = QLabel("Live")
        self.tracking_toggle_btn = QPushButton("Pause")
        self.tracking_toggle_btn.clicked.connect(self.toggle_tracking)
        self.refresh_btn = QPushButton("Refresh")
        self.refresh_btn.clicked.connect(self.update_tracking_section)
        btn_row = QHBoxLayout()
        btn_row.addWidget(self.tracking_toggle_btn)
        btn_row.addWidget(self.refresh_btn)
        tracking_form.addRow("Azimuth (°):", self.az_label)
        tracking_form.addRow("Elevation (°):", self.el_label)
        tracking_form.addRow("UTC:", self.utc_label)
        tracking_form.addRow("Status:", self.tracking_status)
        tracking_form.addRow(btn_row)
        tracking_group.setLayout(tracking_form)
        main_layout.addWidget(tracking_group)

        # Spectrum Analyzer Section
        spectrum_group = QGroupBox("Spectrum Analyzer Settings")
        spectrum_form = QFormLayout()
        self.ip_edit = QLineEdit(self.spectrum.ip)
        self.port_edit = QLineEdit(str(self.spectrum.port))
        self.freq_edit = QLineEdit(str(self.spectrum.center_freq))
        self.span_edit = QLineEdit(str(self.spectrum.span))
        self.rbw_edit = QLineEdit(str(self.spectrum.rbw))
        self.vbw_edit = QLineEdit(str(self.spectrum.vbw))
        self.sweep_edit = QLineEdit(str(self.spectrum.sweep_time))
        self.points_edit = QLineEdit(str(self.spectrum.points))
        self.dummy_checkbox = QCheckBox("Dummy Mode (Simulated)")
        self.dummy_checkbox.setChecked(self.spectrum.dummy)
        self.connect_btn = QPushButton("Connect")
        self.connect_btn.clicked.connect(self.connect_spectrum)
        self.connection_status = QLabel("Disconnected")
        spectrum_form.addRow("IP:", self.ip_edit)
        spectrum_form.addRow("Port:", self.port_edit)
        spectrum_form.addRow("Center Freq (Hz):", self.freq_edit)
        spectrum_form.addRow("Span (Hz):", self.span_edit)
        spectrum_form.addRow("RBW (Hz):", self.rbw_edit)
        spectrum_form.addRow("VBW (Hz):", self.vbw_edit)
        spectrum_form.addRow("Sweep Time (s):", self.sweep_edit)
        spectrum_form.addRow("Points:", self.points_edit)
        spectrum_form.addRow(self.dummy_checkbox)
        spectrum_form.addRow(self.connect_btn)
        spectrum_form.addRow("Status:", self.connection_status)
        spectrum_group.setLayout(spectrum_form)
        main_layout.addWidget(spectrum_group)

        # Results Section
        results_group = QGroupBox("Results")
        results_layout = QVBoxLayout()
        self.y_label = QLabel("Y-factor: --")
        self.gt_label = QLabel("G/T: --")
        self.calc_btn = QPushButton("Compute G/T")
        self.calc_btn.clicked.connect(self.update_results_section)
        self.clear_btn = QPushButton("Clear Results")
        self.clear_btn.clicked.connect(self.clear_results)
        btn_row3 = QHBoxLayout()
        btn_row3.addWidget(self.calc_btn)
        btn_row3.addWidget(self.clear_btn)
        results_layout.addWidget(self.y_label)
        results_layout.addWidget(self.gt_label)
        results_layout.addLayout(btn_row3)
        results_group.setLayout(results_layout)
        main_layout.addWidget(results_group)

        main_tab.setLayout(main_layout)
        self.tabs.addTab(main_tab, "Main")

        # --- Measurement Tab (Trace Plot) ---
        measurement_tab = QWidget()
        measurement_layout = QVBoxLayout()
        measurement_group = QGroupBox("Measurement & Trace")
        vbox = QVBoxLayout()
        self.trace_canvas = FigureCanvas(Figure(figsize=(5, 3)))
        self.ax = self.trace_canvas.figure.subplots()
        self.measure_btn = QPushButton("Acquire Trace & Detect")
        self.measure_btn.clicked.connect(self.update_measurement_section)
        self.measure_live_btn = QPushButton("Pause Live")
        self.measure_live_btn.clicked.connect(self.toggle_measurement)
        self.save_btn = QPushButton("Save Trace")
        self.save_btn.clicked.connect(self.save_trace)
        btn_row2 = QHBoxLayout()
        btn_row2.addWidget(self.measure_btn)
        btn_row2.addWidget(self.measure_live_btn)
        btn_row2.addWidget(self.save_btn)
        vbox.addWidget(self.trace_canvas)
        vbox.addLayout(btn_row2)
        measurement_group.setLayout(vbox)
        measurement_layout.addWidget(measurement_group)
        measurement_tab.setLayout(measurement_layout)
        self.tabs.addTab(measurement_tab, "Measurement")

        # Timers for live updates
        self.tracking_timer = QTimer()
        self.tracking_timer.timeout.connect(self.update_tracking_section)
        self.tracking_timer.start(2000)

        self.measurement_timer = QTimer()
        self.measurement_timer.timeout.connect(self.update_measurement_section)
        self.measurement_timer.start(3000)

    # --- Section update methods ---
    def update_tracking_section(self):
        if not self.tracking_live:
            self.tracking_status.setText("Paused")
            return
        pos = self.tracker.get_moon_position()
        self.az_label.setText(f"{pos['azimuth_deg']:.2f}")
        self.el_label.setText(f"{pos['elevation_deg']:.2f}")
        self.utc_label.setText(f"{pos['utc']}")
        self.tracking_status.setText("Live")

    def toggle_tracking(self):
        self.tracking_live = not self.tracking_live
        if self.tracking_live:
            self.tracking_status.setText("Live")
            self.tracking_toggle_btn.setText("Pause")
        else:
            self.tracking_status.setText("Paused")
            self.tracking_toggle_btn.setText("Resume")

    def connect_spectrum(self):
        try:
            self.spectrum.ip = self.ip_edit.text()
            self.spectrum.port = int(self.port_edit.text())
            self.spectrum.center_freq = float(self.freq_edit.text())
            self.spectrum.span = float(self.span_edit.text())
            self.spectrum.rbw = float(self.rbw_edit.text())
            self.spectrum.vbw = float(self.vbw_edit.text())
            self.spectrum.sweep_time = float(self.sweep_edit.text())
            self.spectrum.points = int(self.points_edit.text())
            self.spectrum.dummy = self.dummy_checkbox.isChecked()
        except Exception as e:
            QMessageBox.warning(self, "Input Error", f"Invalid input: {e}")
            return

        if self.spectrum.connect():
            self.spectrum.set_params()
            self.connection_status.setText("Connected")
            self.statusBar().showMessage("Connected to Spectrum Analyzer.")
            self.connect_btn.setEnabled(False)
        else:
            self.connection_status.setText("Failed")
            QMessageBox.warning(self, "Connection", "Failed to connect.")

    def update_measurement_section(self):
        if not self.measurement_live:
            return
        # Get current Moon position
        moon_pos = self.tracker.get_moon_position()
        az = moon_pos["azimuth_deg"]
        el = moon_pos["elevation_deg"]
        # Get spectrum trace
        trace = self.spectrum.get_trace()
        # Detect hot/cold
        result = self.detector.detect_hot_cold(trace, az, el, az, el)
        # Plot
        self.ax.clear()
        self.ax.plot(trace, label="Trace")
        self.ax.axhline(result["hot"], color="r", linestyle="--", label="Hot")
        self.ax.axhline(result["cold"], color="b", linestyle="--", label="Cold")
        self.ax.set_title("Spectrum Trace (dB)")
        self.ax.legend()
        self.trace_canvas.draw()
        # Store for results section and saving
        self.last_result = result
        self.last_trace = trace

    def toggle_measurement(self):
        self.measurement_live = not self.measurement_live
        if self.measurement_live:
            self.measure_live_btn.setText("Pause Live")
            self.statusBar().showMessage("Measurement live updates resumed.")
        else:
            self.measure_live_btn.setText("Resume Live")
            self.statusBar().showMessage("Measurement live updates paused.")

    def save_trace(self):
        if not hasattr(self, "last_trace"):
            QMessageBox.warning(self, "No Data", "No trace to save.")
            return
        path, _ = QFileDialog.getSaveFileName(self, "Save Trace", "", "CSV Files (*.csv)")
        if path:
            try:
                import numpy as np
                np.savetxt(path, self.last_trace, delimiter=",")
                self.statusBar().showMessage(f"Trace saved to {path}")
            except Exception as e:
                QMessageBox.warning(self, "Save Error", str(e))

    def update_results_section(self):
        try:
            result = getattr(self, "last_result", None)
            if not result:
                QMessageBox.warning(self, "No Data", "No measurement available.")
                return
            y = self.gtcalc.compute_y_factor(result["hot"], result["cold"])
            gt = self.gtcalc.compute_gt(result["hot"], result["cold"])
            self.y_label.setText(f"Y-factor: {y:.2f}")
            self.gt_label.setText(f"G/T: {gt:.2f} dB/K")
            self.statusBar().showMessage("G/T computed.")
        except Exception as e:
            QMessageBox.warning(self, "Error", str(e))

    def clear_results(self):
        self.y_label.setText("Y-factor: --")
        self.gt_label.setText("G/T: --")
        self.statusBar().showMessage("Results cleared.")