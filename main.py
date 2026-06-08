import sys

from PySide6.QtWidgets import QApplication

from src.ui import QuickBoardWindow


def main() -> None:
    app = QApplication(sys.argv)

    window = QuickBoardWindow()
    window.show_hidden()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()