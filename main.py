import sys

from PySide6.QtWidgets import QApplication

from src.ui import QuickBoardWindow


def main() -> None:
    app = QApplication(sys.argv)

    window = QuickBoardWindow()

    # Show the full panel on startup for a safer first MVP experience.
    window.show_panel()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()