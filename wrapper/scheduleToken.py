from datetime import datetime
from common_lib.const import Priority

class ScheduleToken:
    def __init__(self, priority, action, logger, fromTime = datetime.min, tillTime = datetime.min, params=None):
        self.logger = logger
        self.action = action
        self.params = params

        if(not ScheduleToken.isValidPriority(priority)):
            logger.logWarn(f"priority: {priority} is not valid. Cancelling schedule token")
            return

        self.priority = priority

        if(not isinstance(fromTime, datetime)):
            logger.logWarn(f"fromTime is not datetime type, current type is: {type(fromTime)}")
            return

        self.fromTime = fromTime

        if(not isinstance(tillTime, datetime)):
            logger.logWarn(f"tillTime is not datetime type, current type is: {type(tillTime)}")
            return
            
        if(tillTime == datetime.min):
            tillTime = self.fromTime

        self.tillTime = tillTime

    def isValidPriority(priority):
        return(priority == Priority.NORMAL or
               priority == Priority.IMPORTANT or
               priority == Priority.TOP or
               priority == Priority.RESERVE or
               priority == Priority.EMERGENCY)


