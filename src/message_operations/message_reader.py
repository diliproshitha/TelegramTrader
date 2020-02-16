from telethon import TelegramClient, events
import logging

from config.config_reader import UserConfig
from config import constants
import traceback

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
    global api_id, api_hash, phone, username, target_group_ids, source_group_ids
    api_id = constants.APP_APIID
    api_hash = constants.APP_APIHASH

    config = UserConfig()
    phone = config.getConfigValue(constants.USER_PHONENUMBER)
    username = config.getConfigValue(constants.USER_USERNAME)
    target_group_ids = list(map(int, config.getConfigValue(constants.CHAT_DESTINATION_CHAT_IDS).split(',')))
    source_group_ids = list(map(int, config.getConfigValue(constants.CHAT_SOURCE_CHAT_IDS).split(',')))

def startMessageClient():

    global entities

    init()
    client = TelegramClient(phone, api_id, api_hash)

    # start async client and bind event listener
    @client.on(events.NewMessage(chats=source_group_ids))
    async def my_event_handler(event):
        print(event.raw_text)
        logging.info(str(event))

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

