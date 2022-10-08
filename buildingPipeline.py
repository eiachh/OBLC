from distutils.command.config import config
import json
import math
from time import sleep
from time import sleep
import requests
import json
from const import constants

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
        except Exception as e:
            self.logger.log(f'RESOURCE_LIMITER_ADDR service: {self.config.RESOURCE_LIMITER_ADDR} is not running', 'WARN')
            return False

        try:
            requests.get(self.config.BUILDING_MANAGER_ADDR + '/ready')
        except Exception as e:
            self.logger.log(f'BUILDING_MANAGER_ADDR service: {self.config.BUILDING_MANAGER_ADDR} is not running', 'WARN')
            return False
        return True

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
        self.logger.log(f'Sending data to resource limiter: {data}', 'Info')
        return requests.get(self.config.RESOURCE_LIMITER_ADDR + '/get_allowances', json=data)

    def callBuildingManager(self, dataToSend):
        
        return requests.get(self.config.BUILDING_MANAGER_ADDR + '/get_prefered_building', json=dataToSend)

    def executePipelineOnPlanetID(self, planetID):
        allowanceResourcesJson = json.loads(self.callResourceLimiter(planetID).text)
        self.logger.log(f'Resource limiter response was: {allowanceResourcesJson}', 'Info')

        buildingLevelsAndPrices = self.getResourceBuildingPrices(planetID)
        concattedData = {**allowanceResourcesJson, **buildingLevelsAndPrices}
        
        self.logger.log(f'Sending data to buildingManager: {concattedData}', 'Info')
        buildManagerResponse = self.callBuildingManager(concattedData)
        suggestedBuildingResponse = json.loads(buildManagerResponse.text)
        self.logger.log(f'Recieved suggested building data: {suggestedBuildingResponse}', 'Info')

        constructionResp = self.interractor.construction(planetID)

        ##GHETTO MANUEL PART
        #TODO FIX
        if("Result" in suggestedBuildingResponse):
            print(f'Suggestion was: {suggestedBuildingResponse["Result"]}')
        elif(constructionResp['BuildingCountdown'] == 0):
            self.logger.log(f'Sending POST build: {suggestedBuildingResponse["buildingID"]}/{suggestedBuildingResponse["buildingLevel"]}', 'Info')
            self.interractor.POSTbuild(planetID, suggestedBuildingResponse['buildingID'], suggestedBuildingResponse['buildingLevel'])

        print('asd')

    def getResourceBuildingPrices(self, planetID):
            resourceBuildingsDict = self.interractor.resourceBuildings(planetID)
            priceOFResourceBuildingsDict = dict(resourceBuildingsDict)

            levelOfMetalMine = resourceBuildingsDict[constants.ATTR_NAME_OF_METAL_MINE]
            prevLevelOfMetalMine = levelOfMetalMine - 1
            energyConsumptMetalMine = round(10*levelOfMetalMine*1.1**levelOfMetalMine) - round(10*prevLevelOfMetalMine*1.1**prevLevelOfMetalMine)
            priceOfMetalMine = self.interractor.price(constants.METAL_MINE, priceOFResourceBuildingsDict[constants.ATTR_NAME_OF_METAL_MINE] + 1)
            priceOfMetalMine['Energy'] = energyConsumptMetalMine
            priceOFResourceBuildingsDict[constants.ATTR_NAME_OF_METAL_MINE] = priceOfMetalMine


            levelOfCrystalMine = resourceBuildingsDict[constants.ATTR_NAME_OF_CRYSTAL_MINE]
            prevLevelOfCrystalMine = levelOfCrystalMine - 1
            energyConsumptCrystalMine = round(10*levelOfCrystalMine*1.1**levelOfCrystalMine) - round(10*prevLevelOfCrystalMine*1.1**prevLevelOfCrystalMine)
            priceOfCrystalMine = self.interractor.price(constants.CRYSTAL_MINE, priceOFResourceBuildingsDict[constants.ATTR_NAME_OF_CRYSTAL_MINE] + 1)
            priceOfCrystalMine['Energy'] = energyConsumptCrystalMine
            priceOFResourceBuildingsDict[constants.ATTR_NAME_OF_CRYSTAL_MINE] = priceOfCrystalMine

            levelOfDeuMine = resourceBuildingsDict[constants.ATTR_NAME_OF_DEU_MINE]
            prevLevelOfDeuMine = levelOfDeuMine - 1
            energyConsumptDeuMine = round(20*levelOfDeuMine*1.1**levelOfDeuMine) - round(20*prevLevelOfDeuMine*1.1**prevLevelOfDeuMine)
            priceOfDeuMine = self.interractor.price(constants.DEU_MINE, priceOFResourceBuildingsDict[constants.ATTR_NAME_OF_DEU_MINE] + 1)
            priceOfDeuMine['Energy'] = energyConsumptDeuMine
            priceOFResourceBuildingsDict[constants.ATTR_NAME_OF_DEU_MINE] = priceOfDeuMine

            priceOfSolarPlant = self.interractor.price(constants.SOLAR_PLANT, priceOFResourceBuildingsDict[constants.ATTR_NAME_OF_SOLAR_PLANT] + 1)
            priceOFResourceBuildingsDict[constants.ATTR_NAME_OF_SOLAR_PLANT] = priceOfSolarPlant

            priceOfFusionReactor = self.interractor.price(constants.FUSION_REACTOR, priceOFResourceBuildingsDict[constants.ATTR_NAME_OF_FUSION_REACTOR] + 1)
            priceOFResourceBuildingsDict[constants.ATTR_NAME_OF_FUSION_REACTOR] = priceOfFusionReactor

            priceOfSolarSatellite = self.interractor.price(constants.SOLAR_SATELLITE, priceOFResourceBuildingsDict[constants.ATTR_NAME_OF_SOLAR_SATELLITE] + 1)
            priceOFResourceBuildingsDict[constants.ATTR_NAME_OF_SOLAR_SATELLITE] = priceOfSolarSatellite

            priceOfMetalStorage = self.interractor.price(constants.METAL_STORAGE, priceOFResourceBuildingsDict[constants.ATTR_NAME_OF_METAL_STORAGE] + 1)
            priceOFResourceBuildingsDict[constants.ATTR_NAME_OF_METAL_STORAGE] = priceOfMetalStorage

            priceOfCrystalStorage = self.interractor.price(constants.CRYSTAL_STORAGE, priceOFResourceBuildingsDict[constants.ATTR_NAME_OF_CRYSTAL_STORAGE] + 1)
            priceOFResourceBuildingsDict[constants.ATTR_NAME_OF_CRYSTAL_STORAGE] = priceOfCrystalStorage

            priceOfDeuStorage = self.interractor.price(constants.DEU_STORAGE, priceOFResourceBuildingsDict[constants.ATTR_NAME_OF_DEU_STORAGE] + 1)
            priceOFResourceBuildingsDict[constants.ATTR_NAME_OF_DEU_STORAGE] = priceOfDeuStorage

            return {'buildingLevels': resourceBuildingsDict, 'buildingPrices': priceOFResourceBuildingsDict}
