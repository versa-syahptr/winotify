import winreg

HKEY = winreg.HKEY_CURRENT_USER
SUBKEY = r"SOFTWARE\Classes\{}"


def key_exist(app: str) -> bool:
    try:
        k = winreg.OpenKey(HKEY, SUBKEY.format(app))
        winreg.CloseKey(k)
        return True
    except WindowsError:
        return False


def register(app: str, full_path: str, *, replace=False):
    reg = winreg.ConnectRegistry(None, winreg.HKEY_CURRENT_USER)
    app = format_name(app)

    if not key_exist(app) or replace:
        key = winreg.CreateKey(reg, SUBKEY.format(app))
        with key:
            winreg.SetValueEx(key, '', 0, winreg.REG_SZ, f"URL:{app}")
            winreg.SetValueEx(key, 'URL Protocol', 0, winreg.REG_SZ, '')
            subkey = winreg.CreateKey(key, r"shell\open\command")
            with subkey:
                winreg.SetValueEx(subkey, '', 0, winreg.REG_SZ, f"{full_path} %1")


def format_name(name: str):
    return name.replace(' ', '-')
