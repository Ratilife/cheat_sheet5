from PySide6.QtCore import QObject, Signal
from PySide6.QtWidgets import QTabWidget, QWidget, QVBoxLayout, QTreeView, QApplication

from operation.file_operations import FileOperations


class DynamicTabManager(QObject):
    # TODO 🚧 В разработке: 08.08.2025
        # 🏆task: Создание боковой панели;
        # 🏆task: Открыть боковую панель из стартовой панели;
    # Объявление сигнала
    tab_created = Signal(str, QTreeView)  # Сигнал передает имя вкладки и дерево
    def __init__(self, parent: QWidget = None):
        # TODO 🚧 В разработке: 08.08.2025
        super().__init__(parent)
        self.tab_widget = QTabWidget()
        self.trees = {}  # Словарь для хранения деревьев по именам вкладок

        # 🔽Добавляем методы 17.09.2025🔽
        self.tab_widgets = {}  # {"side_panel": tab_widget1, "editor": tab_widget2}
        self.widget_priorities = []
        # 🔽Конец добавления методов 17.09.2025🔽
        self.file_operations = FileOperations()
    def create_tabs(self, tab_data: dict) -> QTabWidget:
        """Создает вкладки и деревья на основе переданного словаря.
        Ключи словаря используются как имена вкладок.

        Args:
            tab_data: Словарь, где ключи - имена вкладок, а значения - связанные данные

        Returns:
            QTabWidget: Виджет с созданными вкладками

        Raises:
            ValueError: Если словарь пуст
        """
        if not tab_data:
            raise ValueError("Словарь с данными вкладок не может быть пустым!")

        for tab_name in tab_data.keys():
            self._add_tab(tab_name)
        return self.tab_widget

    def _add_tab(self, name: str) -> QTreeView:
        """Добавляет одну вкладку с деревом."""
        # TODO 🚧 В разработке: 08.08.2025
        tree = QTreeView()
        tree.setHeaderHidden(True)  # Пример настройки

        tab_content = QWidget()
        layout = QVBoxLayout()
        layout.addWidget(tree)
        tab_content.setLayout(layout)

        self.tab_widget.addTab(tab_content, name)
        self.trees[name] = tree
        self.tab_created.emit(name, tree)  # Уведомляем о создании

        return tree


    def _update_tree(self, tree: QTreeView, path: str):
        """Обновляет дерево при изменении файлов."""
        # TODO 🚧 В разработке: 08.08.2025
        # Логика обновления дерева...
        pass

    # 🔽Добавляем методы 17.09.2025🔽
    def register_tab_widget(self, widget_name: str, tab_widget: QTabWidget, priority: int = 0):
        """Регистрирует tab_widget с приоритетом"""
        self.tab_widgets[widget_name] = tab_widget
        self.widget_priorities = sorted(
            self.tab_widgets.keys(),
            key=lambda x: priority,
            reverse=True
        )

    def get_active_tab_info_old(self) -> dict | None:
        """Возвращает информацию об активной вкладке из любого окна"""
        for widget_name in self.widget_priorities:
            tab_widget = self.tab_widgets[widget_name]
            if tab_widget and tab_widget.count() > 0:
                current_index = tab_widget.currentIndex()
                if current_index >= 0:
                    return {
                        'widget_name': widget_name,
                        'tab_name': tab_widget.tabText(current_index),
                        'tab_widget': tab_widget
                    }
        return None

    def get_active_tab_info(self) -> dict | None:
        """Возвращает информацию об активной вкладке окна, с которым работает пользователь"""

        # 1. Получаем активное окно приложения
        active_window = QApplication.activeWindow()

        # 2. Если есть активное окно, ищем в нем tab_widget
        if active_window:
            # Ищем tab_widget, который принадлежит активному окну
            for widget_name, tab_widget in self.tab_widgets.items():
                if not tab_widget or not tab_widget.isVisible():
                    continue

                # Проверяем, находится ли tab_widget в активном окне
                tab_widget_window = tab_widget.window()
                if (tab_widget_window == active_window and
                        tab_widget.count() > 0):

                    current_index = tab_widget.currentIndex()
                    if current_index >= 0:
                        return {
                            'widget_name': widget_name,
                            'tab_name': tab_widget.tabText(current_index),
                            'tab_widget': tab_widget,
                            'window': tab_widget_window
                        }

        # 3. Если активного окна нет или в нем не нашли tab_widget,
        # используем окно, которое было зарегистрировано последним
        for widget_name in reversed(self.widget_priorities):
            tab_widget = self.tab_widgets.get(widget_name)
            if (tab_widget and
                    tab_widget.isVisible() and
                    tab_widget.count() > 0):

                current_index = tab_widget.currentIndex()
                if current_index >= 0:
                    return {
                        'widget_name': widget_name,
                        'tab_name': tab_widget.tabText(current_index),
                        'tab_widget': tab_widget,
                        'window': tab_widget.window()
                    }
        return None

    def launch_download_for_active_tab(self):
        """Загружает файлы для активной вкладки"""
        # TODO 29.09.2025 тут начинается проблема.
        tab_info = self.get_active_tab_info()
        if not tab_info:
            print("Нет активных вкладок")
            return None

        files = self.file_operations.load_st_md_files(tab_info['tab_name'])
        return tab_info['tab_name'], files

    # 🔽Конец добавления методов 17.09.2025🔽

    def get_active_tab_info_test(self) -> dict | None:
        """Возвращает информацию об активной вкладке окна, с которым работает пользователь"""

        print("🚩🚩🚩=" * 60)
        print("🔍 DEBUG: get_active_tab_info() вызван")

        # Проверка 1: Сколько виджетов зарегистрировано?
        print(f"📊 Зарегистрировано виджетов: {len(self.tab_widgets)}")
        print(f"📋 Ключи виджетов: {list(self.tab_widgets.keys())}")
        print(f"📋 widget_priorities: {self.widget_priorities}")

        # Проверка 2: Детальная информация о каждом виджете
        for widget_name, tab_widget in self.tab_widgets.items():
            print(f"\n🔹 Виджет '{widget_name}':")
            print(f"   - tab_widget существует: {tab_widget is not None}")
            if tab_widget:
                print(f"   - isVisible(): {tab_widget.isVisible()}")
                print(f"   - count(): {tab_widget.count()}")
                print(f"   - currentIndex(): {tab_widget.currentIndex()}")
                print(f"   - window(): {tab_widget.window()}")
                print(
                    f"   - window().isVisible(): {tab_widget.window().isVisible() if tab_widget.window() else 'None'}")

        # 1. Получаем активное окно приложения
        active_window = QApplication.activeWindow()
        print(f"\n🪟 Активное окно: {active_window}")
        if active_window:
            print(f"   - Тип: {type(active_window)}")
            print(f"   - Заголовок: {active_window.windowTitle()}")
            print(f"   - isVisible(): {active_window.isVisible()}")

        # 2. Если есть активное окно, ищем в нем tab_widget
        if active_window:
            print("\n🔎 Ищем tab_widget в активном окне...")
            found_in_active = False
            for widget_name, tab_widget in self.tab_widgets.items():
                if not tab_widget or not tab_widget.isVisible():
                    print(f"   ❌ '{widget_name}': пропущен (tab_widget=None или не видим)")
                    continue

                tab_widget_window = tab_widget.window()
                print(f"   🔹 '{widget_name}':")
                print(f"      - tab_widget.window(): {tab_widget_window}")
                print(f"      - Окна совпадают: {tab_widget_window == active_window}")
                print(f"      - count(): {tab_widget.count()}")

                if (tab_widget_window == active_window and tab_widget.count() > 0):
                    current_index = tab_widget.currentIndex()
                    print(f"      - currentIndex(): {current_index}")
                    if current_index >= 0:
                        result = {
                            'widget_name': widget_name,
                            'tab_name': tab_widget.tabText(current_index),
                            'tab_widget': tab_widget,
                            'window': tab_widget_window
                        }
                        print(f"   ✅ НАЙДЕНО! Возвращаем: {result}")
                        print("=" * 60)
                        return result
                    else:
                        print(f"      ❌ currentIndex() < 0")
                else:
                    print(f"      ❌ Не подходит (окна не совпадают или count() == 0)")
            print("   ❌ Не найдено подходящего виджета в активном окне")

        # 3. Если активного окна нет или в нем не нашли tab_widget,
        # используем окно, которое было зарегистрировано последним
        print("\n🔎 Пробуем найти по приоритетам (fallback)...")
        for widget_name in reversed(self.widget_priorities):
            tab_widget = self.tab_widgets.get(widget_name)
            print(f"   🔹 Проверяем '{widget_name}':")
            if not tab_widget:
                print(f"      ❌ tab_widget = None")
                continue
            print(f"      - isVisible(): {tab_widget.isVisible()}")
            print(f"      - count(): {tab_widget.count()}")

            if (tab_widget and tab_widget.isVisible() and tab_widget.count() > 0):
                current_index = tab_widget.currentIndex()
                print(f"      - currentIndex(): {current_index}")
                if current_index >= 0:
                    result = {
                        'widget_name': widget_name,
                        'tab_name': tab_widget.tabText(current_index),
                        'tab_widget': tab_widget,
                        'window': tab_widget.window()
                    }
                    print(f"   ✅ НАЙДЕНО (fallback)! Возвращаем: {result}")
                    print("=" * 60)
                    return result
                else:
                    print(f"      ❌ currentIndex() < 0")
            else:
                print(f"      ❌ Не подходит")

        print("❌ НЕ НАЙДЕНО! Возвращаем None")
        print("=" * 60)
        return None