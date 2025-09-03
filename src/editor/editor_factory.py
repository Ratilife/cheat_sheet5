# Фабрика редакторов

from pathlib import Path
from .st_editor import STEditor
from .markdown_editor import MarkdownEditor
from .plain_text_editor import PlainTextEditor


class EditorFactory:
    """Фабрика для создания редакторов based on расширения файла"""

    @staticmethod
    def create_editor(file_path: str, parent=None):
        extension = Path(file_path).suffix.lower()

        editor_registry = {
            '.st': STEditor,
            '.md': MarkdownEditor,
            # Можно добавить другие форматы
        }

        editor_class = editor_registry.get(extension, PlainTextEditor)
        return editor_class(parent)