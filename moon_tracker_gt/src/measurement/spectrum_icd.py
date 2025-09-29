import socket
import time
import yaml
import os

try:
    import pyvisa
except ImportError:
    pyvisa = None

class SpectrumICD:
    def __init__(self, config_path=None, dummy=False):
        # Load config
        if config_path is None:
            module_dir = os.path.dirname(os.path.abspath(__file__))
            project_root = os.path.dirname(os.path.dirname(os.path.dirname(module_dir)))
            config_path = os.path.join(project_root, "moon_tracker_gt", "config.yaml")
        with open(config_path, "r") as f:
            cfg = yaml.safe_load(f)
        self.cfg = cfg.get("spectrum_analyzer", {})
        self.ip = self.cfg.get("ip", "127.0.0.1")
        self.port = self.cfg.get("port", 5025)
        self.center_freq = self.cfg.get("center_freq", 2.505e9)
        self.span = self.cfg.get("span", 50e6)
        self.rbw = self.cfg.get("rbw", 300e3)
        self.vbw = self.cfg.get("vbw", 3e6)
        self.sweep_time = self.cfg.get("sweep_time", 0.4)
        self.points = self.cfg.get("points", 1001)
        self.ref_level = self.cfg.get("ref_level", 0.0)
        self.input_att = self.cfg.get("input_att", 10.0)
        self.dummy = dummy
        self.conn = None
        self.rm = None

    def connect(self, use_pyvisa=False):
        if self.dummy:
            self.conn = "dummy"
            return True
        try:
            if use_pyvisa and pyvisa:
                self.rm = pyvisa.ResourceManager()
                resource_str = f"TCPIP::{self.ip}::{self.port}::SOCKET"
                self.conn = self.rm.open_resource(resource_str, timeout=5000)
                return True
            else:
                self.conn = socket.create_connection((self.ip, self.port), timeout=5)
                return True
        except Exception as e:
            print(f"Connection failed: {e}")
            return False

    def set_params(self):
        if self.dummy:
            return True
        cmds = [
            f":FREQ:CENT {self.center_freq}",
            f":FREQ:SPAN {self.span}",
            f":BAND {self.rbw}",
            f":BAND:VID {self.vbw}",
            f":SWE:TIME {self.sweep_time}",
            f":SWE:POIN {self.points}",
            f":DISP:WIND:TRAC:Y:RLEV {self.ref_level}",
            f":INP:ATT {self.input_att}",
        ]
        for cmd in cmds:
            self._write(cmd)
        return True

    def get_trace(self):
        if self.dummy:
            return [float(i) for i in range(self.points)]
        self._write(":INIT;*WAI")
        self._write(":TRAC? TRACE1")
        data = self._read()
        try:
            return [float(x) for x in data.strip().split(",")]
        except Exception as e:
            print(f"Error parsing trace data: {e}")
            return []

    def get_idn(self):
        if self.dummy:
            return "DUMMY,MODEL,0,0"
        self._write("*IDN?")
        return self._read().strip()

    def _write(self, cmd):
        if self.dummy:
            return
        if self.rm and hasattr(self.conn, "write"):
            self.conn.write(cmd)
        else:
            self.conn.sendall((cmd + "\n").encode())

    def _read(self):
        if self.dummy:
            return ",".join(str(i) for i in range(self.points))
        if self.rm and hasattr(self.conn, "read"):
            return self.conn.read()
        else:
            data = b""
            while True:
                chunk = self.conn.recv(4096)
                if not chunk:
                    break
                data += chunk
                if b"\n" in chunk:
                    break
            return data.decode()

    def close(self):
        if self.dummy:
            return
        if self.conn:
            if self.rm and hasattr(self.conn, "close"):
                self.conn.close()
                self.rm.close()
            else:
                self.conn.close()

if __name__ == "__main__":
    # Set dummy=False for real hardware
    icd = SpectrumICD(dummy=False)
    if icd.connect(use_pyvisa=False):  # use_pyvisa=False for raw socket over LAN
        print("Connected.")
        print("Instrument ID:", icd.get_idn())
        icd.set_params()
        trace = icd.get_trace()
        print("Trace:", trace[:10], "...")
        # Analyze trace with SignalDetector
        try:
            from measurement.signal_detector import SignalDetector
        except ImportError:
            from signal_detector import SignalDetector
        detector = SignalDetector()
        # Example: use dummy az/el values, replace with real tracking if available
        result = detector.detect_hot_cold(trace, az=0, el=0, moon_az=0, moon_el=0)
        print("Signal Detection Result:", result)
        icd.close()
    else:
        print("Failed to connect.")