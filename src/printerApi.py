import warnings
import os
import json
import sys

from printer import PrinterDriver, PrinterError
from bleak.exc import BleakDBusError, BleakError    # pylint: disable=wrong-import-order
from printer_lib.ipp import IPP
# Supress non-sense asyncio warnings

warnings.simplefilter('ignore', RuntimeWarning, 0, True)
IsAndroid = (os.environ.get("P4A_BOOTSTRAP") is not None)


class DictAsObject(dict):
    " Let you use a dict like an object in JavaScript. "

    def __getattr__(self, key):
        return self.get(key, None)

    def __setattr__(self, key, value):
        self[key] = value


class PrinterServerError(PrinterError):
    'Error of PrinterServer'


class PrinterHandler():
    buffer = 4 * 1024 * 1024
    max_payload = buffer * 16
    settings = DictAsObject({
        'config_path': os.path.abspath(os.path.join("config.json")),
        'version': 4,
        'first_run': True,
        'is_android': False,
        'scan_time': 4.0,
        'dry_run': False,
        'energy': 64,
        'quality': 36
    })
    _settings_blacklist = (
        'printer', 'is_android'
    )
    all_script: list = []
    printer: PrinterDriver = PrinterDriver()
    IPPHandler = IPP
    ipp: IPP = None

    def load_config(self):
        'Load config file, or if not exist, create one with default'
        if IsAndroid:
            self.settings['is_android'] = True
            from android.storage import app_storage_path    # pylint: disable=import-error
            settings_path = app_storage_path()
            os.makedirs(settings_path, exist_ok=True)
            self.settings['config_path'] = os.path.join(
                settings_path, 'config.json'
            )
        if os.path.exists(self.settings.config_path):
            with open(self.settings.config_path, 'r', encoding='utf-8') as file:
                settings = DictAsObject(json.load(file))
                if (settings.version is None or
                        settings.version < self.settings.version):
                    # Version too old, start over
                    # TODO: selective?
                    self.save_config()
                    return
                for key in settings:
                    self.settings[key] = settings[key]
        else:
            if os.name in ('posix',) or IsAndroid:
                self.settings['scan_time'] = 2.0
            self.save_config()

    def save_config(self):
        'Save config file'
        with open(self.settings.config_path, 'w', encoding='utf-8') as file:
            settings = {}
            for i in self.settings:
                if i not in self._settings_blacklist:
                    settings[i] = self.settings[i]
            json.dump(settings, file, indent=4)

    def update_printer(self):
        'Update `PrinterDriver` state/config'
        self.printer.dry_run = self.settings.dry_run
        self.printer.scan_time = self.settings.scan_time
        self.printer.fake = self.settings.fake
        self.printer.dump = self.settings.dump
        if self.settings.energy is not None:
            self.printer.energy = int(self.settings.energy) * 0x100
        if self.settings.quality is not None:
            self.printer.speed = int(self.settings.quality)
        self.printer.flip_h = self.settings.flip_h or self.settings.flip
        self.printer.flip_v = self.settings.flip_v or self.settings.flip
        self.printer.rtl = self.settings.force_rtl

    def exit(self):
        'Stop correctly & cleanly'
        self.save_config()
        self.printer.unload()
        sys.exit(0)
