import sys, subprocess, time, tempfile, threading, requests
from pathlib import Path
from PySide6.QtWidgets import (
    QApplication, QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QProgressBar
)
from PySide6.QtWebEngineWidgets import QWebEngineView
from PySide6.QtWebEngineCore import QWebEngineSettings
from PySide6.QtCore import QUrl, Qt, QTimer
from PySide6.QtGui import QIcon, QPixmap

ROOT        = Path(__file__).parent.parent
ASSETS      = ROOT / "assets"
LAUNCH_FLAG = Path(tempfile.gettempdir()) / "krabbystrap_launch.flag"

_BASE = """
QDialog { background: #202020; }
QLabel#title {
    color: #ffffff; font-size: 20px; font-weight: 700;
    font-family: "Segoe UI", "Noto Sans", system-ui, sans-serif;
}
QLabel#sub, QLabel#status {
    color: rgba(255,255,255,0.40); font-size: 11px;
    font-family: "Segoe UI", "Noto Sans", system-ui, sans-serif;
}
"""

HOME_STYLE = _BASE + """
QPushButton#btn_launch {
    background: #C9B827; color: #0f0f0f; border: none; border-radius: 4px;
    font-size: 13px; font-weight: 600;
    font-family: "Segoe UI", "Noto Sans", system-ui, sans-serif;
    padding: 10px 0; min-width: 140px;
}
QPushButton#btn_launch:hover   { background: #b5a523; }
QPushButton#btn_launch:pressed { background: #9d8f1e; }
QPushButton#btn_settings {
    background: rgba(255,255,255,0.07); color: rgba(255,255,255,0.85);
    border: 1px solid rgba(255,255,255,0.10); border-radius: 4px;
    font-size: 13px;
    font-family: "Segoe UI", "Noto Sans", system-ui, sans-serif;
    padding: 10px 0; min-width: 140px;
}
QPushButton#btn_settings:hover   { background: rgba(255,255,255,0.11); }
QPushButton#btn_settings:pressed { background: rgba(255,255,255,0.05); }
"""

SPLASH_STYLE = _BASE + """
QProgressBar {
    background: rgba(255,255,255,0.08);
    border: none; border-radius: 2px;
}
QProgressBar::chunk { background: #C9B827; border-radius: 2px; }
"""


def _sober_running() -> bool:
    try:
        r = subprocess.run(["flatpak", "ps"], capture_output=True, text=True)
        return "org.vinegarhq.Sober" in r.stdout
    except Exception:
        return False


def _make_brand(parent_layout, icon_size=54, spacing=36):
    brand = QHBoxLayout()
    brand.setSpacing(16)
    brand.setAlignment(Qt.AlignmentFlag.AlignCenter)

    icon_lbl = QLabel()
    px = QPixmap(str(ASSETS / "krabby.png")).scaled(
        icon_size, icon_size,
        Qt.AspectRatioMode.KeepAspectRatio,
        Qt.TransformationMode.SmoothTransformation,
    )
    icon_lbl.setPixmap(px)
    brand.addWidget(icon_lbl)

    text_col = QVBoxLayout()
    text_col.setSpacing(3)
    t = QLabel("Krabbystrap")
    t.setObjectName("title")
    s = QLabel("Roblox launcher for Linux · Sober 1.6.7")
    s.setObjectName("sub")
    text_col.addWidget(t)
    text_col.addWidget(s)
    brand.addLayout(text_col)

    parent_layout.addLayout(brand)
    parent_layout.addSpacing(spacing)


class HomeDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Krabbystrap")
        self.setFixedSize(420, 230)
        self.setWindowFlags(Qt.WindowType.Dialog | Qt.WindowType.WindowCloseButtonHint)
        self.setStyleSheet(HOME_STYLE)
        self.choice = None

        root = QVBoxLayout(self)
        root.setContentsMargins(40, 36, 40, 36)
        root.setSpacing(0)

        _make_brand(root)

        btns = QHBoxLayout()
        btns.setSpacing(10)

        self.btn_launch = QPushButton("Launch")
        self.btn_launch.setObjectName("btn_launch")
        self.btn_launch.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_launch.clicked.connect(self._launch)

        self.btn_settings = QPushButton("Settings")
        self.btn_settings.setObjectName("btn_settings")
        self.btn_settings.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_settings.clicked.connect(self._settings)

        btns.addWidget(self.btn_launch)
        btns.addWidget(self.btn_settings)
        root.addLayout(btns)

    def _launch(self):
        self.choice = "launch"
        self.accept()

    def _settings(self):
        self.choice = "settings"
        self.accept()


class LaunchSplash(QDialog):
    TIMEOUT  = 60
    MIN_SHOW = 3.0

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Krabbystrap")
        self.setFixedSize(420, 200)
        self.setWindowFlags(Qt.WindowType.Dialog | Qt.WindowType.WindowCloseButtonHint)
        self.setStyleSheet(SPLASH_STYLE)

        root = QVBoxLayout(self)
        root.setContentsMargins(40, 36, 40, 36)
        root.setSpacing(0)

        _make_brand(root, icon_size=46, spacing=24)

        self.status_lbl = QLabel("Starting Sober…")
        self.status_lbl.setObjectName("status")
        root.addWidget(self.status_lbl)
        root.addSpacing(8)

        self.bar = QProgressBar()
        self.bar.setRange(0, 100)
        self.bar.setValue(0)
        self.bar.setTextVisible(False)
        self.bar.setFixedHeight(4)
        root.addWidget(self.bar)

        self._lock       = threading.Lock()
        self._found      = False
        self._timed_out  = False
        self._start_time = 0.0

        self._anim = QTimer(self)
        self._anim.setInterval(150)
        self._anim.timeout.connect(self._animate)

    def start(self):
        self._start_time = time.time()
        self._anim.start()
        threading.Thread(target=self._poll, daemon=True).start()

    def _poll(self):
        deadline = time.time() + self.TIMEOUT
        while time.time() < deadline:
            if _sober_running():
                with self._lock:
                    self._found = True
                return
            time.sleep(0.5)
        with self._lock:
            self._timed_out = True

    def _animate(self):
        elapsed = time.time() - self._start_time

        with self._lock:
            found     = self._found
            timed_out = self._timed_out

        if found and elapsed >= self.MIN_SHOW:
            self._anim.stop()
            self.bar.setValue(100)
            self.status_lbl.setText("Launched!")
            QTimer.singleShot(900, self.accept)
            return

        if found:
            self.bar.setValue(100)
            self.status_lbl.setText("Launched!")
            return

        if timed_out:
            self._anim.stop()
            self.status_lbl.setText("Timed out — check if Sober is installed.")
            QTimer.singleShot(2500, self.reject)
            return

        self.bar.setValue(min(int(elapsed / self.TIMEOUT * 85), 85))
        if elapsed < 3:
            self.status_lbl.setText("Starting Sober…")
        elif elapsed < 10:
            self.status_lbl.setText("Waiting for Roblox…")
        else:
            self.status_lbl.setText("Still loading…")


def wait_ready(url, timeout=12):
    t = time.time()
    while time.time() - t < timeout:
        try:
            if requests.get(url, timeout=1).status_code == 200:
                return True
        except Exception:
            pass
        time.sleep(0.25)
    return False


def open_settings(app):
    LAUNCH_FLAG.unlink(missing_ok=True)

    server = subprocess.Popen(
        [sys.executable, str(Path(__file__).parent / "server.py")]
    )
    if not wait_ready("http://127.0.0.1:8502"):
        print("Server failed to start")
        server.terminate()
        sys.exit(1)

    view = QWebEngineView()
    view.setWindowTitle("Krabbystrap")
    view.resize(1000, 580)
    view.setMinimumSize(900, 520)

    s = view.settings()
    s.setAttribute(QWebEngineSettings.WebAttribute.JavascriptEnabled, True)
    s.setAttribute(QWebEngineSettings.WebAttribute.LocalContentCanAccessRemoteUrls, True)

    view.titleChanged.connect(lambda _: view.setWindowTitle("Krabbystrap"))
    view.page().windowCloseRequested.connect(view.close)
    view.load(QUrl("http://127.0.0.1:8502"))
    view.show()

    def _check_flag():
        if LAUNCH_FLAG.exists():
            LAUNCH_FLAG.unlink(missing_ok=True)
            view.close()

    flag_timer = QTimer()
    flag_timer.setInterval(400)
    flag_timer.timeout.connect(_check_flag)
    flag_timer.start()

    code = app.exec()
    flag_timer.stop()
    server.terminate()
    server.wait()
    sys.exit(code)


def main():
    app = QApplication(sys.argv)
    app.setApplicationName("Krabbystrap")

    icon = ASSETS / "krabby.png"
    if icon.exists():
        app.setWindowIcon(QIcon(str(icon)))

    if "--settings" in sys.argv:
        open_settings(app)
        return

    dlg = HomeDialog()
    if dlg.exec() != QDialog.DialogCode.Accepted or dlg.choice is None:
        sys.exit(0)

    if dlg.choice == "launch":
        if _sober_running():
            sys.exit(0)
        subprocess.Popen(
            ["flatpak", "run", "org.vinegarhq.Sober"],
            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
        )
        splash = LaunchSplash()
        splash.start()
        splash.exec()
        sys.exit(0)

    open_settings(app)


if __name__ == "__main__":
    main()
