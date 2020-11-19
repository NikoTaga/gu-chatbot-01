"""Used to add new webhook subs to the testing OK group.

Also clears outdated subscriptions.
usage: python ok_subscribe.py <link>
<link> is usually an ngrok (https://ngrok.com/download) tunnel link"""

import requests
import json
from pprint import pprint
import sys
from datetime import timedelta, datetime
from pytz import timezone


# unused for now
VPS_HOOKS = [
    "http://194.67.90.202:8000/ok_test/",
    "http://194.67.90.202:8000/ok_webhook/",
]

CHAT = 'chat:C44f9f0965600'
TOKEN = 'tkn1wILRxmauO2rhrdYCdw41cqv2aLtebSzXqTHbv6SrRzQuZ7u8hz0ZOJMc9NmRESevE2:CLOKPPJGDIHBABABA'
HEADERS = {'Content-Type': 'application/json;charset=utf-8'}


def subscribe_webhook(url):
    link = f'https://api.ok.ru/graph/me/subscribe?access_token={TOKEN}'
    data = '''{"url":"%s"}''' % url

    r = requests.post(link, headers=HEADERS, data=data)
    ans = json.loads(r.text)
    # pprint(ans)
    if ans['success']:
        print(f'Subscribed "{url}"')


def unsubscribe_webhook(url):
    link = f'https://api.ok.ru/graph/me/unsubscribe?access_token={TOKEN}'
    data = '''{"url":"%s"}''' % url

    r = requests.post(link, headers=HEADERS, data=data)
    ans = json.loads(r.text)
    # pprint(ans)
    if ans['success']:
        print(f'Unsubscribed "{url}"')


def list_webhooks():
    link = f'https://api.ok.ru/graph/me/subscriptions?access_token={TOKEN}'

    r = requests.post(link, headers=HEADERS)
    # pprint(json.loads(r.text))
    return json.loads(r.text)


if __name__ == '__main__':
    current_subs = [sub for sub in list_webhooks()['subscriptions'] if 'url' in sub]
    print('Existing webhooks:')
    for sub in current_subs:
        print(sub['url'])
    if not sys.argv:
        print('Input a url as a parameter to set a new webhook!')
        sys.exit(1)

    msk_tz = timezone('Europe/Moscow')
    outdated_urls = [
        sub['url'] for sub in current_subs
        if (datetime.now().astimezone() - msk_tz.localize(datetime.fromtimestamp(sub['time']/1000)) > timedelta(hours=2))
    ]
    print('Clearing old webhooks...')
    for url in outdated_urls:
        unsubscribe_webhook(url)

    new_webhook = sys.argv[1]
    subscribe_webhook(new_webhook)
