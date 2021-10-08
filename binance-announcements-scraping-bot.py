#!/usr/bin/env python3
import traceback
from requests import get
from bs4 import BeautifulSoup
from ch1p import State, telegram_notify
from html import escape
from argparse import ArgumentParser


def scrap_announcements():
    url = "https://www.binance.com/en/support/announcement"
    response = get(url)
    soup = BeautifulSoup(response.text, 'html.parser')

    data = []
    total_news = 0

    categories_list = soup.find_all(class_='css-wmvdm0')
    for c in categories_list:
        category_title = c.select('h2[data-bn-type="text"]')[0].text
        category_data = {
            'title': category_title,
            'news': []
        }

        for link in c.find_next('div').select('a[data-bn-type="link"]'):
            if link.text.strip().lower() == 'view more':
                continue

            href = link.get('href')
            if href.startswith('/'):
                href = f'https://www.binance.com{href}'
            category_data['news'].append({
                'text': link.text,
                'link': href
            })
            total_news += 1

        data.append(category_data)

    if not total_news:
        raise RuntimeError('failed to find any articles')

    return data


if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument('--stdout', action='store_true')
    args = parser.parse_args()

    state = State(default=dict(urls=[]))
    try:
        blocks = []
        data = scrap_announcements()
        for category in data:
            updates = []
            for item in category['news']:
                if item['link'] not in state['urls']:
                    updates.append(item)
                    state['urls'].append(item['link'])

            if updates:
                buf = f"<b>Binance: {category['title']}</b>\n"
                buf += '\n'.join(list(map(lambda item: f"<a href='{item['link']}'>{item['text']}</a>", updates)))
                blocks.append(buf)

        if blocks:
            message = '\n\n'.join(blocks)

            if args.stdout:
                print(message)
            else:
                telegram_notify(text=message, parse_mode='HTML', disable_web_page_preview=True)

    except:
        if args.stdout:
            traceback.print_exc()
        else:
            telegram_notify(text='error: ' + escape(traceback.format_exc()), parse_mode='HTML')