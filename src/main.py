#  Copyright 2026 anominy
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.

import sys

# noinspection PyUnusedImports
import resources

from PySide6.QtWidgets import QApplication, QMainWindow, QWidget
from PySide6.QtGui import QIcon

_APP_NAME = 'Remedy'
_RES_ICON = ':/icons/icon.ico'

def _main():
    app = QApplication(sys.argv)

    window = QMainWindow()
    window.setWindowTitle(_APP_NAME)
    window.setWindowIcon(QIcon(_RES_ICON))

    root_widget = QWidget()
    window.setCentralWidget(root_widget)

    window.show()
    sys.exit(app.exec())


if __name__ == '__main__':
    _main()
