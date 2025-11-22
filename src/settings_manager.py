import os
from pathlib import Path
from PyQt5.QtCore import QSettings, QByteArray


class SettingsManager:

    BASE_DIR = Path(__file__).resolve().parent
    SETTINGS_INI_PATH = BASE_DIR.parent / "settings.ini"
    STYLES_PATH = BASE_DIR / "styles"
    IMAGES_PATH = BASE_DIR / "images"
    LANGUAGE_PATH = BASE_DIR / "language"
    APPLICATION_DATA_FOLDER = Path.home() / "Documents" / "MarmaraConnector"
    APPLICATION_DATA_FOLDER.mkdir(parents=True, exist_ok=True)

    def __init__(self):
        # INI dosyasının konumu
        self.settings = QSettings(str(self.SETTINGS_INI_PATH), QSettings.IniFormat)

    # -------------------------------------------------
    # WINDOW GEOMETRY
    # -------------------------------------------------
    def save_geometry(self, window):
        self.settings.setValue("window/geometry", window.saveGeometry())
        self.settings.setValue("window/state", window.saveState())

    def restore_geometry(self, window):
        geo = self.settings.value("window/geometry")
        st = self.settings.value("window/state")
        if geo:
            window.restoreGeometry(geo)
        if st:
            window.restoreState(st)

    # -------------------------------------------------
    # GENERAL
    # -------------------------------------------------
    def get_language(self):
        return self.settings.value("general/language", "EN")

    def set_language(self, lang):
        self.settings.setValue("general/language", lang)

    def get_style(self):
        return self.settings.value("general/style", "light")

    def set_style(self, style):
        self.settings.setValue("general/style", style)

    def get_font_size(self):
        return int(self.settings.value("general/font_size", 12))

    def set_font_size(self, size):
        self.settings.setValue("general/font_size", size)

    # -------------------------------------------------
    # PATHS
    # -------------------------------------------------
    def get_path(self, key):
        path = self.settings.value(f"paths/{key}")
        if not path:
            return ""
        return os.path.normpath(path)

    def set_path(self, key, value):
        self.settings.setValue(f"paths/{key}", value)

    # -------------------------------------------------
    # STYLE FILE
    # -------------------------------------------------
    def read_style(self, style_name):
        file_path = self.STYLES_PATH / style_name
        return file_path.read_text()

    def language_files(self):
        return {file.stem: file for file in self.LANGUAGE_PATH.glob("*.qm")}