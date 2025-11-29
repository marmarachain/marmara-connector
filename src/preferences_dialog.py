from PyQt5.QtWidgets import QDialog, QFormLayout
from PyQt5.QtGui import QIcon

from ui.generated.ui_preferences import Ui_Preferences


class PreferencesDialog(QDialog):

    def __init__(self, config_manager, parent=None):
        super().__init__(parent)

        self.config = config_manager

        self.ui = Ui_Preferences()
        self.ui.setupUi(self)
        self.remote_chain_layout = QFormLayout(self.ui.remote_chain_groupBox)
        self.load_settings()

    # -------------------------------------------------
    # LOAD SETTINGS INTO UI
    # -------------------------------------------------
    def load_settings(self):
        self.load_languages()
        self.load_styles()

        self.ui.lang_comboBox.setCurrentText(self.config.get_language())
        self.ui.style_comboBox.setCurrentText(self.config.get_style())
        self.ui.font_size_spinBox.setValue(self.config.get_font_size())

        self.ui.contacts_save_file_lineEdit.setText(self.config.get_contacts_path())
        self.ui.local_chain_location_lineEdit.setText(self.config.get_local_chain_path())
        self.ui.remote_host_save_file_lineEdit.setText(self.config.get_remote_host_save_files_path())

    # -------------------------------------------------
    # LOAD LANGUAGE FILES
    # -------------------------------------------------
    def load_languages(self):
        qm_files = sorted(self.config.LANGUAGE_PATH.glob("*.qm"))
        for file in qm_files:
            lang_name = file.stem
            self.ui.lang_comboBox.addItem(lang_name)
            lang_icon = self.config.IMAGES_PATH / f"{lang_name}.png"
            if lang_icon.exists():
                lang_index = self.ui.lang_comboBox.findText(lang_name)
                self.ui.lang_comboBox.setItemIcon(lang_index, QIcon(str(lang_icon)))

    # -------------------------------------------------
    # LOAD STYLES
    # -------------------------------------------------
    def load_styles(self):
        self.ui.style_comboBox.clear()
        self.ui.style_comboBox.addItem("light")

        qss_files = sorted(self.config.STYLES_PATH.glob("*.qss"))
        for file in qss_files:
            self.ui.style_comboBox.addItem(file.stem)

    # -------------------------------------------------
    # SAVE WHEN OK
    # -------------------------------------------------
    def done(self, result):
        if result == QDialog.Accepted:
            self.save_settings()
        super().done(result)

    def save_settings(self):
        self.config.set_language(self.ui.lang_comboBox.currentText())
        self.config.set_style(self.ui.style_comboBox.currentText())
        self.config.set_font_size(self.ui.font_size_spinBox.value())

        self.config.set_contacts_path(self.ui.contacts_save_file_lineEdit.text())
        self.config.set_local_chain_path(self.ui.local_chain_location_lineEdit.text())
        self.config.set_remote_host_save_files_path(self.ui.remote_host_save_file_lineEdit.text())
