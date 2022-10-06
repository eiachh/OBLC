from cgi import print_arguments


class OBLC_Logger:
    logLevel = 'Info'

    def __init__(self, loglevel):
        if(loglevel == 'Info' or loglevel == 'Debug' or loglevel == 'Init'):
            self.logLevel = loglevel
        else:
            self.logLevel = 'Info'
            self.log(f'Set log level was invalid {loglevel} using default value: {self.logLevel}', 'Warning')

    def setLogLevel(self, loglevel):
        self.logLevel = loglevel

    def getLogLevel(self):
        return self.logLevel

    def log(self, message, loglevel):
        if(loglevel == 'Init'):
            self.logImplementation(message)
            return
        if(loglevel == 'Debug' and self.logLevel == 'Info'):
            return
        self.logImplementation(message)

    def logImplementation(self, message):
        print(message)