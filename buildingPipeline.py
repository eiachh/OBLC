from distutils.command.config import config
import json
import math
from time import sleep
from time import sleep
import requests
import json
from common_lib.const import constants

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
        
        try:
            requests.get(self.config.PROGRESSION_MANAGER_ADDR + '/ready')
        except Exception as e:
            self.logger.log(f'PROGRESSION_MANAGER_ADDR service: {self.config.PROGRESSION_MANAGER_ADDR} is not running', 'WARN')
            return False

        try:
            requests.get(self.config.RESEARCH_MANAGER_ADDR + '/ready')
        except Exception as e:
            self.logger.log(f'RESEARCH_MANAGER_ADDR service: {self.config.RESEARCH_MANAGER_ADDR} is not running', 'WARN')
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

    def callProgressionManager(self, dataToSend):
        return requests.get(self.config.PROGRESSION_MANAGER_ADDR + '/get_progression_suggestion', json=dataToSend)

    def executePipelineOnPlanetID(self, planetID):

        allowanceResourcesJson = json.loads(self.callResourceLimiter(planetID).text)
        self.logger.log(f'Resource limiter response was: {allowanceResourcesJson}', 'Info')

        buildingLevelsAndPrices = self.getResourceBuildingPrices(planetID)
        concattedData = {**allowanceResourcesJson, **buildingLevelsAndPrices}

        self.logger.log(f'Sending data to buildingManager: {concattedData}', 'Info')
        buildManagerResponse = self.callBuildingManager(concattedData)
        suggestedBuildingResponse = json.loads(buildManagerResponse.text)
        self.logger.log(f'Recieved suggested building data: {suggestedBuildingResponse}', 'Info')
        
        facilityLevelsAndPrices = self.getFacilitiesPrices(planetID)
        researchLevelsAndPrices = self.getResearchPrices()
        concattedData = {**concattedData, **facilityLevelsAndPrices, **researchLevelsAndPrices}

        self.logger.log(f'Sending Data to progression manager: {concattedData}', 'Info')
        progressionManagerResponse = self.callProgressionManager(concattedData)

        self.logger.log(f'progression manager response before json: {progressionManagerResponse.text}', 'Info')
        progressionManagerResponseJson = json.loads(progressionManagerResponse.text)
        progressionManagerResponseJson = {'buildingManager' : progressionManagerResponseJson}

        concattedData = {**concattedData, **progressionManagerResponseJson}
        print("asdadas")
        print(concattedData)
        self.logger.log(f'progression manager resp: {progressionManagerResponseJson}', 'Info')

        #constructionResp = self.interractor.construction(planetID)

        ##GHETTO MANUEL PART
        #TODO FIX
        #if("Result" in suggestedBuildingResponse):
        #    print(f'Suggestion was: {suggestedBuildingResponse["Result"]}')
        #elif(constructionResp['BuildingCountdown'] == 0):
        #    self.logger.log(f'Sending POST build: {suggestedBuildingResponse["buildingID"]}/{suggestedBuildingResponse["buildingLevel"]}', 'Info')
        #    self.interractor.POSTbuild(planetID, suggestedBuildingResponse['buildingID'], suggestedBuildingResponse['buildingLevel'])

        print('End of building pipeline process')

    def getFacilitiesPrices(self, planetID):
        facilitiesDict = self.interractor.facilities(planetID)
        priceOFFacilitiesDict = dict(facilitiesDict)

        price = self.interractor.price(constants.ROBOT_FACTORY, priceOFFacilitiesDict[constants.ATTR_NAME_OF_ROBOT_FACTORY] + 1)
        priceOFFacilitiesDict[constants.ATTR_NAME_OF_ROBOT_FACTORY] = price

        price = self.interractor.price(constants.SHIPYARD, priceOFFacilitiesDict[constants.ATTR_NAME_OF_SHIPYARD] + 1)
        priceOFFacilitiesDict[constants.ATTR_NAME_OF_SHIPYARD] = price

        price = self.interractor.price(constants.RESEARCH_LAB, priceOFFacilitiesDict[constants.ATTR_NAME_OF_RESEARCH_LAB] + 1)
        priceOFFacilitiesDict[constants.ATTR_NAME_OF_RESEARCH_LAB] = price

        price = self.interractor.price(constants.MISSILE_SILO, priceOFFacilitiesDict[constants.ATTR_NAME_OF_MISSILE_SILO] + 1)
        priceOFFacilitiesDict[constants.ATTR_NAME_OF_MISSILE_SILO] = price

        price = self.interractor.price(constants.NANITE_FACTORY, priceOFFacilitiesDict[constants.ATTR_NAME_OF_NANITE_FACTORY] + 1)
        priceOFFacilitiesDict[constants.ATTR_NAME_OF_NANITE_FACTORY] = price

        price = self.interractor.price(constants.TERRAFORMER, priceOFFacilitiesDict[constants.ATTR_NAME_OF_TERRAFORMER] + 1)
        priceOFFacilitiesDict[constants.ATTR_NAME_OF_TERRAFORMER] = price

        return {'facilityLevels': facilitiesDict, 'facilityPrices': priceOFFacilitiesDict}

    def getResearchPrices(self):
        researchesDict = self.interractor.research()
        priceOFResearchesDict = dict(researchesDict)

        price = self.interractor.price(constants.ENERGY_TECH, priceOFResearchesDict[constants.ATTR_NAME_OF_ENERGY_TECH] + 1)
        priceOFResearchesDict[constants.ATTR_NAME_OF_ENERGY_TECH] = price

        price = self.interractor.price(constants.LASER_TECH, priceOFResearchesDict[constants.ATTR_NAME_OF_LASER_TECH] + 1)
        priceOFResearchesDict[constants.ATTR_NAME_OF_LASER_TECH] = price

        price = self.interractor.price(constants.ION_Tech, priceOFResearchesDict[constants.ATTR_NAME_OF_ION_Tech] + 1)
        priceOFResearchesDict[constants.ATTR_NAME_OF_ION_Tech] = price

        price = self.interractor.price(constants.HYPER_SPACE_TECH, priceOFResearchesDict[constants.ATTR_NAME_OF_HYPER_SPACE_TECH] + 1)
        priceOFResearchesDict[constants.ATTR_NAME_OF_HYPER_SPACE_TECH] = price

        price = self.interractor.price(constants.PLASMA_TECH, priceOFResearchesDict[constants.ATTR_NAME_OF_PLASMA_TECH] + 1)
        priceOFResearchesDict[constants.ATTR_NAME_OF_PLASMA_TECH] = price

        price = self.interractor.price(constants.COMBUSTION_DRIVE, priceOFResearchesDict[constants.ATTR_NAME_OF_COMBUSTION_DRIVE] + 1)
        priceOFResearchesDict[constants.ATTR_NAME_OF_COMBUSTION_DRIVE] = price

        price = self.interractor.price(constants.IMPULSE_DRIVE, priceOFResearchesDict[constants.ATTR_NAME_OF_IMPULSE_DRIVE] + 1)
        priceOFResearchesDict[constants.ATTR_NAME_OF_IMPULSE_DRIVE] = price

        price = self.interractor.price(constants.HYPERSPACE_DRIVE, priceOFResearchesDict[constants.ATTR_NAME_OF_HYPERSPACE_DRIVE] + 1)
        priceOFResearchesDict[constants.ATTR_NAME_OF_HYPERSPACE_DRIVE] = price

        price = self.interractor.price(constants.SPY_TECH, priceOFResearchesDict[constants.ATTR_NAME_OF_SPY_TECH] + 1)
        priceOFResearchesDict[constants.ATTR_NAME_OF_SPY_TECH] = price

        price = self.interractor.price(constants.COMPUTER_TECH, priceOFResearchesDict[constants.ATTR_NAME_OF_COMPUTER_TECH] + 1)
        priceOFResearchesDict[constants.ATTR_NAME_OF_COMPUTER_TECH] = price

        price = self.interractor.price(constants.ASTROPHYSICS, priceOFResearchesDict[constants.ATTR_NAME_OF_ASTROPHYSICS] + 1)
        priceOFResearchesDict[constants.ATTR_NAME_OF_ASTROPHYSICS] = price

        price = self.interractor.price(constants.INT_GAL_RESEARCH, priceOFResearchesDict[constants.ATTR_NAME_OF_INT_GAL_RESEARCH] + 1)
        priceOFResearchesDict[constants.ATTR_NAME_OF_INT_GAL_RESEARCH] = price

        price = self.interractor.price(constants.GRAVITON_TECH, priceOFResearchesDict[constants.ATTR_NAME_OF_GRAVITON_TECH] + 1)
        priceOFResearchesDict[constants.ATTR_NAME_OF_GRAVITON_TECH] = price

        price = self.interractor.price(constants.WEAPON_TECH, priceOFResearchesDict[constants.ATTR_NAME_OF_WEAPON_TECH] + 1)
        priceOFResearchesDict[constants.ATTR_NAME_OF_WEAPON_TECH] = price

        price = self.interractor.price(constants.SHIELD_TECH, priceOFResearchesDict[constants.ATTR_NAME_OF_SHIELD_TECH] + 1)
        priceOFResearchesDict[constants.ATTR_NAME_OF_SHIELD_TECH] = price

        price = self.interractor.price(constants.ARMOUR_TECH, priceOFResearchesDict[constants.ATTR_NAME_OF_ARMOUR_TECH] + 1)
        priceOFResearchesDict[constants.ATTR_NAME_OF_ARMOUR_TECH] = price

        return {'researchLevels': researchesDict, 'researchPrices': priceOFResearchesDict}

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

    def dummyDataSend(self):
        dummyData = "{'actualResources': {'Crystal': 10000, 'Darkmatter': 0, 'Deuterium': 10000, 'Energy': 220, 'Food': 10, 'Metal': 75000, 'Population': 210}, 'allowanceResources': {'Crystal': 10000, 'Deuterium': 10000, 'Metal': 75000}, 'allowanceShips': {'Crystal': 0, 'Deuterium': 0, 'Metal': 0}, 'buildingLevels': {'MetalMine': 13, 'CrystalMine': 11, 'DeuteriumSynthesizer': 7, 'SolarPlant': 15, 'FusionReactor': 0, 'SolarSatellite': 0, 'MetalStorage': 3, 'CrystalStorage': 0, 'DeuteriumTank': 0}, 'buildingPrices': {'MetalMine': {'Metal': 11677, 'Crystal': 2919, 'Deuterium': 0, 'Energy': 72, 'Darkmatter': 0, 'Population': 0, 'Food': 0}, 'CrystalMine': {'Metal': 8444, 'Crystal': 4222, 'Deuterium': 0, 'Energy': 55, 'Darkmatter': 0, 'Population': 0, 'Food': 0}, 'DeuteriumSynthesizer': {'Metal': 3844, 'Crystal': 1281, 'Deuterium': 0, 'Energy': 60, 'Darkmatter': 0, 'Population': 0, 'Food': 0}, 'SolarPlant': {'Metal': 32842, 'Crystal': 13136, 'Deuterium': 0, 'Energy': 0, 'Darkmatter': 0, 'Population': 0, 'Food': 0}, 'FusionReactor': {'Metal': 900, 'Crystal': 360, 'Deuterium': 180, 'Energy': 0, 'Darkmatter': 0, 'Population': 0, 'Food': 0}, 'SolarSatellite': {'Metal': 0, 'Crystal': 2000, 'Deuterium': 500, 'Energy': 0, 'Darkmatter': 0, 'Population': 0, 'Food': 0}, 'MetalStorage': {'Metal': 8000, 'Crystal': 0, 'Deuterium': 0, 'Energy': 0, 'Darkmatter': 0, 'Population': 0, 'Food': 0}, 'CrystalStorage': {'Metal': 1000, 'Crystal': 500, 'Deuterium': 0, 'Energy': 0, 'Darkmatter': 0, 'Population': 0, 'Food': 0}, 'DeuteriumTank': {'Metal': 1000, 'Crystal': 1000, 'Deuterium': 0, 'Energy': 0, 'Darkmatter': 0, 'Population': 0, 'Food': 0}}, 'facilityLevels': {'RoboticsFactory': 0, 'Shipyard': 0, 'ResearchLab': 0, 'AllianceDepot': 0, 'MissileSilo': 0, 'NaniteFactory': 0, 'Terraformer': 0, 'SpaceDock': 0, 'LunarBase': 0, 'SensorPhalanx': 0, 'JumpGate': 0}, 'facilityPrices': {'RoboticsFactory': {'Metal': 400, 'Crystal': 120, 'Deuterium': 200, 'Energy': 0, 'Darkmatter': 0, 'Population': 0, 'Food': 0}, 'Shipyard': {'Metal': 400, 'Crystal': 200, 'Deuterium': 100, 'Energy': 0, 'Darkmatter': 0, 'Population': 0, 'Food': 0}, 'ResearchLab': {'Metal': 200, 'Crystal': 400, 'Deuterium': 200, 'Energy': 0, 'Darkmatter': 0, 'Population': 0, 'Food': 0}, 'AllianceDepot': 0, 'MissileSilo': {'Metal': 20000, 'Crystal': 20000, 'Deuterium': 1000, 'Energy': 0, 'Darkmatter': 0, 'Population': 0, 'Food': 0}, 'NaniteFactory': {'Metal': 1000000, 'Crystal': 500000, 'Deuterium': 100000, 'Energy': 0, 'Darkmatter': 0, 'Population': 0, 'Food': 0}, 'Terraformer': {'Metal': 0, 'Crystal': 50000, 'Deuterium': 100000, 'Energy': 1000, 'Darkmatter': 0, 'Population': 0, 'Food': 0}, 'SpaceDock': 0, 'LunarBase': 0, 'SensorPhalanx': 0, 'JumpGate': 0}, 'researchLevels': {'EnergyTechnology': 0, 'LaserTechnology': 0, 'IonTechnology': 0, 'HyperspaceTechnology': 0, 'PlasmaTechnology': 0, 'CombustionDrive': 0, 'ImpulseDrive': 0, 'HyperspaceDrive': 0, 'EspionageTechnology': 0, 'ComputerTechnology': 0, 'Astrophysics': 0, 'IntergalacticResearchNetwork': 0, 'GravitonTechnology': 0, 'WeaponsTechnology': 0, 'ShieldingTechnology': 0, 'ArmourTechnology': 0}, 'researchPrices': {'EnergyTechnology': {'Metal': 0, 'Crystal': 800, 'Deuterium': 400, 'Energy': 0, 'Darkmatter': 0, 'Population': 0, 'Food': 0}, 'LaserTechnology': {'Metal': 200, 'Crystal': 100, 'Deuterium': 0, 'Energy': 0, 'Darkmatter': 0, 'Population': 0, 'Food': 0}, 'IonTechnology': {'Metal': 1000, 'Crystal': 300, 'Deuterium': 100, 'Energy': 0, 'Darkmatter': 0, 'Population': 0, 'Food': 0}, 'HyperspaceTechnology': {'Metal': 0, 'Crystal': 4000, 'Deuterium': 2000, 'Energy': 0, 'Darkmatter': 0, 'Population': 0, 'Food': 0}, 'PlasmaTechnology': {'Metal': 2000, 'Crystal': 4000, 'Deuterium': 1000, 'Energy': 0, 'Darkmatter': 0, 'Population': 0, 'Food': 0}, 'CombustionDrive': {'Metal': 400, 'Crystal': 0, 'Deuterium': 600, 'Energy': 0, 'Darkmatter': 0, 'Population': 0, 'Food': 0}, 'ImpulseDrive': {'Metal': 2000, 'Crystal': 4000, 'Deuterium': 600, 'Energy': 0, 'Darkmatter': 0, 'Population': 0, 'Food': 0}, 'HyperspaceDrive': {'Metal': 10000, 'Crystal': 20000, 'Deuterium': 6000, 'Energy': 0, 'Darkmatter': 0, 'Population': 0, 'Food': 0}, 'EspionageTechnology': {'Metal': 200, 'Crystal': 1000, 'Deuterium': 200, 'Energy': 0, 'Darkmatter': 0, 'Population': 0, 'Food': 0}, 'ComputerTechnology': {'Metal': 0, 'Crystal': 400, 'Deuterium': 600, 'Energy': 0, 'Darkmatter': 0, 'Population': 0, 'Food': 0}, 'Astrophysics': {'Metal': 4000, 'Crystal': 8000, 'Deuterium': 4000, 'Energy': 0, 'Darkmatter': 0, 'Population': 0, 'Food': 0}, 'IntergalacticResearchNetwork': {'Metal': 240000, 'Crystal': 400000, 'Deuterium': 160000, 'Energy': 0, 'Darkmatter': 0, 'Population': 0, 'Food': 0}, 'GravitonTechnology': {'Metal': 0, 'Crystal': 0, 'Deuterium': 0, 'Energy': 300000, 'Darkmatter': 0, 'Population': 0, 'Food': 0}, 'WeaponsTechnology': {'Metal': 800, 'Crystal': 200, 'Deuterium': 0, 'Energy': 0, 'Darkmatter': 0, 'Population': 0, 'Food': 0}, 'ShieldingTechnology': {'Metal': 200, 'Crystal': 600, 'Deuterium': 0, 'Energy': 0, 'Darkmatter': 0, 'Population': 0, 'Food': 0}, 'ArmourTechnology': {'Metal': 1000, 'Crystal': 0, 'Deuterium': 0, 'Energy': 0, 'Darkmatter': 0, 'Population': 0, 'Food': 0}}}"
        progressionManagerResponse = self.callProgressionManager(dummyData)
        print("asdasdad")

