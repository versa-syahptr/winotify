from os import path
import sys
import winreg

HKEY = winreg.HKEY_CURRENT_USER
SUBKEY = r"SOFTWARE\Classes\{}"
SHELLKEY = r"shell\open\command"

PY_EXE = path.join(path.dirname(sys.executable), "python.exe")
PYW_EXE = path.join(path.dirname(sys.executable), "pythonw.exe")


class InvalidKeyStructure(Exception): pass


class Registry:
    def __init__(self, app_id: str, executable=PY_EXE, script_path: str = '', *, force_override=False):
        """
        register app_id to windows registry as a protocol,
        eg. the app_id is "My Awesome App" can be called from browser or run.exe by typing "my-awesome-app:[Params]"
        Params is optional
        :param app_id:
        :param executable: [PY_EXE|PYW_EXE] the executable to register. It can be python, pythonw or your compiled
                           script, default is python.exe
        :param script_path:
        :param force_override: if the `app-id` key is exist in Windows Registry, choose whether

        :raise InvalidKeyStructure: if force_override and the key structure is invalid
        """
        self.app = format_name(app_id)
        self._key = SUBKEY.format(self.app)
        self.executable = executable
        self.path = script_path
        self._override = force_override

        self.reg = winreg.ConnectRegistry(None, winreg.HKEY_CURRENT_USER)
        self._register()

    def _validate_structure(self):
        key = winreg.OpenKey(self.reg, self._key)
        try:
            winreg.OpenKey(key, SHELLKEY).Close()
        except WindowsError:
            raise InvalidKeyStructure(f'The registry from "{self.app}" was not created by winotify or the structure '
                                      f'is invalid')

    def key_exist(self) -> bool:
        try:
            winreg.OpenKey(HKEY, self._key).Close()
            return True
        except WindowsError:
            return False

    def _register(self):

        if self.key_exist() and self._override:
            self._validate_structure()  # validate

        key = winreg.CreateKey(self.reg, self._key)
        with key:
            winreg.SetValueEx(key, '', 0, winreg.REG_SZ, f"URL:{self.app}")
            winreg.SetValueEx(key, 'URL Protocol', 0, winreg.REG_SZ, '')
            subkey = winreg.CreateKey(key, SHELLKEY)
            with subkey:
                winreg.SetValueEx(subkey, '', 0, winreg.REG_SZ, f'{self.executable} {self.path} %1')



def format_name(name: str):
    return name.replace(' ', '-')
