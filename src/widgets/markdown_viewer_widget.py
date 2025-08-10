from PySide6.QtWidgets import QWidget,  QVBoxLayout,QRadioButton
class MarkdownViewer(QWidget):
    """Класс для отображения MD файлов в двух режимах: текст и markdown"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent
        self._init_ui()
        self._current_mode = 'markdown'
        self.highlighter = None  # Ссылка на экземпляр подсветки синтаксиса

    def _init_ui(self):
        """Инициализация интерфейса просмотрщика MD"""
        # TODO 🚧 В разработке: 10.08.2025
        self.layout = QVBoxLayout(self)              # Основной вертикальный макет
        self.layout.setContentsMargins(0, 0, 0, 0)   # Убираем отступы по краям

        # Панель переключения режимов
        self.mode_panel = QWidget()
        mode_layout = QHBoxLayout(self.mode_panel)
        mode_layout.setSpacing(5)                    # Расстояние между элементами

        # Группа для переключателей (радио-кнопок)
        self.mode_group = QButtonGroup(self)

        # Кнопка для текстового режима
        self.text_mode_btn = QRadioButton("Текст")

        # Кнопка для markdown режима
        self.markdown_mode_btn = QRadioButton("Markdown")
        self.markdown_mode_btn.setChecked(True)  # По умолчанию выбран

        # Добавление кнопок в группу
        self.mode_group.addButton(self.text_mode_btn)
        self.mode_group.addButton(self.markdown_mode_btn)
        self.mode_group.buttonClicked.connect(self._change_mode)

        # Добавление кнопок на панель
        mode_layout.addWidget(self.text_mode_btn)
        mode_layout.addWidget(self.markdown_mode_btn)
        mode_layout.addStretch()

        # Текстовый редактор для редактирования Markdown
        self.text_editor = QTextEdit()
        self.text_editor.setAcceptRichText(False)
        # Инициализация подсветки синтаксиса для текстового редактора
        self.highlighter = MarkdownHighlighter(self.text_editor.document())

        # Редактор для просмотра HTML (рендер Markdown)
        self.markdown_editor = QTextEdit()
        self.markdown_editor.setReadOnly(True)   #?
        self.markdown_editor.setVisible(True)    #?
        self.text_editor.setVisible(False)       #?

        # Добавление виджетов на основной layout
        self.layout.addWidget(self.mode_panel)
        self.layout.addWidget(self.text_editor)
        self.layout.addWidget(self.markdown_editor)

    def _change_mode(self):
        """Переключение между режимами просмотра"""
        # TODO 🚧 В разработке: 10.08.2025
        pass