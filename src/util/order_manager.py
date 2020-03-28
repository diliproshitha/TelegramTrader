import re
from libs.DWX_ZeroMQ_Connector_v2_0_1_RC8 import DWX_ZeroMQ_Connector
import requests
from datetime import datetime
import decimal
import logging
from config.config_reader import UserConfig
from config import constants
import ast

logging.basicConfig(handlers=[logging.FileHandler('../logs/messages.log', 'a', 'utf-8')], level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def init():
    global user_config

    global REMOTE_SERVER_IP
    global FORGE_API_KEY
    global pairs

    user_config = UserConfig()

    REMOTE_SERVER_IP = user_config.getUserConfigValue(constants.TRD_REMOTE_SERVER_IP)
    FORGE_API_KEY = user_config.getUserConfigValue(constants.TRD_FORGE_API_KEY)
    pairs = user_config.getUserConfigValue(constants.TRD_PAIRS).split(',')


def sendOrder(orderDict):

    try:
        _zmq = DWX_ZeroMQ_Connector(_host=REMOTE_SERVER_IP)
        _my_trade = _zmq._generate_default_order_dict()
        _my_trade['_SL'] = getPricePoints(ast.literal_eval(orderDict.get(constants.ORDER_PRICE)), ast.literal_eval(orderDict.get(constants.ORDER_STOP_LOSS)), orderDict.get(constants.ORDER_INSATRUMENT))
        _my_trade['_TP'] = getPricePoints(ast.literal_eval(orderDict.get(constants.ORDER_PRICE)), ast.literal_eval(orderDict.get(constants.ORDER_TAKE_PROFIT)), orderDict.get(constants.ORDER_INSATRUMENT))
        _my_trade['_price'] = ast.literal_eval(orderDict.get(constants.ORDER_PRICE))
        _my_trade['_type'] = orderDict.get(constants.ORDER_TYPE)
        _my_trade['_symbol'] = orderDict.get(constants.ORDER_INSATRUMENT)
        _my_trade['_comment'] = '*New Signal* ' + str(datetime.now())

        print(_my_trade)
        _zmq._DWX_MTX_NEW_TRADE_(_my_trade)

    except Exception as e:
        logging.error(str(e) + '\n')

def getCurrentPrice(pair):
    url = 'https://forex.1forge.com/1.0.3/quotes?pairs=' + pair +'&api_key=' + FORGE_API_KEY
    response = requests.get(url)
    # print('Fetching price from: ' + url)
    # print('Response: ' + str(response.json()))
    return float(response.json()[0]['bid'])

def getPricePoints(order_price, target_price, instrument):
    # num_decimal_places = abs(decimal.Decimal(str(order_price)).as_tuple().exponent)
    # temp_order_price = order_price * (10 ** num_decimal_places)
    # temp_take_profit = target_price * (10 ** num_decimal_places)
    decimal_factor = ast.literal_eval(user_config.getUserConfigValue(constants.TRD_PAIR_PRICE_POINT_FACTOR + instrument))
    return int(abs(order_price - target_price) * decimal_factor)