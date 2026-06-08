from functools import partial
from typing import Any

from PySide6.QtCore import QObject, QEvent, Qt, Signal, QTimer
from PySide6.QtWidgets import (
    QApplication,
    QComboBox,
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
from src.settings import load_settings, save_settings
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

BACKGROUND_COLORS = [
    ("Wood", "#8B5E34"),
    ("Dark wood", "#5C4033"),
    ("Warm sand", "#D6B98C"),
    ("Cream", "#F3E8D2"),
    ("Soft green", "#8FAF8F"),
    ("Slate", "#475569"),
    ("Charcoal", "#1F2937"),
    ("White", "#F9FAFB"),
]

TRANSLATIONS = {
    "en": {
        "app_title": "quick-board",
        "subtitle": "Your quick copy board",
        "empty_state": "No cards yet.\n\nClick the button below to add your first quick note.",
        "add_card": "+ Add new card",
        "language": "Language",
        "background": "Background",
        "quit": "Quit",
        "title": "Title",
        "content": "Content",
        "color": "Color",
        "short_title": "Short title",
        "content_placeholder": "Content to copy later",
        "cancel": "Cancel",
        "save": "Save",
        "missing_title": "Missing information",
        "missing_message": "Title and content are required.",
        "limit_title": "Limit reached",
        "limit_message": "You can only save up to {max_slots} cards.",
        "delete_title": "Delete card",
        "delete_message": "Are you sure you want to delete this card?",
        "copy_tooltip": "Copy content",
        "edit_tooltip": "Edit card",
        "delete_tooltip": "Delete card",
        "quit_title": "Quit quick-board",
        "quit_message": "Do you want to close quick-board completely?",
        "hotkey_unavailable": "Hotkey unavailable",
        "hotkey_error": "The global hotkey could not be registered.",
        "copied": "Copied",
    },
    "es": {
        "app_title": "quick-board",
        "subtitle": "Tu tablero rápido para copiar",
        "empty_state": "Todavía no hay tarjetas.\n\nHacé click abajo para agregar tu primera nota rápida.",
        "add_card": "+ Agregar tarjeta",
        "language": "Idioma",
        "background": "Fondo",
        "quit": "Salir",
        "title": "Título",
        "content": "Contenido",
        "color": "Color",
        "short_title": "Título corto",
        "content_placeholder": "Contenido para copiar después",
        "cancel": "Cancelar",
        "save": "Guardar",
        "missing_title": "Falta información",
        "missing_message": "El título y el contenido son obligatorios.",
        "limit_title": "Límite alcanzado",
        "limit_message": "Solo podés guardar hasta {max_slots} tarjetas.",
        "delete_title": "Borrar tarjeta",
        "delete_message": "¿Seguro que querés borrar esta tarjeta?",
        "copy_tooltip": "Copiar",
        "edit_tooltip": "Editar tarjeta",
        "delete_tooltip": "Borrar tarjeta",
        "quit_title": "Cerrar quick-board",
        "quit_message": "¿Querés cerrar quick-board definitivamente?",
        "hotkey_unavailable": "Atajo no disponible",
        "hotkey_error": "No se pudo registrar el atajo global.",
        "copied": "Copiado",
    },
}


class HotkeySignals(QObject):
    toggle_requested = Signal()


class SlotDialog(QDialog):
    def __init__(
        self,
        parent: QWidget | None = None,
        slot: dict[str, Any] | None = None,
        language: str = "es",
    ) -> None:
        super().__init__(parent)

        self.language = language
        self.selected_color = CARD_COLORS[0]

        self.setWindowTitle(self.translate("title"))
        self.setModal(True)
        self.resize(420, 340)

        self.title_input = QLineEdit()
        self.title_input.setPlaceholderText(self.translate("short_title"))

        self.content_input = QTextEdit()
        self.content_input.setPlaceholderText(self.translate("content_placeholder"))

        self.color_buttons: list[QPushButton] = []

        if slot:
            self.title_input.setText(slot.get("title", ""))
            self.content_input.setPlainText(slot.get("content", ""))
            self.selected_color = slot.get("color", CARD_COLORS[0])

        main_layout = QVBoxLayout()
        main_layout.setSpacing(12)

        title_label = QLabel(self.translate("title"))
        content_label = QLabel(self.translate("content"))
        color_label = QLabel(self.translate("color"))

        color_layout = QHBoxLayout()
        color_layout.setSpacing(8)

        for color in CARD_COLORS:
            button = QPushButton()
            button.setFocusPolicy(Qt.NoFocus)
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

        cancel_button = QPushButton(self.translate("cancel"))
        cancel_button.setFocusPolicy(Qt.NoFocus)
        cancel_button.clicked.connect(self.reject)

        save_button = QPushButton(self.translate("save"))
        save_button.setFocusPolicy(Qt.NoFocus)
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

    def translate(self, key: str) -> str:
        return TRANSLATIONS.get(self.language, TRANSLATIONS["es"]).get(key, key)

    def select_color(self, color: str) -> None:
        self.selected_color = color

    def validate_and_accept(self) -> None:
        title = self.title_input.text().strip()
        content = self.content_input.toPlainText().strip()

        if not title or not content:
            QMessageBox.warning(
                self,
                self.translate("missing_title"),
                self.translate("missing_message"),
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
        self.settings = load_settings()
        self.language = self.settings.get("language", "es")
        self.background_color = self.settings.get("background_color", "#8B5E34")
        self.is_panel_visible = False

        self.setWindowTitle("quick-board")
        self.setWindowFlags(
            Qt.WindowStaysOnTopHint
            | Qt.FramelessWindowHint
            | Qt.Tool
        )

        self.screen_geometry = self.screen().availableGeometry()
        self.panel_width = max(380, self.screen_geometry.width() // 4)
        self.panel_height = self.screen_geometry.height()

        self.visible_x = self.screen_geometry.right() - self.panel_width + 1
        self.hidden_tab_width = 42
        self.hidden_x = self.screen_geometry.right() - self.hidden_tab_width + 1
        self.panel_y = self.screen_geometry.top()

        self.resize(self.panel_width, self.panel_height)

        self.hotkey_signals = HotkeySignals()
        self.hotkey_signals.toggle_requested.connect(self.toggle_panel)

        self.root_widget = QWidget()
        self.root_layout = QHBoxLayout()
        self.root_layout.setContentsMargins(0, 0, 0, 0)
        self.root_layout.setSpacing(0)

        self.tab_button = QPushButton("QB")
        self.tab_button.setFocusPolicy(Qt.NoFocus)
        self.tab_button.setFixedWidth(self.hidden_tab_width)
        self.tab_button.setCursor(Qt.PointingHandCursor)
        self.tab_button.clicked.connect(self.toggle_panel)

        self.board_widget = QWidget()
        self.board_layout = QVBoxLayout()
        self.board_layout.setContentsMargins(16, 16, 16, 16)
        self.board_layout.setSpacing(12)
        self.board_widget.setLayout(self.board_layout)

        self.root_layout.addWidget(self.tab_button)
        self.root_layout.addWidget(self.board_widget)

        self.root_widget.setLayout(self.root_layout)
        self.setCentralWidget(self.root_widget)

        app = QApplication.instance()

        if app:
            app.installEventFilter(self)

        self.hotkey_manager = GlobalHotkeyManager(self.request_toggle_from_hotkey)
        self.register_hotkey_safely()

        self.apply_base_styles()
        self.render_board()

    def translate(self, key: str) -> str:
        return TRANSLATIONS.get(self.language, TRANSLATIONS["es"]).get(key, key)

    def eventFilter(self, watched: QObject, event: QEvent) -> bool:
        if event.type() in {QEvent.KeyPress, QEvent.KeyRelease}:
            if self.is_internal_hotkey_event(event):
                return True

        return super().eventFilter(watched, event)

    def is_internal_hotkey_event(self, event: QEvent) -> bool:
        key = event.key()
        modifiers = event.modifiers()

        is_space = key == Qt.Key_Space
        has_ctrl = bool(modifiers & Qt.ControlModifier)
        has_shift = bool(modifiers & Qt.ShiftModifier)
        has_alt = bool(modifiers & Qt.AltModifier)

        is_ctrl_shift_space = is_space and has_ctrl and has_shift
        is_ctrl_alt_space = is_space and has_ctrl and has_alt

        return is_ctrl_shift_space or is_ctrl_alt_space

    def request_toggle_from_hotkey(self) -> None:
        self.hotkey_signals.toggle_requested.emit()

    def register_hotkey_safely(self) -> None:
        try:
            self.hotkey_manager.register()
        except Exception as error:
            QTimer.singleShot(
                500,
                lambda: QMessageBox.warning(
                    self,
                    self.translate("hotkey_unavailable"),
                    f"{self.translate('hotkey_error')}\n\n{error}",
                ),
            )

    def apply_base_styles(self) -> None:
        self.tab_button.setStyleSheet(
            """
            QPushButton {
                background-color: #111827;
                color: white;
                border: none;
                font-size: 12px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #374151;
            }
            """
        )

        self.board_widget.setStyleSheet(
            f"""
            QWidget {{
                background-color: {self.background_color};
                color: #111827;
                font-family: Segoe UI;
                font-size: 13px;
            }}
            """
        )

    def persist_settings(self) -> None:
        self.settings["language"] = self.language
        self.settings["background_color"] = self.background_color
        save_settings(self.settings)

    def show_hidden(self) -> None:
        self.resize(self.panel_width, self.panel_height)
        self.move(self.hidden_x, self.panel_y)
        self.board_widget.hide()
        self.tab_button.setText("QB")
        self.is_panel_visible = False
        self.show()

    def show_panel(self) -> None:
        self.resize(self.panel_width, self.panel_height)
        self.move(self.visible_x, self.panel_y)
        self.board_widget.show()
        self.tab_button.setText("×")
        self.is_panel_visible = True
        self.show()
        self.raise_()

    def hide_panel(self) -> None:
        self.resize(self.panel_width, self.panel_height)
        self.move(self.hidden_x, self.panel_y)
        self.board_widget.hide()
        self.tab_button.setText("QB")
        self.is_panel_visible = False
        self.show()

    def toggle_panel(self) -> None:
        if self.is_panel_visible:
            self.hide_panel()
        else:
            self.show_panel()

    def render_board(self) -> None:
        self.clear_layout(self.board_layout)
        self.apply_base_styles()

        header_card = QFrame()
        header_card.setObjectName("headerCard")
        header_card.setStyleSheet(
            """
            QFrame#headerCard {
                background-color: rgba(255, 255, 255, 0.84);
                border-radius: 16px;
                border: 1px solid rgba(255, 255, 255, 0.55);
            }
            """
        )

        header_layout = QVBoxLayout()
        header_layout.setContentsMargins(14, 14, 14, 14)
        header_layout.setSpacing(10)

        top_row = QHBoxLayout()

        title_group = QVBoxLayout()
        title_group.setSpacing(2)

        header = QLabel(self.translate("app_title"))
        header.setStyleSheet(
            """
            QLabel {
                font-size: 22px;
                font-weight: bold;
                color: #111827;
                background-color: transparent;
            }
            """
        )

        subtitle = QLabel(self.translate("subtitle"))
        subtitle.setStyleSheet(
            """
            QLabel {
                color: #6B7280;
                font-size: 12px;
                background-color: transparent;
            }
            """
        )

        title_group.addWidget(header)
        title_group.addWidget(subtitle)

        quit_button = QPushButton("⏻")
        quit_button.setFocusPolicy(Qt.NoFocus)
        quit_button.setFixedSize(34, 34)
        quit_button.setCursor(Qt.PointingHandCursor)
        quit_button.setToolTip(self.translate("quit"))
        quit_button.clicked.connect(self.quit_application)
        quit_button.setStyleSheet(
            """
            QPushButton {
                background-color: #FEE2E2;
                color: #991B1B;
                border: none;
                border-radius: 17px;
                font-size: 16px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #FECACA;
            }
            """
        )

        top_row.addLayout(title_group)
        top_row.addStretch()
        top_row.addWidget(quit_button)

        controls_layout = QVBoxLayout()
        controls_layout.setSpacing(8)

        language_row = QHBoxLayout()
        language_label = QLabel(self.translate("language"))
        language_label.setStyleSheet("background-color: transparent; color: #374151;")

        self.language_combo = QComboBox()
        self.language_combo.setFocusPolicy(Qt.NoFocus)
        self.language_combo.addItem("Español", "es")
        self.language_combo.addItem("English", "en")
        self.language_combo.setCurrentIndex(0 if self.language == "es" else 1)
        self.language_combo.currentIndexChanged.connect(self.change_language)
        self.language_combo.setStyleSheet(
            """
            QComboBox {
                background-color: #FFFFFF;
                border: 1px solid #D1D5DB;
                border-radius: 8px;
                padding: 5px 8px;
            }
            """
        )

        language_row.addWidget(language_label)
        language_row.addStretch()
        language_row.addWidget(self.language_combo)

        background_label = QLabel(self.translate("background"))
        background_label.setStyleSheet("background-color: transparent; color: #374151;")

        background_buttons_layout = QHBoxLayout()
        background_buttons_layout.setSpacing(6)

        for color_name, color_value in BACKGROUND_COLORS:
            button = QPushButton()
            button.setFocusPolicy(Qt.NoFocus)
            button.setFixedSize(24, 24)
            button.setCursor(Qt.PointingHandCursor)
            button.setToolTip(color_name)
            button.clicked.connect(partial(self.change_background_color, color_value))
            border_color = "#111827" if color_value == self.background_color else "#FFFFFF"
            button.setStyleSheet(
                f"""
                QPushButton {{
                    background-color: {color_value};
                    border-radius: 12px;
                    border: 2px solid {border_color};
                }}
                QPushButton:hover {{
                    border: 2px solid #111827;
                }}
                """
            )
            background_buttons_layout.addWidget(button)

        controls_layout.addLayout(language_row)
        controls_layout.addWidget(background_label)
        controls_layout.addLayout(background_buttons_layout)

        header_layout.addLayout(top_row)
        header_layout.addLayout(controls_layout)
        header_card.setLayout(header_layout)

        self.board_layout.addWidget(header_card)

        if not self.slots:
            empty_state = QLabel(self.translate("empty_state"))
            empty_state.setAlignment(Qt.AlignCenter)
            empty_state.setStyleSheet(
                """
                QLabel {
                    color: #4B5563;
                    background-color: rgba(255, 255, 255, 0.86);
                    border: 1px dashed rgba(17, 24, 39, 0.25);
                    border-radius: 14px;
                    padding: 24px;
                }
                """
            )
            self.board_layout.addWidget(empty_state)

        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setFrameShape(QFrame.NoFrame)
        scroll_area.setStyleSheet(
            """
            QScrollArea {
                background-color: transparent;
                border: none;
            }
            QScrollBar:vertical {
                background-color: rgba(255, 255, 255, 0.25);
                width: 8px;
                border-radius: 4px;
            }
            QScrollBar::handle:vertical {
                background-color: rgba(17, 24, 39, 0.35);
                border-radius: 4px;
            }
            """
        )

        cards_container = QWidget()
        cards_container.setStyleSheet("background-color: transparent;")

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
            add_button = QPushButton(self.translate("add_card"))
            add_button.setFocusPolicy(Qt.NoFocus)
            add_button.setCursor(Qt.PointingHandCursor)
            add_button.clicked.connect(self.add_slot)
            add_button.setStyleSheet(
                """
                QPushButton {
                    background-color: #2563EB;
                    color: white;
                    border: none;
                    padding: 11px;
                    border-radius: 12px;
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
                    border-radius: 16px;
                    border: 1px solid rgba(17, 24, 39, 0.14);
                }}
                """
            )

            layout = QVBoxLayout()
            layout.setContentsMargins(12, 10, 12, 12)
            layout.setSpacing(8)

            title_row = QHBoxLayout()
            title_row.setSpacing(8)

            title = QLabel(slot.get("title", "Untitled"))
            title.setWordWrap(True)
            title.setStyleSheet(
                """
                QLabel {
                    font-size: 12px;
                    font-weight: 600;
                    color: rgba(17, 24, 39, 0.62);
                    background-color: transparent;
                }
                """
            )

            secondary_actions_layout = QHBoxLayout()
            secondary_actions_layout.setSpacing(5)

            edit_button = self.create_icon_button(
                "✏️",
                self.translate("edit_tooltip"),
                partial(self.edit_slot, index),
            )

            delete_button = self.create_icon_button(
                "🗑️",
                self.translate("delete_tooltip"),
                partial(self.delete_slot, index),
            )

            secondary_actions_layout.addWidget(edit_button)
            secondary_actions_layout.addWidget(delete_button)

            title_row.addWidget(title)
            title_row.addStretch()
            title_row.addLayout(secondary_actions_layout)

            content_box = QFrame()
            content_box.setObjectName("contentBox")
            content_box.setStyleSheet(
                """
                QFrame#contentBox {
                    background-color: rgba(255, 255, 255, 0.88);
                    border-radius: 12px;
                    border: 1px solid rgba(17, 24, 39, 0.10);
                }
                """
            )

            content_layout = QVBoxLayout()
            content_layout.setContentsMargins(12, 12, 12, 12)
            content_layout.setSpacing(10)

            content = QLabel(slot.get("content", ""))
            content.setTextFormat(Qt.PlainText)
            content.setWordWrap(True)
            content.setTextInteractionFlags(Qt.TextSelectableByMouse)
            content.setStyleSheet(
                """
                QLabel {
                    color: #111827;
                    font-size: 14px;
                    font-weight: 500;
                    line-height: 150%;
                    background-color: transparent;
                }
                """
            )

            copy_row = QHBoxLayout()
            copy_row.setSpacing(0)

            copy_button = QPushButton(f"📋  {self.translate('copy_tooltip')}")
            copy_button.setFocusPolicy(Qt.NoFocus)
            copy_button.setCursor(Qt.PointingHandCursor)
            copy_button.clicked.connect(partial(self.copy_slot_content, index))
            copy_button.setStyleSheet(
                """
                QPushButton {
                    background-color: #16A34A;
                    color: #FFFFFF;
                    border: none;
                    border-radius: 10px;
                    padding: 7px 12px;
                    font-size: 12px;
                    font-weight: 600;
                }
                QPushButton:hover {
                    background-color: #374151;
                }
                """
            )

            copy_row.addWidget(copy_button)
            copy_row.addStretch()

            content_layout.addWidget(content)

            content_box.setLayout(content_layout)

            layout.addLayout(title_row)
            layout.addWidget(content_box)
            layout.addLayout(copy_row)

            card.setLayout(layout)

            return card

    def create_icon_button(
            self,
            text: str,
            tooltip: str,
            callback,
        ) -> QPushButton:
            button = QPushButton(text)
            button.setFocusPolicy(Qt.NoFocus)
            button.setFixedSize(30, 30)
            button.setCursor(Qt.PointingHandCursor)
            button.setToolTip(tooltip)
            button.clicked.connect(callback)
            button.setStyleSheet(
                """
                QPushButton {
                    background-color: rgba(255, 255, 255, 0.82);
                    color: #111827;
                    border: 1px solid rgba(17, 24, 39, 0.10);
                    border-radius: 15px;
                    font-size: 14px;
                }
                QPushButton:hover {
                    background-color: #FFFFFF;
                    border: 1px solid rgba(17, 24, 39, 0.24);
                }
                """
            )
            return button

    def change_language(self) -> None:
        selected_language = self.language_combo.currentData()

        if selected_language not in {"es", "en"}:
            return

        self.language = selected_language
        self.persist_settings()
        self.render_board()

    def change_background_color(self, color: str) -> None:
        self.background_color = color
        self.persist_settings()
        self.render_board()

    def add_slot(self) -> None:
        if len(self.slots) >= MAX_SLOTS:
            QMessageBox.information(
                self,
                self.translate("limit_title"),
                self.translate("limit_message").format(max_slots=MAX_SLOTS),
            )
            return

        dialog = SlotDialog(self, language=self.language)

        if dialog.exec() == QDialog.Accepted:
            self.slots.append(dialog.get_slot_data())
            save_slots(self.slots)
            self.render_board()

    def edit_slot(self, index: int) -> None:
        if index < 0 or index >= len(self.slots):
            return

        dialog = SlotDialog(self, self.slots[index], language=self.language)

        if dialog.exec() == QDialog.Accepted:
            self.slots[index] = dialog.get_slot_data()
            save_slots(self.slots)
            self.render_board()

    def delete_slot(self, index: int) -> None:
        if index < 0 or index >= len(self.slots):
            return

        confirm = QMessageBox.question(
            self,
            self.translate("delete_title"),
            self.translate("delete_message"),
        )

        if confirm == QMessageBox.Yes:
            self.slots.pop(index)
            save_slots(self.slots)
            self.render_board()

    def copy_slot_content(self, index: int) -> None:
        if index < 0 or index >= len(self.slots):
            return

        copy_to_clipboard(self.slots[index].get("content", ""))

    def quit_application(self) -> None:
        confirm = QMessageBox.question(
            self,
            self.translate("quit_title"),
            self.translate("quit_message"),
        )

        if confirm == QMessageBox.Yes:
            QApplication.quit()

    def closeEvent(self, event) -> None:
        app = QApplication.instance()

        if app:
            app.removeEventFilter(self)

        try:
            self.hotkey_manager.unregister()
        finally:
            event.accept()

    def clear_layout(self, layout) -> None:
        while layout.count():
            item = layout.takeAt(0)

            widget = item.widget()

            if widget:
                widget.deleteLater()
                continue

            child_layout = item.layout()

            if child_layout:
                self.clear_layout(child_layout)