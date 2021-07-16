import win32api
import win32con
import winreg
import sys
import os

def is_key_exist(key_name=None,
                 reg_root=win32con.HKEY_CURRENT_USER,
                 reg_path=r"SOFTWARE\Microsoft\Windows\CurrentVersion\Run",
                 abspath=None
                 ):
    reg_flags = win32con.WRITE_OWNER | win32con.KEY_WOW64_64KEY | win32con.KEY_ALL_ACCESS
    try:
        key = winreg.OpenKey(reg_root, reg_path, 0, reg_flags)
        location, type = winreg.QueryValueEx(key, key_name)
        feedback = 0
        if location != abspath:
            feedback = 1
    except FileNotFoundError as e:
        feedback = 1
    except PermissionError as e:
        feedback = 2
    except:
        feedback = 3
    return feedback

def autorun(status, key_name, abspath=os.path.abspath(sys.argv[0])):
    key_exist = is_key_exist(reg_root=win32con.HKEY_CURRENT_USER,
                             reg_path=r"Software\Microsoft\Windows\CurrentVersion\Run",
                             key_name=key_name,
                             abspath=abspath)
    KeyName = r'Software\Microsoft\Windows\CurrentVersion\Run'
    key = win32api.RegOpenKey(win32con.HKEY_CURRENT_USER, KeyName, 0, win32con.KEY_ALL_ACCESS)
    if status:
        try:
            win32api.RegSetValueEx(key, key_name, 0, win32con.REG_SZ, abspath)
            win32api.RegCloseKey(key)
            return True
        except:
            return False
    try:
        if key_exist == 0:
            win32api.RegDeleteValue(key, key_name)
            win32api.RegCloseKey(key)
            return True
    except:
        pass
    return False