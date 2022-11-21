from datetime import datetime, timedelta
from time import sleep
import uuid
from common_lib.const import Priority
from wrapper.scheduleToken import ScheduleToken
from random import randrange
from datetime import timedelta
import random

from threading import Timer

class RepeatedTimer(object):
    def __init__(self, intervalFunc, function, *args, **kwargs):
        self._timer     = None
        self.getIntervalFunc   = intervalFunc
        self.function   = function
        self.args       = args
        self.kwargs     = kwargs
        self.is_running = False
        self.start()

    def _run(self):
        self.is_running = False
        self.start()
        self.function(*self.args, **self.kwargs)

    def start(self):
        if not self.is_running:
            self._timer = Timer(self.getIntervalFunc(), self._run)
            self._timer.start()
            self.is_running = True

    def stop(self):
        self._timer.cancel()
        self.is_running = False

class Scheduler:

    SCHEDULE_QUEUE_STALL_INTERVAL = 10
    SCHEDULED_QUEUE_RECHECK_DEFAULT_INTERVAL = 4
    RESULT_LIST_TIMEOT_INTERVAL = 600

    PRIORITY_QUEUE_RECHECK_MIN = 1
    PRIORITY_QUEUE_RECHECK_MAX = 3

    def __init__(self, logger):
        self.logger = logger
        self.NormalQueue = []
        self.ImportantQueue = []
        self.TopQueue = []

        self.ScheduledQueue = []

        self.ResultDict = {}        

    def startScheduler(self):
        self.scheduledQueueConsumer = RepeatedTimer(Scheduler.getScheduledQueueRecheckInterval, self.iterateScheduledQueue)
        self.priorityQueueConsumer = RepeatedTimer(Scheduler.getPriorityQueueRecheckInterval, self.iteratePriorityQueue)

    def getScheduledQueueRecheckInterval():
        return Scheduler.SCHEDULED_QUEUE_RECHECK_DEFAULT_INTERVAL

    def getPriorityQueueRecheckInterval():
        return random.randint(Scheduler.PRIORITY_QUEUE_RECHECK_MIN,Scheduler.PRIORITY_QUEUE_RECHECK_MAX)

    def scheduleAction(self, scheduleToken):
        if( not (isinstance(scheduleToken, ScheduleToken))):
            self.logger.logWarn(f"Schedule token invalid, current token type: {type(scheduleToken)}")
            return
        actionUuid = uuid.uuid1().urn

        if(scheduleToken.priority == Priority.EMERGENCY):
            self.executeToken(scheduleToken)
        elif(self.isNormalQueableToken(scheduleToken)):
            self.appendPriorityQueue(scheduleToken, actionUuid)
        elif(self.isScheduleQueableToken(scheduleToken)):
            self.appendScheduleQueue(scheduleToken, actionUuid)

        return actionUuid

    def getResultOf(self, uuid):
        for uuidKey in self.ResultDict:
            if(uuid == uuidKey):
                copiedDict = self.ResultDict[uuid].copy()
                copiedDict['Created'] = str(copiedDict['Created'])
                return copiedDict
        
        queuePosition = 0
        for scheduledItem in self.ScheduledQueue:
            if(scheduledItem['uuid'] == uuid):
                return self.createQueueResultItem(queuePosition)
            queuePosition=queuePosition+1

        queuePosition = 0
        for queuedItem in self.TopQueue:
            if(queuedItem['uuid'] == uuid):
                return self.createQueueResultItem(queuePosition)
            queuePosition=queuePosition+1
        for queuedItem in self.ImportantQueue:
            if(queuedItem['uuid'] == uuid):
                return self.createQueueResultItem(queuePosition)
            queuePosition=queuePosition+1
        for queuedItem in self.NormalQueue:
            if(queuedItem['uuid'] == uuid):
                return self.createQueueResultItem(queuePosition)
            queuePosition=queuePosition+1

        return {'Result': 'Not found'}

    def createQueueResultItem(self, queuePosition):
        return {'Completed': False, 'Result': f'Queue position:{queuePosition}' }

    def isNormalQueableToken(self, scheduleToken):
        return(scheduleToken.priority == Priority.NORMAL or
           scheduleToken.priority == Priority.IMPORTANT or
           scheduleToken.priority == Priority.TOP)

    def isScheduleQueableToken(self, scheduleToken):
        return(scheduleToken.priority == Priority.RESERVE)

    def appendPriorityQueue(self, scheduleToken, uuid):
        if(scheduleToken.priority == Priority.NORMAL):
            self.NormalQueue.append(Scheduler.createQueueItem(scheduleToken, uuid))
        elif(scheduleToken.priority == Priority.IMPORTANT):
            self.ImportantQueue.append(Scheduler.createQueueItem(scheduleToken, uuid))
        elif(scheduleToken.priority == Priority.TOP):
            self.TopQueue.append(Scheduler.createQueueItem(scheduleToken, uuid))

    def appendScheduleQueue(self, scheduleToken, uuid):
        scheduledTime = Scheduler.getRandomDate(scheduleToken.fromTime, scheduleToken.tillTime)
        scheduleToken.fromTime = scheduledTime
        scheduleToken.tillTime = scheduledTime

        for i in range(len(self.ScheduledQueue)):
            if(self.ScheduledQueue[i]['token'].fromTime > scheduleToken.fromTime):
                self.ScheduledQueue.insert(i, Scheduler.createQueueItem(scheduleToken, uuid))
                return

        self.ScheduledQueue.append(Scheduler.createQueueItem(scheduleToken, uuid))

    def getRandomDate(start, end):
        if(start == end):
            return start

        delta = end - start
        int_delta = (delta.days * 24 * 60 * 60) + delta.seconds
        random_second = randrange(int_delta)
        return start + timedelta(seconds=random_second)

    def createQueueItem(scheduleToken, uuid):
        return {'token': scheduleToken, 'uuid': uuid}

    def executeToken(self, scheduleToken):
        actionResult = scheduleToken['token'].action(scheduleToken['token'].params)
        self.logger.logMinorInfo(f'Token action result: {actionResult}')
        return actionResult

    def createActionResultDict(self, scheduleDictElem, actionResult):
        uuid = scheduleDictElem['uuid']
        element = {'Completed': True, 'Result': actionResult, 'Created': datetime.now() }
        self.ResultDict[uuid] = element
        self.removeTimedOutResults()

    def createBeingProcessedResultDict(self, scheduleDictElem):
        uuid = scheduleDictElem['uuid']
        element = {'Completed': False, 'Result': f'Queue position:{0}', 'Created': -1 }
        self.ResultDict[uuid] = element
        
    def removeTimedOutResults(self):
        timedOutResults = []
        
        for key in self.ResultDict.keys():
            if(self.ResultDict[key]['Created'] == -1):
                continue

            elapsed = (datetime.now() - self.ResultDict[key]['Created']).total_seconds()
            if(elapsed > Scheduler.RESULT_LIST_TIMEOT_INTERVAL):
                timedOutResults.append(key)
        
        for timedOutKey in timedOutResults:
            del self.ResultDict[timedOutKey]

    def iterateScheduledQueue(self):
        if(len(self.ScheduledQueue) == 0):
            return

        now = datetime.now()

        scheduledDict = self.ScheduledQueue[0]
        scheduledToken = scheduledDict['token']
        diffInSec = (scheduledToken.fromTime - now).total_seconds()

        if(diffInSec < 0):
            self.logger.logError(f'The scheduler failed to execute task in time. Scheduled time: {scheduledToken.fromTime}, now: {now}, action uuid: {scheduledDict["uuid"]} aborting action.')
            return

        if(diffInSec < Scheduler.SCHEDULE_QUEUE_STALL_INTERVAL):
            self.logger.logMinorInfo(f'Found scheduled token at {datetime.now()} token scheduled for: {scheduledToken.fromTime}. WAITING: {diffInSec} seconds')
            self.createBeingProcessedResultDict(scheduledDict)
            self.ScheduledQueue.remove(scheduledDict)
            sleep(diffInSec)
            actionResult = self.executeToken(scheduledDict)
            self.createActionResultDict(scheduledDict, actionResult)
            self.iterateScheduledQueue()

    def iteratePriorityQueue(self):
        print(f"Iterating on normal queue. Current time {datetime.now()}")
        queueElementDict = None
        if(len(self.TopQueue) > 0):
            queueElementDict = self.TopQueue[0]
        elif(len(self.ImportantQueue) > 0):
            queueElementDict = self.ImportantQueue[0]
        elif(len(self.NormalQueue) > 0):
            queueElementDict = self.NormalQueue[0]

        if(queueElementDict == None):
            return
        
        priority = queueElementDict['token'].priority
        self.createBeingProcessedResultDict(queueElementDict)

        if(priority == Priority.TOP):
            self.TopQueue.remove(queueElementDict)
        elif(priority == Priority.IMPORTANT):
            self.ImportantQueue.remove(queueElementDict)
        elif(priority == Priority.NORMAL):
            self.NormalQueue.remove(queueElementDict)

        actionResult = self.executeToken(queueElementDict)
        self.createActionResultDict(queueElementDict, actionResult)


        
    