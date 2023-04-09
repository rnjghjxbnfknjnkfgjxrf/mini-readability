from bs4 import BeautifulSoup, Tag
import requests

class WebScraper():

    __slots__ = ['_html', '_url', '_title', '_tags_with_text', '_main_tag', '_secondary_tags']

    def __init__(self, main_tag: str = 'div', secondary_tags: list[str] = None) -> None:
        self._main_tag = main_tag
        if secondary_tags is None:
            secondary_tags = ('span', 'li', 'blockquote')
        self._secondary_tags = secondary_tags

    def _retrieve_html(self, url: str) -> bool and int:
        response = requests.get(url)
        if response.status_code != 200:
            return False, response.status_code

        self._url = url
        self._html = BeautifulSoup(response.content, 'html.parser').body

        self._get_fragment_with_the_article_only()

        return True, response.status_code

    def _get_fragment_with_the_article_only(self) -> None:
        article_tag = self._html.find('article')
        if article_tag is not None and article_tag.find('p'):
            self._html = article_tag
        else:
            for div in self._html('div'):
                headers = div.find_all('h1')
                if headers is None:
                    headers = []
                if len(headers) == 1:
                    self._html = div
                    break

    def _remove_useless_tags(self) -> None:
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
        for header in self._html.find_all(('h2', 'h3')):
            if header('a'):
                continue
            new_p_tag = BeautifulSoup().new_tag('p')
            new_p_tag.extend(header)
            header.insert_after(new_p_tag)
            header.unwrap()

    def _find_main_tags_with_text(self) -> None:
        self._replace_headers()
        tags = []
        for tag in [self._html, *self._html.find_all(self._main_tag)]:
            p_tags = tag('p', recursive=False)
            tags.append(p_tags)

        self._tags_with_text = tags

    def _replace_secondary_tags_with_main_tags(self) -> None:
        for secondary_tag in self._html.find_all(self._secondary_tags):
            if secondary_tag('p', recursive=False):
                new_main_tag = BeautifulSoup().new_tag(self._main_tag)
                new_main_tag.extend(secondary_tag('p'))
                secondary_tag.insert_after(new_main_tag)
                secondary_tag.unwrap()

    def _replace_br_with_new_line(self) -> None:
        for br_tags in self._html('br'):
            br_tags.replace_with('\n')

    def _set_title(self) -> None:
        self._title = self._html.find('h1').get_text().strip()

    def _extract_href_from_tag(self, tag: Tag) -> str:
        result = ''
        href = tag['href']
        if not href.startswith('http'):
            result += '/'.join(self._url.split('/')[:3])
        result += href
        return f' [{result}]'

    def _generate_text(self) -> list[str]:
        full_text = [self._title]

        for tags in self._tags_with_text:
            for tag in tags:
                a_tags = tag('a', href=True)
                for a_tag in a_tags:
                    if a_tag.text.startswith('http'):
                        continue
                    href = BeautifulSoup().new_tag('a')
                    href.string = self._extract_href_from_tag(a_tag)
                    a_tag.insert_after(href)
                    a_tag.unwrap()
                full_text.append(tag.text.strip())
        return list(filter(lambda x: x, full_text))

    def parse(self, url) -> dict[str: str]:
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
