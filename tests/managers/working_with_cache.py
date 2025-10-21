from src.parsers.content_cache import ContentCache
from src.operation.file_operations import FileOperations

def get_cache(cache):
    # Простой способ посмотреть что в кэше
    #cache = ContentCache()

    print("Ключи в кэше:")
    for key in cache._cache.keys():
        print(f" - {key}")

    print(f"\nВсего элементов: {len(cache._cache)}")

def get_cache_path(cache,file_path):
    if file_path in cache._cache:
        data = cache._cache[file_path]
        print("Метаданные:", {
            'size': data['size'],
            'timestamp': data['timestamp'],
            'access_count': data['access_count']
        })
        print("Контент:", data['content'])
    else:
        print("Файл не найден в кэше")

    # Посмотреть все доступные файлы в кэше
    #print("Файлы в кэше:")
    #for path in cache._cache.keys():
    #    print(f" - {path}")

def working_with_cache(info_item_dict, element_dict):
    print(f'🔥🔥🔥🔥 Зашли в метод working_with_cache 🔥🔥🔥🔥')
    content_cache = ContentCache()
    cache_data = content_cache.find_point_selection(info_item_dict)
    print(f'☢️cache_data:  {cache_data}')
    print(f'⚔️ element_dict: {element_dict}')
    if cache_data:
        file_operation = FileOperations()
        # 1. Изменяем структуру в кэше
        updated_structure = file_operation.add_data_st_structure(cache_data, element_dict)
        print(f'updated_structure:  {updated_structure}')
        file_path = info_item_dict['path']
        # 2. Сохраняем обновленную структуру обратно в кэш
        updated_structure_tuple = 'file', updated_structure
        content_cache.set(file_path, updated_structure_tuple)
        # 3. Получаем данные из кэш
        cache = content_cache.get(file_path)
        print(f'⌯⌲ Из кэш получили данные: {cache}')
        print("****************************************")
        get_cache_path(content_cache,file_path)
        #ddc = content_cache.debug_detailed_contents()
        #print(ddc)
        #print("****************************************")
        #print("****************************************")
        #ddc2 = content_cache.debug_show_cache_contents()
        #print(ddc2)
        print(f'🔴🟠🟡🟢🔵🟣 вышли из метода working_with_cache 🔴🟠🟡🟢🔵🟣')
def main() -> None:
    """Основная функция, запускаемая при выполнении модуля напрямую."""
    pass

if __name__ == "__main__":
    pass