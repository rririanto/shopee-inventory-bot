# shopee-inventory-bot

"I Make dropshiper's job easier" ~ shopee inventory bot [Watch video demo](https://github.com/jimmyromanticdevil/shopee-inventory-bot/blob/master/demo_video.mp4)

The idea inspired by my wife daily life as a dropshippers. In order to keep her store stock up-to-date, she did manual update for stocks from the suppliers store in shopee and it was quite exhausting because the more the items, the longer it takes to update them all. So as a loving husband, I came up with this simple idea to make her job easier. 

The bot tasks are quite simple. Just type /update_stock_store on Telegram message and all of the stock on the spreadsheets will be updated automaticaly. After that she just need to download the updated spreadsheet and upload it using [shopee mass updater](https://seller.shopee.co.id/edu/article/100)

## Requirements

- python-telegram-bot `pip install python-telegram-bot`
- oauth2client `pip install oauth2client`
- gspread `pip install gspread`
- requests `pip install requests`
- python-dotenv `pip install python-dotenv`

## Setup [.env](https://github.com/jimmyromanticdevil/shopee-inventory-bot/blob/master/.env)

GOOGLE_CREDENTIALS => [Obtain OAuth2 credentials from Google Developers Console](http://gspread.readthedocs.org/en/latest/oauth2.html)

TELEGRAM_TOKEN => [To generate an Access Token](https://github.com/python-telegram-bot/python-telegram-bot/wiki/Introduction-to-the-API)

TELEGRAM_CHAT_ID => [how to get the Chat ID](https://answers.splunk.com/answers/590658/telegram-alert-action-where-do-you-get-a-chat-id.html)

STORE_ID => https://shopee.co.id/{STORE_ID}

SPREADSHEET_NAME => Your spreadsheet name on google sheet. First go to mass update panel on [shopee store](https://seller.shopee.co.id/edu/article/100), download the xlxs and upload it to google spreadsheet and copy the name of it then put it on here.


## Installation

```sh

git clone https://github.com/jimmyromanticdevil/shopee-inventory-bot/
cd shopee-inventory-bot
pip install -r requirements.txt

python start_bot.py

```

## Issues
If the code is not working, you could check the bot.log in the directory and read the error.

- gspread.exceptions.SpreadsheetNotFound or This operation is not supported for this document', 'status': 'FAILED_PRECONDITION'
  please make sure you save the file as googlespreadsheet not as google drive. convert the spreadsheet by going to File> Save as Google Sheet.

- caused error ('Unexpected credentials type', None, 'Expected', 'service_account')
  please make sure to follow this step to create correct service acount. https://gspread.readthedocs.io/en/latest/oauth2.html

## Learn More

You can learn more about telegram-bot in the [Here](https://medium.com/@arushsharma91/telegram-bot-from-the-first-line-to-deployment-83141129a573) and [Here](https://www.freecodecamp.org/news/learn-to-build-your-first-bot-in-telegram-with-python-4c99526765e4/) 

To learn gspread, check out [Here](https://www.twilio.com/blog/2017/02/an-easy-way-to-read-and-write-to-a-google-spreadsheet-in-python.html)
