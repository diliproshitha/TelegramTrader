from telethon import TelegramClient, events
import logging

from config.config_reader import UserConfig
from config import constants
import traceback
from util.message_util import analyzeMessage

logging.basicConfig(level=logging.INFO, filename='../logs/messages.log')

api_id = None
api_hash = None

phone = None
username = None
target_group_ids = None
source_group_ids = None

config = None

entities = {}

# Init the message_interceptor
def init():
    global api_id, api_hash, phone, username, target_group_ids, source_group_ids, config
    api_id = constants.APP_APIID
    api_hash = constants.APP_APIHASH

    config = UserConfig()
    phone = config.getConfigValue(constants.USER_PHONENUMBER)
    username = config.getConfigValue(constants.USER_USERNAME)
    target_group_ids = list(map(int, config.getConfigValue(constants.CHAT_DESTINATION_CHAT_IDS).split(',')))
    source_group_ids = list(map(int, config.getConfigValue(constants.CHAT_SOURCE_CHAT_IDS).split(',')))

def startMessageClient():

    global entities, config

    init()
    print('Connecting to Telegram servers...')
    client = TelegramClient(phone, api_id, api_hash)
    print('Connected to Telegram servers...')
    print('Listening to Messages...')

    # start async client and bind event listener
    @client.on(events.NewMessage(chats=source_group_ids))
    async def my_event_handler(event):
        print('Message received : ' + event.raw_text)
        # logging.info(str(event.raw_text))

        #################################################
        #           ALTER AND FOREWARD                  #
        #################################################
        if config.getConfigValue(constants.ENV_ENVIRONMENT_FUNCTION) == constants.ENV_FUNCTION_ALTER_AND_FOREWARD :

            order_dict = analyzeMessage(event.raw_text)

            if order_dict.get(constants.ORDER_STATUS):

                decorated_message = getDecoratedMessage(order_dict)

                try:

                    # checks target group ids
                    # then get dialogs and stores them as entities if already not in entities
                    for target_group_id in target_group_ids:
                        if target_group_id not in entities:
                            dialogs = await client.get_dialogs(limit=None)
                            for dialog in dialogs:
                                if (dialog.entity.id == target_group_id):
                                    entities[target_group_id] = dialog

                        await client.send_message(entities.get(target_group_id).entity, decorated_message)

                except Exception as e:
                    print(e)
                    logging.error(str(e) + '\n')
                traceback.print_exc()

        #################################################
        #             READ AND FOREWARD                 #
        #################################################
        if config.getConfigValue(constants.ENV_ENVIRONMENT_FUNCTION) == constants.ENV_FUNCTION_READ_AND_FOREWARD:
            try:

                # checks target group ids
                # then get dialogs and stores them as entities if already not in entities
                for target_group_id in target_group_ids:
                            if target_group_id not in entities:
                                dialogs = await client.get_dialogs(limit=None)
                                for dialog in dialogs:
                                    if (dialog.entity.id == target_group_id):
                                        entities[target_group_id] = dialog

                            await client.send_message(entities.get(target_group_id).entity, event.raw_text)

            except Exception as e:
                print(e)
                logging.error(str(e) + '\n')
            traceback.print_exc()

    client.start()
    client.run_until_disconnected()

def getDecoratedMessage( order_dict ):

    message = ''
    if order_dict.get(constants.ORDER_STATUS):
        message += order_dict.get(constants.ORDER_TYPE) + ' '
        message += order_dict.get(constants.ORDER_INSATRUMENT) + ' '
        message += order_dict.get(constants.ORDER_PRICE) + '\n'
        message += 'STOP LOSS: ' + order_dict.get(constants.ORDER_STOP_LOSS) + '\n'
        message += 'TAKE PROFIT: ' + order_dict.get(constants.ORDER_TAKE_PROFIT)

    return message