import json
import argparse
from readability_tools.web_scraper import WebScraper, RequestException, ConfigurableTag
from readability_tools.file_saver import FileSaverTool
from readability_tools.utils import web_scraper_from_cofing, file_siver_from_config

def get_config() -> dict:
    required_keys = ('main_tag',
                     'secondary_tags',
                     'text_tag',
                     'characters_per_line',
                     'paragraphs_indent',
                     'default_file_name',
                     'file_extension')
    try:
        file = open('config.json', 'r')
        config = json.load(file)
        if any([x not in config for x in required_keys]):
            raise Exception(
                "Config file doesn't contains all reqiered keys. Must be present:\n"+ '\n'.join(required_keys))
        config['main_tag'] = ConfigurableTag.from_dict(config['main_tag'])
        config['secondary_tags'] = tuple(map(
                                         lambda x: 
                                         ConfigurableTag.from_dict(x),
                                         config['secondary_tags']))
        config['text_tag'] = ConfigurableTag.from_dict(config['text_tag'])
        print('Config has been successfully loaded.')
    except Exception as error:
        print(f'Config file is not found or invalid:\n{error}\n\nUsing default settings.\n')
        config = {}
    finally:
        return config
    
def main():
    config = get_config() if not args.default else {}
    scraper = WebScraper() if not config else web_scraper_from_cofing(config)
    saver_tool = FileSaverTool() if not config else file_siver_from_config(config)
    try:
        result = scraper.parse(args.url)
    except RequestException as error:
        print(error)
    else:
        saver_tool.write_to_file(result, args.url)

if __name__ == '__main__':
    arg_parses = argparse.ArgumentParser(description='News article parses')
    arg_parses.add_argument('url', type=str, help='Link to the article for parsing')
    arg_parses.add_argument('-d', '--default', action='store_true',
                            help='Forse use of default config.')
    args = arg_parses.parse_args()
    main()
