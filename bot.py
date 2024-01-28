import schedule
import telebot
from threading import Thread
from time import sleep
from pybit.unified_trading import HTTP
import pandas as pd
from datetime import datetime, timedelta, date
import config


bot = telebot.TeleBot(config.TELEGRAM_BOT_TOKEN)


emojies = {
    'spot' : '\U0001F3F9',
    'invest': '\U0001F33E',
    'pin' : '\U0001F4CC',
}


def schedule_checker():
    while True:
        schedule.run_pending()
        sleep(1)


def get_trade_history(api_key, api_secret):

    session = HTTP(
        testnet=False,
        api_key=api_key,
        api_secret=api_secret,
    )

    data = session.get_executions(
        category="spot",
        startTime=round(datetime.timestamp((datetime.now() - timedelta(hours=1))) * 1000),
    )['result']['list']

    df = pd.DataFrame(data)[['symbol', 'side', 'orderType', 'execFee', 'execPrice', 'execQty', 'execTime']] \
           .astype({'execFee': 'float', 'execPrice': 'float', 'execQty': 'float'})

    df['time'] = pd.to_datetime(df.execTime, unit='ms').dt.date
    df['amount'] = (df.execPrice * df.execQty) + df.execFee

    return df.groupby(['time', 'symbol'], as_index=False) \
             .agg({'amount': 'sum'}) \
             .sort_values(by=['time', 'symbol'], ascending=[0,1])


def create_notification(type):
    if type == 'spot':
        df = get_trade_history(config.SPOT_API_KEY, config.SPOT_API_SECRET)
    elif type == 'invest':
        df = get_trade_history(config.INVEST_API_KEY, config.INVEST_API_SECRET)

    if len(df) == 0:
        return False
    else:
        res = f"{emojies[type]}{type.upper()}{emojies[type]}\n"
        for row in df.iterrows():
            res += (f"\n{emojies['pin']} {row[1]['symbol']}: {round(row[1]['amount'], 2)}")
        return res


def send_notification():
    try:
        spot_notification = create_notification('spot')
    except:
        spot_notification = False
    try:
        invest_notification = create_notification('invest')
    except:
        invest_notification = False

    if spot_notification:
        bot.send_message(config.CHAT_ID, spot_notification)
    if invest_notification:
        bot.send_message(config.CHAT_ID, invest_notification)


@bot.message_handler(commands=['start'])
def start_message(message):
    bot.send_message(message.chat.id, f'CHAT_ID: {message.chat.id}')


if __name__ == "__main__":

    schedule.every().hour.do(send_notification)

    Thread(target=schedule_checker).start()

    bot.infinity_polling(timeout=10, long_polling_timeout=5)
