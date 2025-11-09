# cache_manager.py
from src.parsers.content_cache import ContentCache

# Создаем глобальный экземпляр кэша
_content_cache_instance = None

def get_content_cache():
    """Возвращает единый экземпляр ContentCache для всего приложения"""
    global _content_cache_instance
    if _content_cache_instance is None:
        _content_cache_instance = ContentCache()
    return _content_cache_instance

def clear_cache():
    """Очищает кэш (для тестирования)"""
    global _content_cache_instance
    if _content_cache_instance is None:
        _content_cache_instance = ContentCache()
    _content_cache_instance.invalidate_all()