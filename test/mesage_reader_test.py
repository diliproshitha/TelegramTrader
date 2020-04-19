from util.message_util import analyzeMessage
from message_operations.message_reader import getDecoratedMessage
from config.config_reader import UserConfig
from util import order_manager
from config import constants


message = "NZDUSD - SELL\n@ 0.60356\nTP - 0.59159\nSL - 0.60752"
config = UserConfig()
order_manager.init()

order_dict = analyzeMessage(message)
pairs = config.getUserConfigValue(constants.TRD_PAIRS).split(',')

if int(config.getEnvConfigValue(constants.TRD_ALLOW_TRADING)) == 1 and order_dict.get(
        constants.ORDER_STATUS) and order_dict.get(constants.ORDER_INSATRUMENT) in pairs:
    order_manager.sendOrder(order_dict)
print(getDecoratedMessage(order_dict))