class Logger:
    """
    just a simple logging class.

    This is a singleton class. See ../settings.py for usage
    """
    LEVEL_NONE = 0
    LEVEL_ITERATIONS = 1
    LEVEL_DETAILS = 2

    # internal class (used for singleton pattern)
    class __Logger:
        def __init__(self, loglevel: int):
            self.__loglevel = loglevel

        def setLoglevel(self, loglevel: int):
            self.__loglevel = loglevel

        def __call__(self, msg: str, level: int, end: str = "\n"):
            if level <= self.__loglevel:
                print(msg, end=end)

    __instance = __Logger(LEVEL_DETAILS)

    @staticmethod
    def getInstance(loglevel: int = LEVEL_DETAILS) -> __Logger:
        """
        :returns a Logger instance (Singleton)
        :param loglevel: the level to log with
        """
        if Logger.__instance is None:
            Logger.__instance = Logger.__Logger()

        Logger.__instance.setLoglevel(loglevel)
        return Logger.__instance
