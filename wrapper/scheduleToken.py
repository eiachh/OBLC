from datetime import datetime


class ScheduleToken:
    class Priority:
        NORMAL = 'NORMAL_PRIORITY'  #Lowest priority, scheduler can reschedule                                  | Priority queue item
        IMPORTANT = 'IMPORTANT_PRIORITY' #One over NORMAL priority, scheduler can reschedule                    | Priority queue item
        TOP = 'TOP_PRIORITY' #Over NORMAL and IMPORTANT priority, scheduler can reschedule                      | Priority queue item
        RESERVE = 'RESERVE_PRIORITY' #Over NORMAL and IMPORTANT and TOP priority, scheduler CAN NOT RESCHEDULE  | SCHEDULE queue item
        EMERGENCY = 'EMERGENCY_PRIORITY' # Ignores all queues and all limitations, activates as soon as it is possible | QUEUE ignores

    def __init__(self, priority, logger, fromTime, tillTime = datetime.min):
        self.logger = logger

        if(not ScheduleToken.isValidPriority(priority)):
            logger.logWarn(f"priority: {priority} is not valid. Cancelling schedule token")
            return

        self.priority = priority

        if(type(fromTime) != type(datetime.now())):
            logger.logWarn(f"fromTime is not datetime type, current type is: {type(fromTime)}")
            return

        self.fromTime = fromTime

        if(type(tillTime) != type(datetime.now())):
            logger.logWarn(f"tillTime is not datetime type, current type is: {type(tillTime)}")
            return

        self.tillTime = tillTime

    def isValidPriority(priority):
        return(priority == ScheduleToken.Priority.NORMAL or
               priority == ScheduleToken.Priority.IMPORTANT or
               priority == ScheduleToken.Priority.TOP or
               priority == ScheduleToken.Priority.RESERVE or
               priority == ScheduleToken.Priority.EMERGENCY)


