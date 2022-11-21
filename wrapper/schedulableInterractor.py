from datetime import datetime
from wrapper.interractorWrapper import Interractor
import requests
import json
from flask import Flask,request
from wrapper.scheduleToken import ScheduleToken
from wrapper.scheduler import Scheduler

app = Flask(__name__)
isAppRunning = False
instance=None
restPort = 4999

class SchedulableInterractor(Interractor):
    def __init__(self, ip, port, logger):
        global instance
        super().__init__(ip,port)
        
        self.logger = logger
        self.scheduler = Scheduler(logger)

        instance = self
            
    def startRest():
        global app
        global isAppRunning
        if(not isAppRunning):
            isAppRunning = True
            instance.scheduler.startScheduler()
            app.run(host='0.0.0.0', port=restPort)

    def scheduleActionTemplate(func, dataDict):
        fromTime = dataDict.get('fromTime', str(datetime.min))
        fromTime = fromTime.split('.')[0]
        fromTime = datetime.strptime(fromTime, '%Y-%m-%d %H:%M:%S')

        tillTime = dataDict.get('tillTime', str(datetime.min))
        tillTime = tillTime.split('.')[0]
        tillTime = datetime.strptime(tillTime, '%Y-%m-%d %H:%M:%S')

        token = ScheduleToken(dataDict['priority'],func, instance.logger, params=dataDict, fromTime=fromTime, tillTime=tillTime)
        return instance.scheduler.scheduleAction(token)

    @app.route('/ready', methods=['GET'])
    def getReadiness():
        return "{Status: OK}"

    @app.route('/result', methods=['GET'])
    def getResultOfToken():
        uuid = json.loads(request.get_json())['Result']
        return instance.scheduler.getResultOf(uuid)

    @app.route('/galaxyInfo', methods=['GET'])
    def galaxyInfoRest():
        result = SchedulableInterractor.scheduleActionTemplate(instance.galaxyInfo, request.get_json())
        return {'Result':str(result.urn)}

    @app.route('/price', methods=['GET'])
    def priceRest():
        result = SchedulableInterractor.scheduleActionTemplate(instance.price, request.get_json())
        return {'Result':str(result.urn)}

    @app.route('/planetAtCoord', methods=['GET'])
    def planetAtCoordRest():
        result = SchedulableInterractor.scheduleActionTemplate(instance.planetAtCoord, request.get_json())
        return {'Result':str(result.urn)}

    @app.route('/planetById', methods=['GET'])
    def planetByIdRest():
        result = SchedulableInterractor.scheduleActionTemplate(instance.planetById, request.get_json())
        return {'Result':str(result.urn)}

    @app.route('/resourceSettings', methods=['GET'])
    def resourceSettingsRest():
        result = SchedulableInterractor.scheduleActionTemplate(instance.resourceSettings, request.get_json())
        return {'Result':str(result.urn)}

    @app.route('/resourceBuildings', methods=['GET'])
    def resourceBuildingsRest():
        result = SchedulableInterractor.scheduleActionTemplate(instance.resourceBuildings, request.get_json())
        return {'Result':str(result.urn)}

    @app.route('/ships', methods=['GET'])
    def shipsRest():
        result = SchedulableInterractor.scheduleActionTemplate(instance.ships, request.get_json())
        return {'Result':str(result.urn)}

    @app.route('/facilities', methods=['GET'])
    def facilitiesRest():
        result = SchedulableInterractor.scheduleActionTemplate(instance.facilities, request.get_json())
        return {'Result':str(result.urn)}

    @app.route('/production', methods=['GET'])
    def productionRest():
        result = SchedulableInterractor.scheduleActionTemplate(instance.production, request.get_json())
        return {'Result':str(result.urn)}

    @app.route('/constructionAndResearch', methods=['GET'])
    def constructionAndResearchRest():
        result = SchedulableInterractor.scheduleActionTemplate(instance.constructionAndResearch, request.get_json())
        return {'Result':str(result.urn)}

    @app.route('/resources', methods=['GET'])
    def resourcesRest():
        result = SchedulableInterractor.scheduleActionTemplate(instance.resources, request.get_json())
        return {'Result':str(result.urn)}

    #--------------------Parameterless------------------------------------------------------------
    #--------------------Parameterless------------------------------------------------------------
    #--------------------Parameterless------------------------------------------------------------

    @app.route('/isUnderAttack', methods=['GET'])
    def isUnderAttackRest():
        result = SchedulableInterractor.scheduleActionTemplate(instance.isUnderAttack, request.get_json())
        return {'Result':str(result.urn)}

    @app.route('/serverTime', methods=['GET'])
    def serverTimeRest():
        result = SchedulableInterractor.scheduleActionTemplate(instance.serverTime, request.get_json())
        return {'Result':str(result.urn)}

    @app.route('/userInfos', methods=['GET'])
    def userInfosRest():
        result = SchedulableInterractor.scheduleActionTemplate(instance.userInfos, request.get_json())
        return {'Result':str(result.urn)}

    @app.route('/fleets', methods=['GET'])
    def fleetsRest():
        result = SchedulableInterractor.scheduleActionTemplate(instance.fleets, request.get_json())
        return {'Result':str(result.urn)}

    @app.route('/ourAttacks', methods=['GET'])
    def ourAttacksRest():
        result = SchedulableInterractor.scheduleActionTemplate(instance.ourAttacks, request.get_json())
        return {'Result':str(result.urn)}

    @app.route('/planets', methods=['GET'])
    def planetsRest():
        result = SchedulableInterractor.scheduleActionTemplate(instance.planets, request.get_json())
        return {'Result':str(result.urn)}

    @app.route('/research', methods=['GET'])
    def researchRest():
        result = SchedulableInterractor.scheduleActionTemplate(instance.research, request.get_json())
        return {'Result':str(result.urn)}

    @app.route('/espionageReport', methods=['GET'])
    def espionageReportRest():
        result = SchedulableInterractor.scheduleActionTemplate(instance.espionageReport, request.get_json())
        return {'Result':str(result.urn)}
    
    #--------------------POST------------------------------------------------------------
    #--------------------POST------------------------------------------------------------
    #--------------------POST------------------------------------------------------------

    @app.route('/SendFleet', methods=['POST'])
    def POSTSendFleetRest():
        result = SchedulableInterractor.scheduleActionTemplate(instance.POSTSendFleet, request.get_json())
        return {'Result':str(result.urn)}

    @app.route('/build', methods=['POST'])
    def POSTbuildRest():
        result = SchedulableInterractor.scheduleActionTemplate(instance.POSTbuild, request.get_json())
        return {'Result':str(result.urn)}

    @app.route('/cancelBuild', methods=['POST'])
    def POSTcancelBuildRest():
        result = SchedulableInterractor.scheduleActionTemplate(instance.POSTcancelBuild, request.get_json())
        return {'Result':str(result.urn)}

    #--------------------REST OVER------------------------------------------------------------
    #--------------------REST OVER------------------------------------------------------------
    #--------------------REST OVER------------------------------------------------------------

    def __str__(self):
        return f"Schedulable interractor ,wrapped interractor addr: {self.ip}:{self.port}"

    def isSchedulable(self):
        return True

    def galaxyInfo(self, dataDict):
        return super().galaxyInfo(dataDict['galaxy'], dataDict['system'])

#hours := (metalCost + crystalCost) / (2500 * (1 + roboticLvl) * float64(universeSpeed) * math.Pow(2, naniteLvl))
    def price(self, dataDict):
        return super().price(dataDict['ogameID'], dataDict['nbr'])

    def planetAtCoord(self, dataDict):
        return super().planetAtCoord(dataDict['galaxy'], dataDict['system'], dataDict['position'])

    def planetById(self, dataDict):
        return super().planetById(dataDict['planetID'])

    #The operation %, eg all at 100% unless changed
    def resourceSettings(self, dataDict):
        return super().resourceSettings(dataDict['planetID'])

    def resourceBuildings(self, dataDict):
        return super().resourceBuildings(dataDict['planetID'])

    def ships(self, dataDict):
        return super().ships(dataDict['planetID'])

    def facilities(self, dataDict):
        return super().facilities(dataDict['planetID'])

    def production(self, dataDict):
        return super().production(dataDict['planetID'])

    def constructionAndResearch(self, dataDict):
        return super().constructionAndResearch(dataDict['planetID'])

    def resources(self, dataDict):
        return super().resources(dataDict['planetID'])

    #-d 'ships=204,1&ships=205,2&speed=10&galaxy=4&system=208&position=8&mission=3&metal=1&crystal=2&deuterium=3'
    def POSTSendFleet(self, dataDict):
        return super().POSTSendFleet(dataDict['planetID'], dataDict['fleetData'])
    
    def POSTbuild(self, dataDict):
        return super().POSTbuild(dataDict['planetID'], dataDict['objectToBuildOgameID'], dataDict['nbr'])

    def POSTcancelBuild(self, dataDict):
        return super().POSTcancelBuild(dataDict['planetID'], dataDict['objectToBuildOgameID'])

