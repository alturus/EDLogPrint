from sys import platform
from os import listdir
from os.path import join, isdir


config = {
    'journal_dir': 'default',
    'screenshots_dir': 'default',

    # (Fore, Style)
    # Fore: BLACK, RED, GREEN, YELLOW, BLUE, MAGENTA, CYAN, WHITE
    # Style: DIM, NORMAL, BRIGHT
    'colors': {
        'default': ('WHITE', 'BRIGHT'),
        'event_key': ('GREEN', 'NORMAL'),
        'event_value': ('GREEN', 'BRIGHT'),
        'key': ('WHITE', 'BRIGHT'),
        'value': ('WHITE', 'NORMAL'),
    }
}


def default_dir(regkey):
    assert ('win32' in platform), "This code runs on Windows only."
    import winreg

    subkey = r'Software\Microsoft\Windows\CurrentVersion\Explorer\Shell Folders'
    default_dir = None
    try:
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, subkey) as hkey:
            keyval = winreg.QueryValueEx(hkey, regkey)[0]
            default_dir = join(keyval, 'Frontier Developments', 'Elite Dangerous')
    except WindowsError:
        return None

    if not isdir(default_dir):
        return None

    return default_dir


if not isdir(config['journal_dir']):
    FOLDERID_SavedGames = '{4C5C32FF-BB9D-43B0-B5B4-2D72E54EAAA4}'
    config['journal_dir'] = default_dir(FOLDERID_SavedGames)

if not isdir(config['screenshots_dir']):
    config['screenshots_dir'] = default_dir('My Pictures')
