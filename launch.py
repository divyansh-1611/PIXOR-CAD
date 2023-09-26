#!/usr/bin/env python

import sys
from PyQt5.QtWidgets import QApplication

from cad.application import Application


if __name__ == '__main__':
    app = QApplication(sys.argv)
    workspace = Application()
    workspace.show()
    sys.exit(app.exec_())
