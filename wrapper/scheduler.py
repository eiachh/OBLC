from wrapper.scheduleToken import ScheduleToken

class Scheduler:

    def __init__(self, logger):
        self.logger = logger
        self.NormalQueue = {}
        self.

    def scheduleAction(self, scheduleToken):
        if( not (type(scheduleToken) == type(ScheduleToken))):
            self.logger.logWarn(f"Schedule token invalid, current token type: {type(scheduleToken)}")
            return
        if(self.isNormalQueableToken(scheduleToken)):
            
        
    def isNormalQueableToken(self, scheduleToken):
        return(scheduleToken.priority == ScheduleToken.Priority.NORMAL or
           scheduleToken.priority == ScheduleToken.Priority.IMPORTANT or
           scheduleToken.priority == ScheduleToken.Priority.TOP)

    def isScheduleQueableToken(self, scheduleToken):
        return(scheduleToken.priority == ScheduleToken.Priority.RESERVE)
        