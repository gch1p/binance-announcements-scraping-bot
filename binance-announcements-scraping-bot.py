#!/usr/bin/env python3
import sys, traceback
from requests import get
from bs4 import BeautifulSoup
from ch1p import State, telegram_notify
from html import escape


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
            id = link.get('id')
            if id is None:
                continue
            if not link.get('id').startswith('supportList'):
                continue

            category_data['news'].append({
                'text': link.text,
                'link': link.get('href')
            })
            total_news += 1

        data.append(category_data)

    if not total_news:
        raise RuntimeError('failed to find any articles')

    return data


if __name__ == '__main__':
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
                buf = f"<i>{category['title']}</i>\n"
                buf += '\n'.join(list(map(lambda item: f"<a href=\"{item['link']}\">{item['text']}</a>", updates)))
                blocks.append(buf)

        if blocks:
            message = '<b>Binance Announcements</b>\n\n'
            message += '\n\n'.join(blocks)

            telegram_notify(text=message, parse_mode='HTML')

    except:
        telegram_notify(text='error: ' + escape(traceback.format_exc()), parse_mode='HTML')