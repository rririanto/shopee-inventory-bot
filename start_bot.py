import logging
import gspread
from telegram.ext import Updater, CommandHandler
from oauth2client.service_account import ServiceAccountCredentials

import requests
import re
from datetime import datetime

# python-dotenv
import os
from dotenv import load_dotenv
load_dotenv()

# Enable logging
logging.basicConfig(
    filename='bot.log',
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO)
logger = logging.getLogger(__name__)

# get credential
GOOGLE_CREDENTIALS = os.getenv('GOOGLE_CREDENTIALS')
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')
SPREADSHEET_NAME = os.getenv('SPREADSHEET_NAME')
STORE_ID = os.getenv('STORE_ID')

# Shopee API endpoint
hostname = 'shopee.com.my'
api_host = f"https://{hostname}/api/v2/"
api_endpoint = {
    "user_detail": f"{api_host}shop/get?username={STORE_ID}",
    "product_detail": "{}item/get?itemid={}&shopid={}",
    "next": "{}search_items/?by=relevancy&match_id={}&newest=0&order=desc&page_type=shop&__classic__=1",
}

# header for scrapper
headers = {
    "host": f"{hostname}:443",
    "Accept": "application/json",
    "Referer": f"https://{hostname}/{STORE_ID}",
    "Content-Type": "application/json",
    "Accept": "*/*",
    "Sec-Fetch-Mode": "no-cors",
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36"
}

# Telegram settings
telegram_api = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"

# Google settings
spreadsheet_api = "https://docs.google.com/spreadsheets/d/{}/export?format=xlsx&id={}"
spreadsheet_scope = ['https://spreadsheets.google.com/feeds',
                     'https://www.googleapis.com/auth/drive']


def error(update, context):
    """Log Errors caused by Updates."""
    logger.warning(f'Update {update} caused error {context.error}')


def info(context):
    """Log Info"""
    logger.info(f'{context}')


def telegraminfo(data, urlspread):
    now = datetime.now()
    date_time = now.strftime("%d-%m-%Y, %H:%M:%S")

    text = "New stock update dari store %s (%s)\n\n" % (
        STORE_ID, date_time)
    for name, stock in (data):
        text += "%s\n" % name
        text += "Stock lama: %s, Stock baru: %s\n\n" % (stock[1], stock[0])

    text += "\n*Note: Download link xlxs & lakukan mass upload di shopee seller:\n%s" % urlspread
    payload = {
        'chat_id': TELEGRAM_CHAT_ID,
        'text': text,
        'parse_mode': 'HTML'
    }
    requests.post(telegram_api, data=payload).content
    return True


def crawler_product(itemid, shopid):
    product_url = api_endpoint["product_detail"].format(
        api_host, itemid, shopid)
    page = requests.get(product_url, headers=headers, verify=True)
    data = page.json()['item']
    return data["name"], data["stock"]


def crawler_shopee():
    url = api_endpoint["user_detail"]
    page = requests.get(url, headers=headers)
    shopid = page.json()['data']['shopid']
    nexturl = api_endpoint["next"].format(api_host, shopid)
    page2 = requests.get(nexturl, headers=headers, verify=True)
    data = []
    for i in page2.json()['items']:
        name, stock = crawler_product(i["itemid"], shopid)
        setup = [
            name,
            str(stock)
        ]
        data.append(setup)
    return data


def insert_gdocs():
    creds = ServiceAccountCredentials.from_json_keyfile_name(
        GOOGLE_CREDENTIALS, spreadsheet_scope)
    client = gspread.authorize(creds)
    sheet = client.open(SPREADSHEET_NAME).sheet1
    sheet_url = spreadsheet_api.format(
        sheet.spreadsheet.id, sheet.spreadsheet.id)
    data = crawler_shopee()
    updateable = []
    for name, stock in (data):
        try:
            amount_re = re.compile(r'%s*' % name, re.IGNORECASE)
            cell = sheet.find(amount_re)
            prev_stock = sheet.cell(cell.row, cell.col + 6).value
            if prev_stock != stock:
                updateable.append([name, [stock, prev_stock]])
                info(f"Update gsheets {name}")
                sheet.update_cell(cell.row, cell.col + 6, stock)
        except BaseException:
            try:
                name = re.compile(
                    r'[\w\d\ ]+',
                    flags=re.IGNORECASE | re.MULTILINE | re.LOCALE).search(name).group()
                amount_re = re.compile(r'%s*' % name, re.IGNORECASE)
                cell = sheet.find(amount_re)
                prev_stock = sheet.cell(cell.row, cell.col + 6).value
                if prev_stock != stock:
                    updateable.append([name, [stock, prev_stock]])
                    info(f"Update gsheets {name}")
                    sheet.update_cell(cell.row, cell.col + 6, stock)
            except BaseException:
                pass

    if updateable:
        return telegraminfo(updateable, sheet_url)
    return False


def start(update, context):
    update.message.reply_text(
        'Hello {}, ketik atau klik /update_stock_toko untuk mulai mengupdate toko'.format(
            update.message.from_user.first_name))


def update_stock_toko(update, context):
    update.message.chat_id
    update.message.reply_text(
        'Proses update sedang berlangsung. mohon tunggu sejenak. Terima Kasih')
    status = insert_gdocs()
    if not status:
        update.message.reply_text(
            'Belum ada perubahan stock terjadi di toko %s' %
            STORE_ID)


def main():
    """Run bot."""
    info("Bot started")
    updater = Updater(TELEGRAM_TOKEN, use_context=True)

    # Get the dispatcher to register handlers
    dp = updater.dispatcher

    # on different commands - answer in Telegram
    dp.add_handler(CommandHandler('start', start))
    dp.add_handler(
        CommandHandler(
            'update_stock_toko',
            update_stock_toko))

    # log all errors
    dp.add_error_handler(error)

    # Start the Bot
    updater.start_polling()

    # Block until you press Ctrl-C or the process receives SIGINT, SIGTERM or
    # SIGABRT. This should be used most of the time, since start_polling() is
    # non-blocking and will stop the bot gracefully.
    updater.idle()


if __name__ == '__main__':
    main()
