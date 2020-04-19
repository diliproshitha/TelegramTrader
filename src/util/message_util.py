import re
import logging
from config import constants

logging.basicConfig(handlers=[logging.FileHandler('../logs/messages.log', 'a', 'utf-8')], level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


def analyzeMessage(msg):

    order_dict = {}
    type_flag = False
    tp_flag = False
    sl_flag = False

    try:
        order_dict[constants.ORDER_STATUS] = False
        regex = re.compile('[^a-z.A-Z@\s\n0-9]')
        # #First parameter is the replacement, second parameter is your input string
        normalized_message = regex.sub('', msg)

        splitted_messages = normalized_message.split('\n');

        temp_msg = None

        for split_msg in splitted_messages:

            split_msg = re.sub(r"\s+", " ", split_msg )

            regex = re.compile('[a-z]{6}\s-\sbuy|sell', re.IGNORECASE)
            if (regex.match(split_msg)):
                temp_msg = split_msg.split(' ')
                if (len(temp_msg) > 1):
                    order_dict[constants.ORDER_TYPE] = temp_msg[1].upper()
                    order_dict[constants.ORDER_INSATRUMENT] = temp_msg[0].upper()
                    type_flag = True

            regex = re.compile('@')
            if (regex.match(split_msg)):
                temp_msg = split_msg.split(" ")
                if(len(temp_msg) > 1):
                    order_dict[constants.ORDER_PRICE] = temp_msg[1].upper()
                    type_flag = True

            regex = re.compile('sl', re.IGNORECASE)
            if regex.match(split_msg):
                temp_msg = split_msg.split(' ')
                if (len(temp_msg) > 1):
                    order_dict[constants.ORDER_STOP_LOSS] = temp_msg[1]
                    sl_flag = True

            regex = re.compile('tp', re.IGNORECASE)
            if regex.match(split_msg):
                temp_msg = split_msg.split(' ')
                if (len(temp_msg) > 1):
                    order_dict[constants.ORDER_TAKE_PROFIT] = temp_msg[1]
                    tp_flag = True

        if type_flag and sl_flag and tp_flag:
            order_dict[constants.ORDER_STATUS] = True
        return order_dict

    except Exception as e:
        return order_dict
        logging.error(str(e) + '\n')