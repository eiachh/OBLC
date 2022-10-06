from distutils.command.config import config
import json
from time import sleep
from time import sleep
import requests
import json

from Configuration import Configuration


class BuildingPipeline:  
    isRunning = False
    config = Configuration

    def __init__(self, interractor, logger, config):
        self.interractor = interractor
        self.logger = logger
        self.config = config

    def checkIfRequiredServiceIsAvailable(self):
        try:
            requests.get(self.config.RESOURCE_LIMITER_ADDR + '/ready')
            return True
        except Exception as e:
            self.logger.log(f'RESOURCE_LIMITER_ADDR service: {self.config.RESOURCE_LIMITER_ADDR} is not running', 'WARN')
            return False

    def resume(self):
        self.isRunning = True
        self.execPipeline()

    def pause(self):
        self.isRunning = False

    def execPipeline(self):
        if(not self.isRunning):
            return
        
        respPlanets = self.interractor.planets()
        for planet in respPlanets:
            planetID = planet['ID']
            self.executePipelineOnPlanetID(planetID)

        sleep(self.config.BUILD_PIPELINE_REACTIVATION)
        self.execPipeline()

    def gatherDataForLimiter(self, planetID):
        resources = self.interractor.resources(planetID)
        resourcesWithHeader =  {'resources': resources}

        facilities = self.interractor.facilities(planetID)
        facilitiesWithHeader =  {'facilities': facilities}

        #TODO FAKE DATA GET REAL
        fleetValueWIthHeader = {'fleetValue': 0}

        concatted = {**resourcesWithHeader, **facilitiesWithHeader, **fleetValueWIthHeader}
        return json.loads(json.dumps(concatted))

    def callResourceLimiter(self, planetID):
        data = self.gatherDataForLimiter(planetID)
        #data = {'resources': {'Metal': 5782, 'Crystal': 3452, 'Deuterium': 0, 'Energy': 117, 'Darkmatter': 0, 'Population': 210, 'Food': 10}, 'facilities': {'RoboticsFactory': 0, 'Shipyard': 0, 'ResearchLab': 0, 'AllianceDepot': 0, 'MissileSilo': 0, 'NaniteFactory': 0, 'Terraformer': 0, 'SpaceDock': 0, 'LunarBase': 0, 'SensorPhalanx': 0, 'JumpGate': 0}, 'fleetValue': 0}
        self.logger.log(f'Sending data to resource limiter: {data}', 'Info')
        return requests.get(self.config.RESOURCE_LIMITER_ADDR + '/get_allowances', json=data)

    def callBuildingManager(self, allowanceResponse):
        allowanceResources = json.loads(allowanceResponse.text)['allowanceResources']
        return requests.get(self.config.BUILDING_MANAGER_ADDR + '/get_prefered_building', json=allowanceResources)

    def executePipelineOnPlanetID(self, planetID):
        allowanceResourcesResponse = self.callResourceLimiter(planetID)
        self.logger.log(f'Resource limiter response was: {allowanceResourcesResponse}')
        #suggestedBuildingResponse = self.callBuildingManager(allowanceResourcesResponse)
        print('asd')
