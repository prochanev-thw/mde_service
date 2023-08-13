import logging
import time
import os
from pprint import pprint

import json
import flask
import requests
import telebot
import sqlite3
from pydantic import parse_obj_as
from model import Update

from dotenv import load_dotenv
load_dotenv(override=True)

API_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
WEBHOOK_HOST = 'prochanev.fvds.ru'
WEBHOOK_PORT = 8443  # 443, 80, 88 or 8443 (port need to be 'open')
WEBHOOK_LISTEN = '0.0.0.0'  # In some VPS you may need to put here the IP addr
WEBHOOK_SSL_CERT = './YOURPUBLIC.pem'  # Path to the ssl certificate
WEBHOOK_SSL_PRIV = './YOURPRIVATE.key'  # Path to the ssl private key
WEBHOOK_URL_BASE = "https://%s:%s" % (WEBHOOK_HOST, WEBHOOK_PORT)

logger = telebot.logger
telebot.logger.setLevel(logging.INFO)

bot = telebot.TeleBot(API_TOKEN)

app = flask.Flask(__name__)


@app.route(f'/bot{API_TOKEN}', methods=['POST'])
def webhook():
    if flask.request.headers.get('content-type') == 'application/json':
        json_string = flask.request.get_data().decode('utf-8')
        update_tuple = parse_obj_as(Update, json.loads(json_string))
        conn = sqlite3.connect('statistic.db')
        cur = conn.cursor()
        cur.execute("""
            CREATE TABLE IF NOT EXISTS update_table (
                message_date INTEGER,
                user_id INTEGER,
                text TEXT,
                video_duration INTEGER,
                video_file_id TEXT
            );
        """)
        stmt = """
            insert into update_table (
                message_date,
                user_id,
                text,
                video_duration,
                video_file_id
            ) values (?, ?, ?, ?, ?)
        """
        print('insert data')
        cur.executemany(stmt, [update_tuple.to_tuple()])
        conn.commit()
        print('close conn')
        cur.close()
        return 'ok'
    else:
        flask.abort(403)


@app.route('/setwebhook', methods=['GET'])
def setwebhook():
    bot.remove_webhook()
    time.sleep(5)
    bot.set_webhook(
        url=os.path.join(
            WEBHOOK_URL_BASE,
            f'bot{API_TOKEN}'
        ),
        certificate=open(WEBHOOK_SSL_CERT, 'r')
    )

    return 'ok'

@app.route('/webhook_info', methods=['GET'])
def webhook_info():
    return requests.get(
            os.path.join(
            'https://api.telegram.org',
            f'bot{API_TOKEN}',
            'getWebhookInfo'
        ),
        verify=False
    ).json()


# Start flask server
app.run(host=WEBHOOK_LISTEN,
        port=WEBHOOK_PORT,
        ssl_context=(WEBHOOK_SSL_CERT, WEBHOOK_SSL_PRIV),
        debug=True)
