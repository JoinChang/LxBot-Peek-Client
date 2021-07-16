
import sys
import psutil

from PyQt5.QtGui import QIcon
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtWidgets import QApplication, QMainWindow, QDialog, QMessageBox, QSystemTrayIcon, QMenu, QAction
from form.Home import Ui_MainWindow
from form.FrpConfigure import Ui_FrpConfigure
from form.HotkeyConfigure import Ui_HotkeyConfigure

from system_hotkey import SystemHotkey

from thread import WorkThreadFlask, WorkThreadFrp
from autorun import autorun
from config import Config

config = Config()

class MainWindow(QMainWindow, Ui_MainWindow):
    sig_keyhot = pyqtSignal(str) # 热键信号

    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent)
        self.setupUi(self)

        # 多线程
        self.work_flask = WorkThreadFlask()
        self.work_frp = WorkThreadFrp()

        # 点击事件
        self.runPeekButton.clicked.connect(self.run_peek)
        self.configureFrpButton.clicked.connect(self.show_frp_configure)
        self.configureHotkeyButton.clicked.connect(self.show_hotkey_configure)
        self.runFrpButton.clicked.connect(self.run_frp)
        self.forceStopFrpButton.clicked.connect(self.stop_frp)
        self.runInBackgroundButton.clicked.connect(self.hide)
        self.aboutButton.clicked.connect(self.show_about)

        # 其它事件
        self.vagueSlider.setValue(int(config.get("screenshot", "vague", 6)))
        self.vagueSlider.valueChanged.connect(self.vague_change) # 模糊度
        self.brightnessSlider.setValue(int(config.get("screenshot", "brightness", 10)))
        self.brightnessSlider.valueChanged.connect(self.brightness_change) # 亮度
        self.peekStatus.setChecked(int(config.get("client", "status", 0)) == 1)
        self.peekStatus.clicked.connect(self.set_peek_status) # 监控状态
        self.autorun.setChecked(int(config.get("client", "autorun", 0)) == 1)
        self.autorun.clicked.connect(self.set_autorun_status) # 开机自启

        # 托盘
        self.tray = QSystemTrayIcon(self)
        self.tray.setIcon(QIcon('./src/icon.ico'))
        self.tray.setToolTip("LxBot Peek Client")
        self.tray.activated.connect(self.tray_activated)
        self.tray_menu = QMenu(QApplication.desktop())
        self.tray_menu.addAction(QAction('LxBot Peek Client', self, triggered=self.show))
        self.tray_menu.addSeparator()
        self.tray_menu.addAction(QAction('退出', self, triggered=application.quit))
        self.tray.setContextMenu(self.tray_menu)
        self.tray.show()

        self.sig_keyhot.connect(self.key_press_event)

        self.hotkey_switch_peek_status = SystemHotkey()
        if int(config.get("hotkey", "status", 0)) == 1:
            self.hotkey_switch_peek_status.register(
                config.get("hotkey", "switch_peek_status", "control|alt|q").split("|"),
                callback=lambda x: self.send_key_event("switch_peek_status")
            )

    def key_press_event(self, data):
        if int(config.get("hotkey", "status", 0)) == 0:
            return
        if data == "switch_peek_status":
            is_peek_status_on = int(config.get("client", "status", 0)) == 1
            config.set("client", "status", 0 if is_peek_status_on else 1)
            self.peekStatus.setChecked(not is_peek_status_on)
            self.tray.showMessage("LxBot Peek Client", f"已{'启用' if int(config.get('client', 'status', 0)) == 1 else '禁用'}监控状态。")

    def send_key_event(self, data):
        self.sig_keyhot.emit(data)
    
    def tray_activated(self, reason):
        if reason == 3:
            self.show()
            self.raise_()

    def show_about(self):
        QMessageBox.about(self, '关于', 'LxBot Peek Client v1.0.2\nBy Lxns')

    def closeEvent(self, event):
        reply = QMessageBox.question(self, '确认', '关闭后监视服务将被终止，是否关闭？', QMessageBox.Yes, QMessageBox.No)
        if reply == QMessageBox.Yes:
            application.quit()
        else:
            event.ignore()

    def run_peek(self):
        self.runPeekButton.setEnabled(False)
        self.work_flask.start()
 
    def show_frp_configure(self):
        self.child = FrpConfigure()
        self.child.show()
 
    def show_hotkey_configure(self):
        self.child = HotkeyConfigure(self.hotkey_switch_peek_status)
        self.child.show()
    
    def run_frp(self):
        self.runFrpButton.setEnabled(False)
        self.forceStopFrpButton.setEnabled(True)
        self.work_frp.start()
    
    def stop_frp(self):
        reply = QMessageBox.question(self, "确认", "是否要强制终止进程 frpc.exe？", QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if reply == QMessageBox.Yes:
            for pid in psutil.pids():
                try:
                    if psutil.Process(pid).name() == "frpc.exe":
                        psutil.Process(pid).kill()
                        self.runFrpButton.setEnabled(True)
                        self.forceStopFrpButton.setEnabled(False)
                        break
                except:
                    continue
    
    def vague_change(self):
        config.set("screenshot", "vague", self.vagueSlider.value())
    
    def brightness_change(self):
        config.set("screenshot", "brightness", self.brightnessSlider.value())
    
    def set_peek_status(self):
        config.set("client", "status", 1 if self.peekStatus.isChecked() else 0)
    
    def set_autorun_status(self):
        if autorun(self.autorun.isChecked(), key_name="LxBot_Peek_Client"):
            config.set("client", "autorun", 1 if self.autorun.isChecked() else 0)
        else:
            QMessageBox.critical(self, "错误", "设置启动项失败", QMessageBox.Yes)

class FrpConfigure(QDialog, Ui_FrpConfigure):
    def __init__(self, parent=None):
        super(FrpConfigure, self).__init__(parent)
        self.setupUi(self)

        self.setWindowFlags(Qt.WindowMinimizeButtonHint | Qt.WindowCloseButtonHint)
        self.setFixedSize(self.width(), self.height())

        frpc_ini = open("./frpc.ini", "r", encoding="UTF-8").read()
        self.config.setPlainText(frpc_ini)

        self.saveButton.clicked.connect(self.set_configure)
        self.cancelButton.clicked.connect(self.close)
    
    def set_configure(self):
        try:
            f = open("frpc.ini", "w")
            f.write(self.config.toPlainText())
            self.close()
        except:
            QMessageBox.critical(self, "错误", "配置文件写入失败", QMessageBox.Yes)

class HotkeyConfigure(QDialog, Ui_HotkeyConfigure):
    def __init__(self, hotkey_switch_peek_status, parent=None):
        super(HotkeyConfigure, self).__init__(parent)
        self.setupUi(self)

        self.hotkey_switch_peek_status = hotkey_switch_peek_status

        self.setWindowFlags(Qt.WindowMinimizeButtonHint | Qt.WindowCloseButtonHint)
        self.setFixedSize(self.width(), self.height())
        
        self.hotkeyCheckBox.setChecked(int(config.get("hotkey", "status", 0)) == 1) # 热键
        
        self.saveButton.clicked.connect(self.set_configure)
        self.cancelButton.clicked.connect(self.close)
    
    def set_configure(self):
        try:
            config.set("hotkey", "status", 1 if self.hotkeyCheckBox.isChecked() else 0)
            self.switchPeekStatus.text()
            self.close()
        except:
            QMessageBox.critical(self, "错误", "配置文件写入失败", QMessageBox.Yes)

if __name__ == "__main__":
    if hasattr(Qt, 'AA_EnableHighDpiScaling'):
        QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)
    if hasattr(Qt, 'AA_UseHighDpiPixmaps'):
        QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps, True)

    application = QApplication(sys.argv)
    main = MainWindow()
    
    main.setWindowIcon(QIcon('./src/icon.ico'))
    main.setWindowFlags(Qt.WindowMinimizeButtonHint | Qt.WindowCloseButtonHint)
    main.setFixedSize(main.width(), main.height())
    
    for pid in psutil.pids():
        try:
            if psutil.Process(pid).name() == "frpc.exe":
                main.runFrpButton.setEnabled(False)
                main.forceStopFrpButton.setEnabled(True)
                break
        except:
            continue

    main.show()
    sys.exit(application.exec_())