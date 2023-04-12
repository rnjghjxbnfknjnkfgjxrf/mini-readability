from readability_tools.web_scraper import WebScraper
from readability_tools.file_saver import FileSaverTool

def web_scraper_from_cofing(config: dict) -> WebScraper:
    """
        Метод, преобразующий значения из с словаря,
        полученного из конфигурационного файла, в объект
        WebScraper.

        Args:
            config - словарь, полученый из конфиг-файла.
        
        Returns:
            Объект WebScraper из значений словаря.
    """
    return WebScraper(config['main_tag'],
                      config['secondary_tags'],
                      config['text_tag'])

def file_siver_from_config(config: dict) -> FileSaverTool:
    """
        Метод, преобразующий значения из с словаря,
        полученного из конфигурационного файла, в объект
        FileSaverTool.

        Args:
            config - словарь, полученый из конфиг-файла.
        
        Returns:
            Объект FileSaverTool из значений словаря.
    """
    return FileSaverTool(config['characters_per_line'],
                         config['paragraphs_indent'],
                         config['default_file_name'],
                         config['file_extension'])
