#!/usr/bin/env python3
import traceback
import json
import sys

from requests import get
from ch1p import State, telegram_notify
from html import escape
from argparse import ArgumentParser


def scrap_announcements():
    response = get('https://www.binance.com/bapi/composite/v1/public/cms/article/list/query?type=1&pageNo=1&pageSize=50')

    data = json.loads(response.text)
    categories = []
    count = 0

    for catalog in data['data']['catalogs']:
        category = {
            'name': catalog['catalogName'],
            'articles': []
        }

        for article in catalog['articles']:
            category['articles'].append({
                'url': f'https://www.binance.com/en/support/announcement/{article["code"]}',
                'rel_date': article['releaseDate'],
                'title': article['title']
            })
            count += 1

        categories.append(category)

    if not count:
        raise RuntimeError('failed to find any articles')

    return categories


def main(print_to_stdout: bool):
    last_rel_date = 0
    state = State(default={'urls': [], 'last_rel_date': last_rel_date})
    if 'last_rel_date' in state:
        last_rel_date = state['last_rel_date']

    try:
        blocks = []
        data = scrap_announcements()
        for category in data:
            updates = []
            for item in category['articles']:
                if item['rel_date'] <= last_rel_date or item['url'] in state['urls']:
                    continue

                updates.append(item)
                if item['rel_date'] > last_rel_date:
                    last_rel_date = item['rel_date']

            if updates:
                buf = f"<b>Binance: {category['name']}</b>\n"
                buf += '\n'.join(list(map(lambda a: f"<a href='{a['url']}'>{a['title']}</a>", updates)))
                blocks.append(buf)

        state['last_rel_date'] = last_rel_date

        if blocks:
            message = '\n\n'.join(blocks)
            if print_to_stdout:
                print(message)
            else:
                telegram_notify(text=message, parse_mode='HTML', disable_web_page_preview=True)
    except:
        if print_to_stdout:
            traceback.print_exc()
        else:
            telegram_notify(text='error: ' + escape(traceback.format_exc()), parse_mode='HTML')


if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument('--stdout', action='store_true')
    args = parser.parse_args()

    main(args.stdout)

