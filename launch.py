import sys, subprocess, time, requests
from pathlib import Path
from PySide6.QtWidgets import (
    QApplication, QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton
)
from PySide6.QtWebEngineWidgets import QWebEngineView
from PySide6.QtWebEngineCore import QWebEngineSettings
from PySide6.QtCore import QUrl, Qt
from PySide6.QtGui import QIcon, QPixmap

ASSETS = Path(__file__).parent / "assets"

HOME_STYLE = """
QDialog {
    background: #202020;
}
QLabel#title {
    color: #ffffff;
    font-size: 20px;
    font-weight: 700;
    font-family: "Segoe UI", "Noto Sans", system-ui, sans-serif;
}
QLabel#sub {
    color: rgba(255,255,255,0.40);
    font-size: 11px;
    font-family: "Segoe UI", "Noto Sans", system-ui, sans-serif;
}
QPushButton#btn_launch {
    background: #C9B827;
    color: #0f0f0f;
    border: none;
    border-radius: 4px;
    font-size: 13px;
    font-weight: 600;
    font-family: "Segoe UI", "Noto Sans", system-ui, sans-serif;
    padding: 10px 0;
    min-width: 140px;
}
QPushButton#btn_launch:hover  { background: #b5a523; }
QPushButton#btn_launch:pressed{ background: #9d8f1e; }
QPushButton#btn_settings {
    background: rgba(255,255,255,0.07);
    color: rgba(255,255,255,0.85);
    border: 1px solid rgba(255,255,255,0.10);
    border-radius: 4px;
    font-size: 13px;
    font-family: "Segoe UI", "Noto Sans", system-ui, sans-serif;
    padding: 10px 0;
    min-width: 140px;
}
QPushButton#btn_settings:hover  { background: rgba(255,255,255,0.11); }
QPushButton#btn_settings:pressed{ background: rgba(255,255,255,0.05); }
"""


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

        # ── branding row ──────────────────────────────────────────
        brand = QHBoxLayout()
        brand.setSpacing(16)
        brand.setAlignment(Qt.AlignmentFlag.AlignCenter)

        icon_lbl = QLabel()
        px = QPixmap(str(ASSETS / "krabby.png")).scaled(
            54, 54, Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation
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

        root.addLayout(brand)
        root.addSpacing(36)

        # ── buttons ───────────────────────────────────────────────
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
    view.load(QUrl("http://127.0.0.1:8502"))
    view.show()

    code = app.exec()
    server.terminate()
    server.wait()
    sys.exit(code)


def main():
    app = QApplication(sys.argv)
    app.setApplicationName("Krabbystrap")

    icon = ASSETS / "krabby.png"
    if icon.exists():
        app.setWindowIcon(QIcon(str(icon)))

    # --settings flag skips home screen (e.g. from a shortcut)
    if "--settings" in sys.argv:
        open_settings(app)
        return

    dlg = HomeDialog()
    result = dlg.exec()

    if result != QDialog.DialogCode.Accepted or dlg.choice is None:
        sys.exit(0)

    if dlg.choice == "launch":
        subprocess.Popen(
            ["flatpak", "run", "org.vinegarhq.Sober"],
            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
        )
        sys.exit(0)

    # choice == "settings"
    open_settings(app)


if __name__ == "__main__":
    main()
