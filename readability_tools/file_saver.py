import textwrap
import os

class FileSaverTool:
    """
    Класс, сохраняющий список строк по заданному пути с
    определенным форматированием.
    """
    __slots__ = ('_path','_characters_per_line', '_paragraphs_indent', '_default_file_name', '_file_extension')

    def __init__(self,
                 character_per_line: int = 80,
                 paragraphs_indent: str = '\n\n',
                 default_file_name: str = 'article',
                 file_extension: str = 'txt'):
        """
        Инициализация экземпляра класса.

        Args:
            character_per_line: максимально допустимое количество символов
                                в одной строке (default: 80).
            paragraphs_indent: символы, по которым будут объединяться абзацы
                               (default: '\\n\\n').
            default_file_name: имя, которое будет присвоено файлу, если
                               не получится получить название из адреса
                               (default: 'article').
            file_extension: расширение итогового файла (default: 'txt').
        """
        self._characters_per_line = character_per_line
        self._paragraphs_indent = paragraphs_indent
        self._default_file_name = default_file_name
        self._file_extension = file_extension

    def _create_directories(self) -> None:
        """
        Создание нужных директорий для сохраения файла.
        """
        os.makedirs('/'.join(self._path[:-1]), exist_ok=True)

    def _set_path(self, url: str) -> None:
        """
        Получение пути и имени файа из адреса.
        Если имя файла не получено, то задается значение из
        атрибута _default_file_name.
        """
        path = url.split('/')[3:]
        path[-1] = self._default_file_name if not path[-1] else path[-1].split('.')[0]
        path[-1] += f'.{self._file_extension}'
        self._path = path

    def write_to_file(self, data: list[str], url: str):
        """
        Запись текста в файл. Название файла и путь к нему
        получаются из ссылки.

        Args:
            data: список со строками (абзацами).
            url: веб-адрес.
        """
        self._set_path(url)
        self._create_directories()

        with open('/'.join(self._path), 'w', encoding='utf-8') as file:
            file.write(self._paragraphs_indent
                       .join([textwrap.fill(x, self._characters_per_line) for x in data]))

        print(f"Article saved to: ./{'/'.join(self._path)}")
