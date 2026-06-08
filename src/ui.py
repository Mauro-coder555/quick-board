from functools import partial
from typing import Any

from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QColor
from PySide6.QtWidgets import (
    QDialog,
    QFrame,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QScrollArea,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from src.clipboard import copy_to_clipboard
from src.hotkeys import GlobalHotkeyManager
from src.storage import MAX_SLOTS, load_slots, save_slots


CARD_COLORS = [
    "#FDE68A",
    "#BFDBFE",
    "#BBF7D0",
    "#FBCFE8",
    "#DDD6FE",
    "#FED7AA",
    "#A7F3D0",
    "#FECACA",
    "#CFFAFE",
    "#E9D5FF",
]


class SlotDialog(QDialog):
    def __init__(
        self,
        parent: QWidget | None = None,
        slot: dict[str, Any] | None = None,
    ) -> None:
        super().__init__(parent)

        self.setWindowTitle("Slot")
        self.setModal(True)
        self.resize(420, 320)

        self.title_input = QLineEdit()
        self.title_input.setPlaceholderText("Short title")

        self.content_input = QTextEdit()
        self.content_input.setPlaceholderText("Content to copy later")

        self.color_buttons: list[QPushButton] = []
        self.selected_color = CARD_COLORS[0]

        if slot:
            self.title_input.setText(slot.get("title", ""))
            self.content_input.setPlainText(slot.get("content", ""))
            self.selected_color = slot.get("color", CARD_COLORS[0])

        main_layout = QVBoxLayout()
        main_layout.setSpacing(12)

        title_label = QLabel("Title")
        content_label = QLabel("Content")
        color_label = QLabel("Color")

        color_layout = QHBoxLayout()
        color_layout.setSpacing(8)

        for color in CARD_COLORS:
            button = QPushButton()
            button.setFixedSize(28, 28)
            button.setCursor(Qt.PointingHandCursor)
            button.setStyleSheet(
                f"""
                QPushButton {{
                    background-color: {color};
                    border-radius: 14px;
                    border: 2px solid #ffffff;
                }}
                QPushButton:hover {{
                    border: 2px solid #111827;
                }}
                """
            )
            button.clicked.connect(partial(self.select_color, color))
            self.color_buttons.append(button)
            color_layout.addWidget(button)

        actions_layout = QHBoxLayout()
        actions_layout.addStretch()

        cancel_button = QPushButton("Cancel")
        cancel_button.clicked.connect(self.reject)

        save_button = QPushButton("Save")
        save_button.clicked.connect(self.validate_and_accept)
        save_button.setDefault(True)

        actions_layout.addWidget(cancel_button)
        actions_layout.addWidget(save_button)

        main_layout.addWidget(title_label)
        main_layout.addWidget(self.title_input)
        main_layout.addWidget(content_label)
        main_layout.addWidget(self.content_input)
        main_layout.addWidget(color_label)
        main_layout.addLayout(color_layout)
        main_layout.addStretch()
        main_layout.addLayout(actions_layout)

        self.setLayout(main_layout)

    def select_color(self, color: str) -> None:
        self.selected_color = color

    def validate_and_accept(self) -> None:
        title = self.title_input.text().strip()
        content = self.content_input.toPlainText().strip()

        if not title or not content:
            QMessageBox.warning(
                self,
                "Missing information",
                "Title and content are required.",
            )
            return

        self.accept()

    def get_slot_data(self) -> dict[str, str]:
        return {
            "title": self.title_input.text().strip(),
            "content": self.content_input.toPlainText().strip(),
            "color": self.selected_color,
        }


class QuickBoardWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()

        self.slots = load_slots()
        self.is_panel_visible = False

        self.setWindowTitle("quick-board")
        self.setWindowFlags(
            Qt.WindowStaysOnTopHint
            | Qt.FramelessWindowHint
            | Qt.Tool
        )

        self.screen_geometry = self.screen().availableGeometry()
        self.panel_width = max(320, self.screen_geometry.width() // 4)
        self.panel_height = self.screen_geometry.height()

        self.visible_x = self.screen_geometry.right() - self.panel_width + 1
        self.hidden_tab_width = 34
        self.hidden_x = self.screen_geometry.right() - self.hidden_tab_width + 1
        self.panel_y = self.screen_geometry.top()

        self.resize(self.panel_width, self.panel_height)

        self.root_widget = QWidget()
        self.root_layout = QHBoxLayout()
        self.root_layout.setContentsMargins(0, 0, 0, 0)
        self.root_layout.setSpacing(0)

        self.tab_button = QPushButton("‹")
        self.tab_button.setFixedWidth(self.hidden_tab_width)
        self.tab_button.setCursor(Qt.PointingHandCursor)
        self.tab_button.clicked.connect(self.toggle_panel)
        self.tab_button.setStyleSheet(
            """
            QPushButton {
                background-color: #111827;
                color: white;
                border: none;
                font-size: 24px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #374151;
            }
            """
        )

        self.board_widget = QWidget()
        self.board_layout = QVBoxLayout()
        self.board_layout.setContentsMargins(16, 16, 16, 16)
        self.board_layout.setSpacing(12)

        self.board_widget.setLayout(self.board_layout)
        self.board_widget.setStyleSheet(
            """
            QWidget {
                background-color: #F9FAFB;
                color: #111827;
                font-family: Segoe UI;
                font-size: 13px;
            }
            """
        )

        self.root_layout.addWidget(self.tab_button)
        self.root_layout.addWidget(self.board_widget)

        self.root_widget.setLayout(self.root_layout)
        self.setCentralWidget(self.root_widget)

        self.hotkey_manager = GlobalHotkeyManager(self.toggle_panel)
        self.register_hotkey_safely()

        self.render_board()

    def register_hotkey_safely(self) -> None:
        try:
            self.hotkey_manager.register()
        except Exception as error:
            QTimer.singleShot(
                500,
                lambda: QMessageBox.warning(
                    self,
                    "Hotkey unavailable",
                    f"The global hotkey could not be registered.\n\n{error}",
                ),
            )

    def show_hidden(self) -> None:
        self.move(self.hidden_x, self.panel_y)
        self.show()
        self.is_panel_visible = False
        self.board_widget.hide()
        self.tab_button.setText("‹")

    def show_panel(self) -> None:
        self.move(self.visible_x, self.panel_y)
        self.board_widget.show()
        self.tab_button.setText("›")
        self.is_panel_visible = True
        self.raise_()
        self.activateWindow()

    def hide_panel(self) -> None:
        self.move(self.hidden_x, self.panel_y)
        self.board_widget.hide()
        self.tab_button.setText("‹")
        self.is_panel_visible = False

    def toggle_panel(self) -> None:
        if self.is_panel_visible:
            self.hide_panel()
        else:
            self.show_panel()

    def render_board(self) -> None:
        self.clear_layout(self.board_layout)

        header = QLabel("quick-board")
        header.setStyleSheet(
            """
            QLabel {
                font-size: 22px;
                font-weight: bold;
                color: #111827;
            }
            """
        )

        subtitle = QLabel("Your temporary copy board")
        subtitle.setStyleSheet(
            """
            QLabel {
                color: #6B7280;
                font-size: 12px;
            }
            """
        )

        self.board_layout.addWidget(header)
        self.board_layout.addWidget(subtitle)

        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setFrameShape(QFrame.NoFrame)

        cards_container = QWidget()
        cards_layout = QVBoxLayout()
        cards_layout.setContentsMargins(0, 8, 0, 8)
        cards_layout.setSpacing(12)

        for index, slot in enumerate(self.slots):
            card = self.create_slot_card(index, slot)
            cards_layout.addWidget(card)

        cards_layout.addStretch()
        cards_container.setLayout(cards_layout)
        scroll_area.setWidget(cards_container)

        self.board_layout.addWidget(scroll_area)

        if len(self.slots) < MAX_SLOTS:
            add_button = QPushButton("+ Add new card")
            add_button.setCursor(Qt.PointingHandCursor)
            add_button.clicked.connect(self.add_slot)
            add_button.setStyleSheet(
                """
                QPushButton {
                    background-color: #2563EB;
                    color: white;
                    border: none;
                    padding: 10px;
                    border-radius: 8px;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background-color: #1D4ED8;
                }
                """
            )
            self.board_layout.addWidget(add_button)

    def create_slot_card(self, index: int, slot: dict[str, Any]) -> QFrame:
        card = QFrame()
        card.setObjectName("slotCard")
        card.setStyleSheet(
            f"""
            QFrame#slotCard {{
                background-color: {slot.get("color", "#FDE68A")};
                border-radius: 12px;
                border: 1px solid rgba(17, 24, 39, 0.12);
            }}
            """
        )

        layout = QVBoxLayout()
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(8)

        title = QLabel(slot.get("title", "Untitled"))
        title.setWordWrap(True)
        title.setStyleSheet(
            """
            QLabel {
                font-size: 15px;
                font-weight: bold;
                color: #111827;
            }
            """
        )

        content = QLabel(slot.get("content", ""))
        content.setWordWrap(True)
        content.setTextInteractionFlags(Qt.TextSelectableByMouse)
        content.setStyleSheet(
            """
            QLabel {
                color: #1F2937;
                line-height: 140%;
            }
            """
        )

        actions_layout = QHBoxLayout()
        actions_layout.setSpacing(6)

        copy_button = QPushButton("Copy")
        copy_button.clicked.connect(partial(self.copy_slot_content, index))

        edit_button = QPushButton("Edit")
        edit_button.clicked.connect(partial(self.edit_slot, index))

        delete_button = QPushButton("Delete")
        delete_button.clicked.connect(partial(self.delete_slot, index))

        for button in [copy_button, edit_button, delete_button]:
            button.setCursor(Qt.PointingHandCursor)
            button.setStyleSheet(
                """
                QPushButton {
                    background-color: rgba(255, 255, 255, 0.7);
                    border: none;
                    padding: 6px 8px;
                    border-radius: 6px;
                    color: #111827;
                }
                QPushButton:hover {
                    background-color: white;
                }
                """
            )

        actions_layout.addWidget(copy_button)
        actions_layout.addWidget(edit_button)
        actions_layout.addWidget(delete_button)
        actions_layout.addStretch()

        layout.addWidget(title)
        layout.addWidget(content)
        layout.addLayout(actions_layout)

        card.setLayout(layout)

        return card

    def add_slot(self) -> None:
        if len(self.slots) >= MAX_SLOTS:
            QMessageBox.information(
                self,
                "Limit reached",
                f"You can only save up to {MAX_SLOTS} cards.",
            )
            return

        dialog = SlotDialog(self)

        if dialog.exec() == QDialog.Accepted:
            self.slots.append(dialog.get_slot_data())
            save_slots(self.slots)
            self.render_board()

    def edit_slot(self, index: int) -> None:
        if index < 0 or index >= len(self.slots):
            return

        dialog = SlotDialog(self, self.slots[index])

        if dialog.exec() == QDialog.Accepted:
            self.slots[index] = dialog.get_slot_data()
            save_slots(self.slots)
            self.render_board()

    def delete_slot(self, index: int) -> None:
        if index < 0 or index >= len(self.slots):
            return

        confirm = QMessageBox.question(
            self,
            "Delete card",
            "Are you sure you want to delete this card?",
        )

        if confirm == QMessageBox.Yes:
            self.slots.pop(index)
            save_slots(self.slots)
            self.render_board()

    def copy_slot_content(self, index: int) -> None:
        if index < 0 or index >= len(self.slots):
            return

        copy_to_clipboard(self.slots[index].get("content", ""))

    def closeEvent(self, event) -> None:
        try:
            self.hotkey_manager.unregister()
        finally:
            event.accept()

    def clear_layout(self, layout: QVBoxLayout) -> None:
        while layout.count():
            item = layout.takeAt(0)

            widget = item.widget()

            if widget:
                widget.deleteLater()
                continue

            child_layout = item.layout()

            if child_layout:
                self.clear_layout(child_layout)