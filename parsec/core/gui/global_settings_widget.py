# Parsec Cloud (https://parsec.cloud) Copyright (c) AGPLv3 2019 Scille SAS

import platform

from PyQt5.QtCore import pyqtSignal
from PyQt5.QtWidgets import QWidget

from parsec.core.gui import lang
from parsec.core.gui import desktop
from parsec.core.gui.new_version import CheckNewVersion
from parsec.core.gui.ui.global_settings_widget import Ui_GlobalSettingsWidget


class GlobalSettingsWidget(QWidget, Ui_GlobalSettingsWidget):
    save_clicked = pyqtSignal()

    def __init__(self, core_config, jobs_ctx, event_bus, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.core_config = core_config
        self.event_bus = event_bus
        self.jobs_ctx = jobs_ctx
        self.setupUi(self)
        if platform.system() != "Windows":
            self.widget_version.hide()
        self.button_save.clicked.connect(self.save_clicked)
        self.check_box_tray.setChecked(self.core_config.gui_tray_enabled)
        current = None
        for lg, key in lang.LANGUAGES.items():
            self.combo_languages.addItem(lg, key)
            if key == self.core_config.gui_language:
                current = lg
        if current:
            self.combo_languages.setCurrentText(current)
        self.label_user_guide.clicked.connect(self.open_user_guide)
        self.label_send_feedback.clicked.connect(self.open_feedback_link)
        self.check_box_check_at_startup.setChecked(self.core_config.gui_check_version_at_startup)
        self.check_box_send_data.setChecked(self.core_config.telemetry_enabled)
        self.check_box_workspace_color.setChecked(self.core_config.gui_workspace_color)
        self.button_check_version.clicked.connect(self.check_version)

    def open_feedback_link(self):
        desktop.open_url("https://parsec.cloud")

    def open_user_guide(self):
        desktop.open_url("https://parsec.cloud")

    def check_version(self):
        d = CheckNewVersion(self.jobs_ctx, self.event_bus, self.core_config, parent=self)
        d.exec_()

    def save(self):
        self.event_bus.send(
            "gui.config.changed",
            telemetry_enabled=self.check_box_send_data.isChecked(),
            gui_tray_enabled=self.check_box_tray.isChecked(),
            gui_language=self.combo_languages.currentData(),
            gui_check_version_at_startup=self.check_box_check_at_startup.isChecked(),
            gui_workspace_color=self.check_box_workspace_color.isChecked(),
        )
