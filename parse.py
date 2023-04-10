import json
import argparse
from readability_tools.web_scraper import WebScraper, RequestException
from readability_tools.file_saver import FileSaverTool


def get_config() -> dict:
    required_keys = ('main_tag',
                     'secondary_tags',
                     'characters_per_line',
                     'paragraphs_indent',
                     'default_file_name',
                     'file_extension')
    try:
        file = open('config.json', 'r')
        config = json.load(file)
        if any([x not in config for x in required_keys]):
            raise Exception("Config file doesn't contains all reqiered keys. Must be present:\n" + '\n'.join(required_keys))
        config['secondary_tags'] = tuple(config['secondary_tags'])
        print('Config has been successfully loaded.')
    except Exception as error:
        print(f'Config file is not found or invalid:\n{error}\n\nUsing default settings.\n')
        config = {}
    finally:
        return config
    
def main():
    config = get_config()
    scraper = WebScraper() if not config else WebScraper(config['main_tag'], config['secondary_tags'])
    saver_tool = FileSaverTool() if not config else FileSaverTool(config['characters_per_line'],
                                                                  config['paragraphs_indent'],
                                                                  config['default_file_name'],
                                                                  config['file_extension'])
    try:
        result = scraper.parse(args.url)
    except RequestException as error:
        print(error)
    else:
        saver_tool.write_to_file(result, args.url)

if __name__ == '__main__':
    arg_parses = argparse.ArgumentParser(description='News article parses')
    arg_parses.add_argument('url', type=str, help='Link to the article for parsing')
    args = arg_parses.parse_args()
    main()
