from pathlib import Path
from PyQt5.QtCore import QSettings, QByteArray


class SettingsManager:
    def __init__(self, ini_path=None):
        # INI dosyasının konumu
        base_dir = Path(__file__).resolve().parent
        if ini_path is None:
            ini_path = base_dir / "app.ini"

        self.ini_path = ini_path
        self.styles_path = base_dir / 'styles'
        self.images_path = base_dir / 'images'
        self.language_path = base_dir / 'language'
        self.settings = QSettings(str(ini_path), QSettings.IniFormat)

        self.application_data_folder = (
            Path.home() / "Documents" / "MarmaraConnector"
        )
        self.application_data_folder.mkdir(parents=True, exist_ok=True)

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
    def get_path(self, key, default=""):
        return self.settings.value(f"paths/{key}", default)

    def set_path(self, key, value):
        self.settings.setValue(f"paths/{key}", value)

    # -------------------------------------------------
    # STYLE FILE
    # -------------------------------------------------
    def read_style(self, style_name):
        file_path = self.styles_path / style_name
        return file_path.read_text()
