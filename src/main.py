from message_operations import message_reader
from config.config_reader import UserConfig
from config import constants

if __name__== "__main__":

    config = UserConfig()

    if (config.getEnvConfigValue(constants.ENV_ENVIRONMENT_FUNCTION) == constants.ENV_FUNCTION_READ_AND_FOREWARD):
        message_reader.startMessageClient()
    elif (config.getEnvConfigValue(constants.ENV_ENVIRONMENT_FUNCTION) == constants.ENV_FUNCTION_ALTER_AND_FOREWARD):
        message_reader.startMessageClient()