import logging

class UserConfig(object):
    class __UserConfig:

        __keys = {}
        __readSuccess = False

        def __init__(self):
            self.val = None
        def __str__(self):
            return repr(self) + self.val

        def initConfig(self):
            separator = "="

            if not self.__readSuccess:
                try:
                    with open('../resources/user.properties') as f:

                        for line in f:
                            if separator in line:
                                # Find the name and value by splitting the string
                                name, value = line.split(separator, 1)

                                # Assign key value pair to dict
                                # strip() removes white space from the ends of strings
                                self.__keys[name.strip()] = value.strip()
                        self.__readSuccess = True
                except Exception as e:
                    logging.error(str(e) + '\n')
                    print(e)

        def getConfigValue(self, configName):
            if not self.__readSuccess:
                self.initConfig()
            return self.__keys.get(configName)


    instance = None
    def __new__(cls): # __new__ always a classmethod
        if not UserConfig.instance:
            UserConfig.instance = UserConfig.__UserConfig()
        return UserConfig.instance
    def __getattr__(self, name):
        return getattr(self.instance, name)
    def __setattr__(self, name):
        return setattr(self.instance, name)
