
import json
from time import sleep 
from vm_auto_eq.app import async_manager 
from vm_auto_eq.ui import main_window

from PySide6.QtWidgets import QApplication
import sys


def main():
    manager = async_manager.AsyncManager()
    manager.start()
    
    app = QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(False)
    tray_app = main_window.TrayApplication(manager)

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
   
