import os
import platform
from pathlib import Path
import logging
from PyQt5.QtCore import QSettings, QByteArray
from utils.csv_file_handler import CSVFileHandler


class ConfigManager:
    APP_NAME = "MarmaraConnector"
    BASE_DIR = Path(__file__).resolve().parent
    STYLES_PATH = BASE_DIR / "styles"
    IMAGES_PATH = BASE_DIR / "images"
    LANGUAGE_PATH = BASE_DIR / "language"
    CONTACTS_HEADER = ['Name', 'Address', 'Pubkey', 'Group']
    REMOTE_HOSTS_HEADER = ['Name', 'UserName', 'HostIp', 'Port']

    def __init__(self):
        self.app_dir = self._get_config_dir()
        self.app_dir.mkdir(parents=True, exist_ok=True)
        self.ini_path = self.app_dir / "app.ini"
        self.log_path = self.app_dir / "marmara_connector.log"
        self.history_path = self.app_dir / "rpc_history.csv"
        self.settings = QSettings(str(self.ini_path), QSettings.IniFormat)
        self._setup_logger()

    def _get_config_dir(self) -> Path:
        home = Path.home()

        if platform.system() == "Windows":
            return home / "AppData" / "Roaming" / self.APP_NAME

        elif platform.system() == "Darwin":
            return home / "Library" / "Application Support" / self.APP_NAME

        else:  # Linux & others
            return home / ".config" / self.APP_NAME

    def _setup_logger(self):
        self.logger = logging.getLogger(self.APP_NAME)
        self.logger.setLevel(logging.INFO)

        if not self.logger.handlers:
            handler = logging.FileHandler(self.log_path, encoding="utf-8")
            formatter = logging.Formatter(
                "%(asctime)s | %(levelname)s | %(name)s | %(module)s:%(funcName)s:%(lineno)d | %(message)s"
            )
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)

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
    def get_contacts_path(self):
        path = self.settings.value(f"paths/contacts_file")
        if not path:
            print(path)
            return ""
        return os.path.normpath(path)

    def set_contacts_path(self, path):
        self.settings.setValue(f"paths/contacts_file", path)

    def get_local_chain_path(self):
        path = self.settings.value(f"paths/local_chain")
        if not path:
            return ""
        return os.path.normpath(path)

    def set_local_chain_path(self, path):
        self.settings.setValue(f"paths/local_chain", path)

    def get_remote_host_save_files_path(self):
        path = self.settings.value(f"paths/remote_host_save_files")
        if not path:
            return ""
        return os.path.normpath(path)

    def set_remote_host_save_files_path(self, path):
        self.settings.setValue(f"paths/remote_host_save_files", path)

    # -------------------------------------------------
    # STYLE FILE
    # -------------------------------------------------
    def read_style(self, style_name):
        file_path = self.STYLES_PATH / style_name
        return file_path.read_text()

    def language_files(self):
        return {file.stem: file for file in self.LANGUAGE_PATH.glob("*.qm")}
