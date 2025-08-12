from src.models.st_file_tree_model import STFileTreeModel
class TreeModelManager:
    """
      Фасад для работы с моделью дерева файлов. Инкапсулирует:
      - Добавление/удаление элементов
      - Парсинг файлов
      - Взаимодействие с DeleteManager
      """

    def __init__(self):
        # TODO 🚧 В разработке: 12.07.2025
        self.tree_model = STFileTreeModel()
