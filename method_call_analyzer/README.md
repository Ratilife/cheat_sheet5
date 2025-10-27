# Method Call Analyzer (Python)

Инструмент анализирует Python-проект:
- находит, где используется указанный метод класса;
- строит граф вызовов методов, начиная с этого метода;
- сохраняет результаты в `.txt` и `.png`.

## Установка

```bash
python3 -m venv .venv && source .venv/bin/activate
python3 -m pip install -U pip
python3 -m pip install -r requirements.txt
```

## Запуск

```bash
python3 method_call_analyzer.py \
  --project-root "/path/to/your/project" \
  --target "ClassName.method_name" \
  --output-dir "./analysis_output" \
  --max-depth 5
```

- `--project-root`: корень проекта, в котором искать `.py` файлы
- `--target`: метод, от которого строим граф; формат: `ClassName.method`, либо просто `method` (менее точно). Также поддерживается `module.path:ClassName.method` для уточнения
- `--output-dir`: каталог для результатов
- `--max-depth`: максимальная глубина обхода графа вызовов (0 — без ограничений)

## Результаты

- `usage_<target>.txt`: места использования метода (файл, строка, фрагмент)
- `callgraph_<target>.txt`: рёбра графа (кто кого вызывает)
- `callgraph_<target>.png`: изображение графа

## Ограничения

- Статический анализ без полноценного вывода типов. Поддерживаются типовые случаи: `self.method()`, `cls.method()`, `ClassName.method()`, `var = ClassName(...); var.method()`.
- Динамические трюки Python (метаклассы, monkey patching, фабрики и пр.) могут не разрешаться.
- Для больших проектов может работать медленнее. Используйте фильтрацию по модулю в `--target` и ограничение `--max-depth`.

## Подсказки

- Если есть несколько одноимённых классов/методов в разных модулях, уточняйте `--target` через `module.submodule:Class.method`.
- Если PNG получается перегруженным, попробуйте меньшую глубину или смотрите `.txt` файл с ребрами.