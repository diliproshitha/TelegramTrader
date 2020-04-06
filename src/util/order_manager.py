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

    global REMOTE_SERVER_IPS
    global FORGE_API_KEY
    global pairs
    global symbol_prefixes
    global lot_sizes
    global excluded_pairs

    user_config = UserConfig()

    REMOTE_SERVER_IPS = user_config.getUserConfigValue(constants.TRD_REMOTE_SERVER_IP).split(',')
    symbol_prefixes = user_config.getUserConfigValue(constants.TRD_SYMBOL_PREFIX).split(',')
    FORGE_API_KEY = user_config.getUserConfigValue(constants.TRD_FORGE_API_KEY)
    pairs = user_config.getUserConfigValue(constants.TRD_PAIRS).split(',')
    excluded_pairs = user_config.getUserConfigValue(constants.TRD_EXCLUDED_PAIRS).split(',')
    lot_sizes = user_config.getUserConfigValue(constants.TRD_LOT_SIZES).split(',')


def sendOrder(orderDict):

    try:

        for (index, ip) in enumerate(REMOTE_SERVER_IPS) :
            excluded_pairs_for_server = excluded_pairs[index].split('-')
            if orderDict.get(constants.ORDER_INSATRUMENT) not in excluded_pairs_for_server:
                _zmq = DWX_ZeroMQ_Connector(_host=ip)
                _my_trade = _zmq._generate_default_order_dict()
                _my_trade['_SL'] = getPricePoints(ast.literal_eval(orderDict.get(constants.ORDER_PRICE)),
                                                  ast.literal_eval(orderDict.get(constants.ORDER_STOP_LOSS)),
                                                  orderDict.get(constants.ORDER_INSATRUMENT))
                _my_trade['_TP'] = getPricePoints(ast.literal_eval(orderDict.get(constants.ORDER_PRICE)),
                                                  ast.literal_eval(orderDict.get(constants.ORDER_TAKE_PROFIT)),
                                                  orderDict.get(constants.ORDER_INSATRUMENT))
                _my_trade['_price'] = ast.literal_eval(orderDict.get(constants.ORDER_PRICE))
                _my_trade['_type'] = 1 if orderDict.get(constants.ORDER_TYPE) == 'SELL' else 0
                _my_trade['_lots'] = ast.literal_eval(lot_sizes[index])
                _my_trade['_symbol'] = orderDict.get(constants.ORDER_INSATRUMENT) + '.' + symbol_prefixes[index] if len(
                    symbol_prefixes[index]) > 0 else orderDict.get(constants.ORDER_INSATRUMENT)
                _my_trade['_comment'] = '*New Signal* ' + str(datetime.now())

                print(_my_trade)
                _zmq._DWX_MTX_NEW_TRADE_(_my_trade)
                adjustOrderPrices(_zmq, orderDict)

    except Exception as e:
        logging.error(str(e) + '\n')

def getCurrentPrice(pair):
    url = 'https://forex.1forge.com/1.0.3/quotes?pairs=' + pair +'&api_key=' + FORGE_API_KEY
    response = requests.get(url)
    # print('Fetching price from: ' + url)
    # print('Response: ' + str(response.json()))
    return float(response.json()[0]['bid'])

def adjustOrderPrices(_zmq, orderDict) :
    if (_zmq._thread_data_output is not None and _zmq._thread_data_output.get('_ticket') is not None):
        ticket = _zmq._thread_data_output.get('_ticket')

        stoploss = abs(getPricePoints(ast.literal_eval(orderDict.get(constants.ORDER_STOP_LOSS)), _zmq._thread_data_output.get('_open_price'), orderDict.get(constants.ORDER_INSATRUMENT)))
        takeprofit = abs(getPricePoints(ast.literal_eval(orderDict.get(constants.ORDER_TAKE_PROFIT)), _zmq._thread_data_output.get('_open_price'), orderDict.get(constants.ORDER_INSATRUMENT)))

        sl_multiplier = 1
        tp_multiplier = 1
        # if orderDict.get(constants.ORDER_TYPE) == 'SELL' :
        #     if ast.literal_eval(orderDict.get(constants.ORDER_STOP_LOSS)) > _zmq._thread_data_output.get('_sl'):
        #         sl_multiplier = 1
        #     else :
        #         sl_multiplier = -1
        #     if ast.literal_eval(orderDict.get(constants.ORDER_TAKE_PROFIT)) > _zmq._thread_data_output.get('_tp'):
        #         tp_multiplier = -1
        #     else :
        #         tp_multiplier = 1
        # else :
        #     if ast.literal_eval(orderDict.get(constants.ORDER_STOP_LOSS)) > _zmq._thread_data_output.get('_sl'):
        #         sl_multiplier = 1
        #     else :
        #         sl_multiplier = -1
        #     if ast.literal_eval(orderDict.get(constants.ORDER_TAKE_PROFIT)) > _zmq._thread_data_output.get('_tp'):
        #         tp_multiplier = 1
        #     else :
        #         tp_multiplier = -1

        stoploss = stoploss * sl_multiplier
        takeprofit = takeprofit * tp_multiplier

        _zmq._DWX_MTX_MODIFY_TRADE_BY_TICKET_(ticket, stoploss, takeprofit)

def getPricePoints(order_price, target_price, instrument):
    # num_decimal_places = abs(decimal.Decimal(str(order_price)).as_tuple().exponent)
    # temp_order_price = order_price * (10 ** num_decimal_places)
    # temp_take_profit = target_price * (10 ** num_decimal_places)
    decimal_factor = ast.literal_eval(user_config.getUserConfigValue(constants.TRD_PAIR_PRICE_POINT_FACTOR + instrument))
    return int(abs(order_price - target_price) * decimal_factor)