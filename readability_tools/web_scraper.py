from bs4 import BeautifulSoup, Tag
import requests

GET_CLASS_IF_EXISTS = lambda attr: {'class': attr.class_} if attr.class_ != 'any' else {}

class ConfigurableTag:
    """
    Класс, позволяющий удобно конфигурировать тег.
    """
    __slots__ = ('name', '_class')

    def __init__(self, name: str, class_: str) -> None:
        """
        Инициализация экземпляра класса.

        Args:
            name: название тега.
            class_: класс тега.
        """
        self.name = name
        self.class_ = class_

    @property
    def class_(self):
        return self._class

    @class_.setter
    def class_(self, class_: str):
        self._class = class_

    def __repr__(self) -> str:
        return f'<{self.name} class={self.class_}>'

    @classmethod
    def from_dict(cls, tag_as_dict: dict[str: str]):
        """
        Метод, преобращуюзий словарь в объект класса
        ConfigurableTag.
        """
        return ConfigurableTag(tag_as_dict['name'],
                               tag_as_dict['class_'])


class WebScraper:
    """
    Класс парсера, разбирающего новостные сайты, вычленяя из них текст статьи.
    """
    __slots__ = ('_html',
                 '_url',
                 '_title',
                 '_tags_with_text',
                 '_main_tag',
                 '_secondary_tags',
                 '_text_tag')

    def __init__(self,
                 main_tag: ConfigurableTag = ConfigurableTag('div', 'any'),
                 secondary_tags: tuple[ConfigurableTag] = None,
                 text_tag: ConfigurableTag = ConfigurableTag('p', 'any')) -> None:
        """
        Инициализация экземпляра класса.

        Args:
            main_tag: тег, внутри которого происходит
                      поиск текстовых тегов (default: ConfigurableTag('div', 'any') == <div>)
            secondary_tags: кортеж  второстепенных тегов, в которых
                            также может находится полезнная информация
                            (default: (ConfigurableTag('span', 'any') == <span>,
                                       ConfigurableTag('li', 'any') == <li>,
                                       ConfigurableTag('blockquote', 'any) == <blockquote>)
            text_tag: тег, внутри которого хранится текст
                           (default: ConfigurableTag('p', 'any') == <p>).
        """
        self._main_tag = main_tag
        if secondary_tags is None:
            secondary_tags = tuple(ConfigurableTag(x, 'any') for x in ('span', 'li', 'blockquote'))
        self._secondary_tags = secondary_tags
        self._text_tag = text_tag

    def _retrieve_html(self, url: str) -> bool and int:
        """
        Отправление запроса по заданному адресу и формирование
        объекта страницы для последующего парсинга.

        Args:
            url: ссылка на статью.
        
        Returns:
            Флаг успешности проведенных операций и код состояния http.
        """
        response = requests.get(url)
        if response.status_code != 200:
            return False, response.status_code

        self._url = url
        self._html = BeautifulSoup(response.content, 'html.parser').body

        self._get_fragment_with_the_article_only()

        return True, response.status_code

    def _get_fragment_with_the_article_only(self) -> None:
        """
        Сужение круга поиска нужных элементов:
        если в структуре сайта есть тэг <article> с находящимся
        внутри текстом (в текстовых тегах), то выбирается этот фрагмент,
        в ином случае берется <div>, в котором только один заголовок
        <h1>.
        """
        article_tag = self._html.find('article')
        if article_tag is not None and article_tag.find(self._text_tag.name,
                                                        GET_CLASS_IF_EXISTS(self._text_tag)):
            self._html = article_tag
        else:
            for div in self._html.find_all('div'):
                headers = div.find_all('h1')
                if headers is None:
                    headers = []
                if len(headers) == 1:
                    self._html = div
                    break

    def _remove_useless_tags(self) -> None:
        """
        Удаление мусорных элементов, в которых с наибольшей
        вероятностью не содержится полезной информации.
        """
        tags_to_remove = ('script',
                          'picture',
                          'button',
                          'style',
                          'svg',
                          'img',
                          'input',
                          'time',
                          'noscript',
                          'nav',
                          'form',
                          'meta_scroll',
                          'noindex',
                          'figure',
                          'figcaption')

        for target in self._html.find_all(tags_to_remove):
            target.decompose()

    def _replace_headers(self) -> None:
        """
        Замена тэгов заголовков <h2> и <h3>  на текстовые теги
        для их корректного позиционирования в конечном тексте. 
        """
        for header in self._html.find_all(('h2', 'h3')):
            if header('a'):
                continue
            new_text_tag = BeautifulSoup().new_tag(self._text_tag.name)
            new_text_tag.extend(header)
            header.insert_after(new_text_tag)
            header.unwrap()

    def _find_main_tags_with_text(self) -> None:
        """
        Поиск опорных элементов, внутри которых содержатся текстовые теги.
        """
        self._replace_headers()
        tags = []
        for tag in [self._html,
                   *self._html.find_all(
                        self._main_tag.name, GET_CLASS_IF_EXISTS(self._main_tag))]:
            text_tags = tag.find_all(self._text_tag.name,
                                     GET_CLASS_IF_EXISTS(self._text_tag),
                                     recursive=False, )
            tags.append(text_tags)

        self._tags_with_text = tags

    def _replace_secondary_tags_with_main_tags(self) -> None:
        """
        Перебор второстепенных элементов.
        Если внутри них встречаются текстовые теги, то 
        эти второстепенные элементы заменяются на опорные.
        """
        for secondary_tag in self._secondary_tags:
            for tag in self._html.find_all(secondary_tag.name, GET_CLASS_IF_EXISTS(secondary_tag)):
                text_tags = tag.find_all(self._text_tag.name,
                                GET_CLASS_IF_EXISTS(self._text_tag),
                                recursive=False)
                if text_tags:
                    new_main_tag = BeautifulSoup().new_tag(self._main_tag.name)
                    new_main_tag.extend(text_tags)
                    tag.insert_after(new_main_tag)
                    tag.unwrap()


    def _replace_br_with_new_line(self) -> None:
        """
        Замена тэгов <br> на символ переноса строки.
        """
        for br_tags in self._html('br'):
            br_tags.replace_with('\n')

    def _set_title(self) -> None:
        """
        Поиск заголовка статьи.
        """
        self._title = self._html.find('h1').get_text().strip()

    def _extract_href_from_tag(self, tag: Tag) -> str:
        """
        Получение корректной ссылки из тега <a>:
        берётся значение из атрибута href, если оно
        не начинается с http, то начало ссылки берётся
        из исходного url.

        Args:
            tag: тег, из которого вычленяется ссылка.

        Returns:
            Строка, в которой полученный адрес оборчивается в
            квадратные скобки
        """
        result = ''
        href = tag['href']
        if not href.startswith('http'):
            result += '/'.join(self._url.split('/')[:3])
        result += href
        return f' [{result}]'

    def _generate_text(self) -> list[str]:
        """
        Получение итогового текста статьи.

        Returns:
            Список строк с параграфами текста.
        """
        full_text = [self._title]

        for tags in self._tags_with_text:
            for tag in tags:
                a_tags = tag.find_all('a', href=True)
                for a_tag in a_tags:
                    if a_tag.text.startswith('http'):
                        continue
                    href = BeautifulSoup().new_tag('a')
                    href.string = self._extract_href_from_tag(a_tag)
                    a_tag.insert_after(href)
                    a_tag.unwrap()
                full_text.append(tag.text.strip())
        return list(filter(lambda x: x, full_text))

    def parse(self, url: str) -> list[str]:
        """
        Парсинг новостного сайта из указанного адреса и получение
        текста статьи.

        Args:
            url: ссылка на статью.
        
        Return:
            Список строк с параграфами текста.
        
        Raises:
            RequestException: Если не получен ответ от сервера.
        """
        response = self._retrieve_html(url)
        if not response[0]:
            raise RequestException(response[1])
        del response

        self._replace_secondary_tags_with_main_tags()
        self._remove_useless_tags()
        self._set_title()
        self._replace_br_with_new_line()
        self._find_main_tags_with_text()

        return self._generate_text()


class RequestException(Exception):
    def __init__(self, status_code):
        super().__init__(f'Invalid URL or website is unreachable (status code: {status_code}).')
