import textwrap
import os

class FileSaverTool:
    __slots__ = ['_path','_characters_per_line', '_paragraphs_indent']

    def __init__(self, character_per_line = 80, paragraphs_indent = '\n\n'):
        self._characters_per_line = character_per_line
        self._paragraphs_indent = paragraphs_indent

    def _create_directories(self) -> None:
        os.makedirs('/'.join(self._path[:-1]), exist_ok=True)

    def _set_path(self, url: str) -> None:
        path = url.split('/')[3:]
        path[-1] = 'article.txt' if not path[-1] else path[-1].split('.')[0] + '.txt'
        self._path = path

    def write_to_file(self, data: str, url: str):
        self._set_path(url)
        self._create_directories()

        with open('/'.join(self._path), 'w', encoding='utf-8') as file:
            file.write(self._paragraphs_indent
                       .join([textwrap.fill(x, self._characters_per_line) for x in data]))

        print(f"Article saved to: ./{'/'.join(self._path)}")
