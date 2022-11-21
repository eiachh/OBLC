import json
from time import sleep
import requests
import json

from common_lib.const import constants
from common_lib.utilities import utilities
from common_lib.const import Priority

from Configuration import Configuration
from wrapper.schedulableInterractor import SchedulableInterractor
from wrapper.scheduleToken import ScheduleToken


class BuildingPipeline:  
    isRunning = False
    config = Configuration

    def __init__(self, scheduler, interractor, logger, config):
        self.scheduler = scheduler
        self.interractor = interractor
        self.logger = logger
        self.config = config

    def checkIfRequiredServiceIsAvailable(self):
        try:
            requests.get(self.config.RESOURCE_LIMITER_ADDR + '/ready')
        except Exception as e:
            self.logger.logWarn(f'RESOURCE_LIMITER_ADDR service: {self.config.RESOURCE_LIMITER_ADDR} is not running')
            return False

        try:
            requests.get(self.config.BUILDING_MANAGER_ADDR + '/ready')
        except Exception as e:
            self.logger.logWarn(f'BUILDING_MANAGER_ADDR service: {self.config.BUILDING_MANAGER_ADDR} is not running')
            return False
        
        try:
            requests.get(self.config.PROGRESSION_MANAGER_ADDR + '/ready')
        except Exception as e:
            self.logger.logWarn(f'PROGRESSION_MANAGER_ADDR service: {self.config.PROGRESSION_MANAGER_ADDR} is not running')
            return False

        try:
            requests.get(self.config.RESEARCH_MANAGER_ADDR + '/ready')
        except Exception as e:
            self.logger.logWarn(f'RESEARCH_MANAGER_ADDR service: {self.config.RESEARCH_MANAGER_ADDR} is not running')
            return False
            
        try:
            requests.get(self.config.INVESTMENT_MANAGER_ADDR + '/ready')
        except Exception as e:
            self.logger.logWarn(f'INVESTMENT_MANAGER_ADDR service: {self.config.INVESTMENT_MANAGER_ADDR} is not running')
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

    def callResourceLimiter(self, dataToSend):
        return requests.get(self.config.RESOURCE_LIMITER_ADDR + '/get_allowances', json=dataToSend)

    def callBuildingManager(self, dataToSend):
        return requests.get(self.config.BUILDING_MANAGER_ADDR + '/get_prefered_building', json=dataToSend)

    def callProgressionManager(self, dataToSend):
        return requests.get(self.config.PROGRESSION_MANAGER_ADDR + '/get_progression_suggestion', json=dataToSend)

    def callResearchManager(self, dataToSend):
        return requests.get(self.config.RESEARCH_MANAGER_ADDR + '/get_preferred_research', json=dataToSend)

    def callInvestmentManager(self, dataToSend):
        return requests.get(self.config.INVESTMENT_MANAGER_ADDR + '/get_investment', json=dataToSend)

    def waitTillActionsCompleted(self, actionList):
        completed = False
        while(not completed):
            completed = True
            for actionUuidStr in actionList:
                if(self.scheduler.getResultOf(actionUuidStr)['Completed'] == False):
                    completed = False
            sleep(5)
        actionList.clear()

    def executePipelineOnPlanetID(self, planetID):
        concattedData = self.gatherDataForPlanet(planetID)

        allowanceResourcesJson = json.loads(self.callResourceLimiter(concattedData).text)
        concattedData = {**concattedData, **allowanceResourcesJson}

        buildingManagerResponse = {'buildingManager' : json.loads(self.callBuildingManager(concattedData).text)}
        progressionManagerResponse = {'progressionManager' : json.loads(self.callProgressionManager(concattedData).text)}
        researchManagerRespJson = json.loads(self.callResearchManager(concattedData).text)

        concattedData = {**concattedData, **buildingManagerResponse, **progressionManagerResponse, **researchManagerRespJson}

        investmentManagerResp = self.callInvestmentManager(concattedData)
        investmentManagerRespJson = json.loads(investmentManagerResp.text)

        self.logger.logMainInfo(f'-----------------------------------------')
        sleep(1)
        self.logger.logMainInfo(f'RESOURCE LIMITER: {allowanceResourcesJson}')
        sleep(1)
        self.logger.logMainInfo(f'BUILDING MANAGER: {buildingManagerResponse}')
        sleep(1)
        self.logger.logMainInfo(f'RESEARCH MANAGER: {researchManagerRespJson}')
        sleep(1)
        self.logger.logMainInfo(f'PROG MANAGER: {progressionManagerResponse}')
        sleep(1)
        self.logger.logMainInfo(f'INV MANAGER: {investmentManagerRespJson}')
        sleep(1)

        self.executeInvestmentManagerCommand(investmentManagerRespJson, planetID)

        self.logger.logMainInfo('End of building pipeline process')

    def executeInvestmentManagerCommand(self, investmentManCmd, planetID):
        invManInner = investmentManCmd['investmentManager']
        buildingID = invManInner['constructable']['buildingID']
        researchID = invManInner['researchable']['researchID']
        if(buildingID != -1):
            self.logger.logMainInfo(f"```Building {constants.convertOgameIDToAttrName(buildingID)} to level: {invManInner['constructable']['buildingLevel']}```")
            self.interractor.POSTbuild(planetID, buildingID, invManInner['constructable']['buildingLevel'])
        if(researchID != -1):
            self.interractor.POSTbuild(planetID, researchID, invManInner['researchable']['researchLevel'])
            self.logger.logMainInfo(f"```Building {constants.convertOgameIDToAttrName(researchID)} to level: {invManInner['researchable']['researchLevel']}```")

    def gatherDataForPlanet(self, planetID):
        actionUuidList = []
        
        uuidOfResources = self.scheduler.scheduleAction(ScheduleToken(Priority.NORMAL, self.interractor.resources, self.logger, params={'planetID': planetID}))
        uuidOfBuildings = self.scheduler.scheduleAction(ScheduleToken(Priority.NORMAL, self.interractor.resourceBuildings, self.logger, params={'planetID': planetID}))
        uuidOfFacilities = self.scheduler.scheduleAction(ScheduleToken(Priority.NORMAL, self.interractor.facilities, self.logger, params={'planetID': planetID}))
        uuidOfResearch = self.scheduler.scheduleAction(ScheduleToken(Priority.NORMAL, self.interractor.research, self.logger, params={'planetID': planetID}))
        uuidOfOngoingConstAndResearch = self.scheduler.scheduleAction(ScheduleToken(Priority.NORMAL, self.interractor.constructionAndResearch, self.logger, params={'planetID': planetID}))

        actionUuidList.append(uuidOfResources)
        actionUuidList.append(uuidOfBuildings)
        actionUuidList.append(uuidOfFacilities)
        actionUuidList.append(uuidOfResearch)
        actionUuidList.append(uuidOfOngoingConstAndResearch)

        self.waitTillActionsCompleted(actionUuidList)

        resourcesDict = self.scheduler.getResultOf(uuidOfResources)['Result']
        buildingLevelsDict = self.scheduler.getResultOf(uuidOfBuildings)['Result']
        facilityLevelsDict = self.scheduler.getResultOf(uuidOfFacilities)['Result']
        researchLevelsDict = self.scheduler.getResultOf(uuidOfResearch)['Result']
        ongoingConstAndResearchDict = self.scheduler.getResultOf(uuidOfOngoingConstAndResearch)['Result']

        uuidOfMetalMinePrice = self.scheduler.scheduleAction(ScheduleToken(Priority.NORMAL, self.interractor.price, self.logger, params={'ogameID': constants.METAL_MINE, 'nbr':buildingLevelsDict[constants.ATTR_NAME_OF_METAL_MINE]+1}))
        uuidOfCrystalMinePrice = self.scheduler.scheduleAction(ScheduleToken(Priority.NORMAL, self.interractor.price, self.logger, params={'ogameID': constants.CRYSTAL_MINE, 'nbr':buildingLevelsDict[constants.ATTR_NAME_OF_CRYSTAL_MINE]+1}))
        uuidOfDeuMinePrice = self.scheduler.scheduleAction(ScheduleToken(Priority.NORMAL, self.interractor.price, self.logger, params={'ogameID': constants.DEU_MINE, 'nbr':buildingLevelsDict[constants.ATTR_NAME_OF_DEU_MINE]+1}))
        uuidOfSolarPlantPrice = self.scheduler.scheduleAction(ScheduleToken(Priority.NORMAL, self.interractor.price, self.logger, params={'ogameID': constants.SOLAR_PLANT, 'nbr':buildingLevelsDict[constants.ATTR_NAME_OF_SOLAR_PLANT]+1}))
        uuidOfFusionReactorPrice = self.scheduler.scheduleAction(ScheduleToken(Priority.NORMAL, self.interractor.price, self.logger, params={'ogameID': constants.FUSION_REACTOR, 'nbr':buildingLevelsDict[constants.ATTR_NAME_OF_FUSION_REACTOR]+1}))
        uuidOfMetalStoragePrice = self.scheduler.scheduleAction(ScheduleToken(Priority.NORMAL, self.interractor.price, self.logger, params={'ogameID': constants.METAL_STORAGE, 'nbr':buildingLevelsDict[constants.ATTR_NAME_OF_METAL_STORAGE]+1}))
        uuidOfCrystalStoragePrice = self.scheduler.scheduleAction(ScheduleToken(Priority.NORMAL, self.interractor.price, self.logger, params={'ogameID': constants.CRYSTAL_STORAGE, 'nbr':buildingLevelsDict[constants.ATTR_NAME_OF_CRYSTAL_STORAGE]+1}))
        uuidOfDeuStoragePrice = self.scheduler.scheduleAction(ScheduleToken(Priority.NORMAL, self.interractor.price, self.logger, params={'ogameID': constants.DEU_STORAGE, 'nbr':buildingLevelsDict[constants.ATTR_NAME_OF_DEU_STORAGE]+1}))

        uuidOfRobotFactoryPrice = self.scheduler.scheduleAction(ScheduleToken(Priority.NORMAL, self.interractor.price, self.logger, params={'ogameID': constants.ROBOT_FACTORY, 'nbr':facilityLevelsDict[constants.ATTR_NAME_OF_ROBOT_FACTORY]+1}))
        uuidOfShipyardPrice = self.scheduler.scheduleAction(ScheduleToken(Priority.NORMAL, self.interractor.price, self.logger, params={'ogameID': constants.SHIPYARD, 'nbr':facilityLevelsDict[constants.ATTR_NAME_OF_SHIPYARD]+1}))
        uuidOfResearchLabPrice = self.scheduler.scheduleAction(ScheduleToken(Priority.NORMAL, self.interractor.price, self.logger, params={'ogameID': constants.RESEARCH_LAB, 'nbr':facilityLevelsDict[constants.ATTR_NAME_OF_RESEARCH_LAB]+1}))
        uuidOfMissleSiloPrice = self.scheduler.scheduleAction(ScheduleToken(Priority.NORMAL, self.interractor.price, self.logger, params={'ogameID': constants.MISSILE_SILO, 'nbr':facilityLevelsDict[constants.ATTR_NAME_OF_MISSILE_SILO]+1}))
        uuidOfNaniteFactoryPrice = self.scheduler.scheduleAction(ScheduleToken(Priority.NORMAL, self.interractor.price, self.logger, params={'ogameID': constants.NANITE_FACTORY, 'nbr':facilityLevelsDict[constants.ATTR_NAME_OF_NANITE_FACTORY]+1}))
        uuidOfTerraformerPrice = self.scheduler.scheduleAction(ScheduleToken(Priority.NORMAL, self.interractor.price, self.logger, params={'ogameID': constants.TERRAFORMER, 'nbr':facilityLevelsDict[constants.ATTR_NAME_OF_TERRAFORMER]+1}))

        uuidOfEnergyTechPrice = self.scheduler.scheduleAction(ScheduleToken(Priority.NORMAL, self.interractor.price, self.logger, params={'ogameID': constants.ENERGY_TECH, 'nbr':researchLevelsDict[constants.ATTR_NAME_OF_ENERGY_TECH]+1}))
        uuidOfLaserTechPrice = self.scheduler.scheduleAction(ScheduleToken(Priority.NORMAL, self.interractor.price, self.logger, params={'ogameID': constants.LASER_TECH, 'nbr':researchLevelsDict[constants.ATTR_NAME_OF_LASER_TECH]+1}))
        uuidOfIonTechPrice = self.scheduler.scheduleAction(ScheduleToken(Priority.NORMAL, self.interractor.price, self.logger, params={'ogameID': constants.ION_Tech, 'nbr':researchLevelsDict[constants.ATTR_NAME_OF_ION_Tech]+1}))
        uuidOfHyperSpaceTechPrice = self.scheduler.scheduleAction(ScheduleToken(Priority.NORMAL, self.interractor.price, self.logger, params={'ogameID': constants.HYPER_SPACE_TECH, 'nbr':researchLevelsDict[constants.ATTR_NAME_OF_HYPER_SPACE_TECH]+1}))
        uuidOfPlasmaTechPrice = self.scheduler.scheduleAction(ScheduleToken(Priority.NORMAL, self.interractor.price, self.logger, params={'ogameID': constants.PLASMA_TECH, 'nbr':researchLevelsDict[constants.ATTR_NAME_OF_PLASMA_TECH]+1}))
        uuidOfCombustionDrivePrice = self.scheduler.scheduleAction(ScheduleToken(Priority.NORMAL, self.interractor.price, self.logger, params={'ogameID': constants.COMBUSTION_DRIVE, 'nbr':researchLevelsDict[constants.ATTR_NAME_OF_COMBUSTION_DRIVE]+1}))
        uuidOfImpulseDrivePrice = self.scheduler.scheduleAction(ScheduleToken(Priority.NORMAL, self.interractor.price, self.logger, params={'ogameID': constants.IMPULSE_DRIVE, 'nbr':researchLevelsDict[constants.ATTR_NAME_OF_IMPULSE_DRIVE]+1}))
        uuidOfHyperspaceDrivePrice = self.scheduler.scheduleAction(ScheduleToken(Priority.NORMAL, self.interractor.price, self.logger, params={'ogameID': constants.HYPERSPACE_DRIVE, 'nbr':researchLevelsDict[constants.ATTR_NAME_OF_HYPERSPACE_DRIVE]+1}))
        uuidOfSpyTechPrice = self.scheduler.scheduleAction(ScheduleToken(Priority.NORMAL, self.interractor.price, self.logger, params={'ogameID': constants.SPY_TECH, 'nbr':researchLevelsDict[constants.ATTR_NAME_OF_SPY_TECH]+1}))
        uuidOfComputerTechPrice = self.scheduler.scheduleAction(ScheduleToken(Priority.NORMAL, self.interractor.price, self.logger, params={'ogameID': constants.COMPUTER_TECH, 'nbr':researchLevelsDict[constants.ATTR_NAME_OF_COMPUTER_TECH]+1}))
        uuidOfAstrophysicsPrice = self.scheduler.scheduleAction(ScheduleToken(Priority.NORMAL, self.interractor.price, self.logger, params={'ogameID': constants.ASTROPHYSICS, 'nbr':researchLevelsDict[constants.ATTR_NAME_OF_ASTROPHYSICS]+1}))
        uuidOfIntGalResearchPrice = self.scheduler.scheduleAction(ScheduleToken(Priority.NORMAL, self.interractor.price, self.logger, params={'ogameID': constants.INT_GAL_RESEARCH, 'nbr':researchLevelsDict[constants.ATTR_NAME_OF_INT_GAL_RESEARCH]+1}))
        uuidOfGravitonTechPrice = self.scheduler.scheduleAction(ScheduleToken(Priority.NORMAL, self.interractor.price, self.logger, params={'ogameID': constants.GRAVITON_TECH, 'nbr':researchLevelsDict[constants.ATTR_NAME_OF_GRAVITON_TECH]+1}))
        uuidOfWeaponTechPrice = self.scheduler.scheduleAction(ScheduleToken(Priority.NORMAL, self.interractor.price, self.logger, params={'ogameID': constants.WEAPON_TECH, 'nbr':researchLevelsDict[constants.ATTR_NAME_OF_WEAPON_TECH]+1}))
        uuidOfShieldTechPrice = self.scheduler.scheduleAction(ScheduleToken(Priority.NORMAL, self.interractor.price, self.logger, params={'ogameID': constants.SHIELD_TECH, 'nbr':researchLevelsDict[constants.ATTR_NAME_OF_SHIELD_TECH]+1}))
        uuidOfArmourPrice = self.scheduler.scheduleAction(ScheduleToken(Priority.NORMAL, self.interractor.price, self.logger, params={'ogameID': constants.ARMOUR_TECH, 'nbr':researchLevelsDict[constants.ATTR_NAME_OF_ARMOUR_TECH]+1}))

        actionUuidList.append(uuidOfMetalMinePrice)
        actionUuidList.append(uuidOfCrystalMinePrice)
        actionUuidList.append(uuidOfDeuMinePrice)
        actionUuidList.append(uuidOfSolarPlantPrice)
        actionUuidList.append(uuidOfFusionReactorPrice)
        actionUuidList.append(uuidOfMetalStoragePrice)
        actionUuidList.append(uuidOfCrystalStoragePrice)
        actionUuidList.append(uuidOfDeuStoragePrice)

        actionUuidList.append(uuidOfRobotFactoryPrice)
        actionUuidList.append(uuidOfShipyardPrice)
        actionUuidList.append(uuidOfResearchLabPrice)
        actionUuidList.append(uuidOfMissleSiloPrice)
        actionUuidList.append(uuidOfNaniteFactoryPrice)
        actionUuidList.append(uuidOfTerraformerPrice)

        actionUuidList.append(uuidOfEnergyTechPrice)
        actionUuidList.append(uuidOfLaserTechPrice)
        actionUuidList.append(uuidOfIonTechPrice)
        actionUuidList.append(uuidOfHyperSpaceTechPrice)
        actionUuidList.append(uuidOfPlasmaTechPrice)
        actionUuidList.append(uuidOfCombustionDrivePrice)
        actionUuidList.append(uuidOfImpulseDrivePrice)
        actionUuidList.append(uuidOfHyperspaceDrivePrice)
        actionUuidList.append(uuidOfSpyTechPrice)
        actionUuidList.append(uuidOfComputerTechPrice)
        actionUuidList.append(uuidOfAstrophysicsPrice)
        actionUuidList.append(uuidOfIntGalResearchPrice)
        actionUuidList.append(uuidOfGravitonTechPrice)
        actionUuidList.append(uuidOfWeaponTechPrice)
        actionUuidList.append(uuidOfShieldTechPrice)
        actionUuidList.append(uuidOfArmourPrice)

        self.waitTillActionsCompleted(actionUuidList)

        priceOFBuildingsDict = {}
        result = self.scheduler.getResultOf(uuidOfMetalMinePrice)['Result']
        result['Energy'] = utilities.getEnergyConsumption(buildingLevelsDict[constants.ATTR_NAME_OF_METAL_MINE] + 1, constants.ATTR_NAME_OF_METAL_MINE)
        priceOFBuildingsDict[constants.ATTR_NAME_OF_METAL_MINE] = result
        result = self.scheduler.getResultOf(uuidOfCrystalMinePrice)['Result']
        result['Energy'] = utilities.getEnergyConsumption(buildingLevelsDict[constants.ATTR_NAME_OF_CRYSTAL_MINE] + 1, constants.ATTR_NAME_OF_CRYSTAL_MINE)
        priceOFBuildingsDict[constants.ATTR_NAME_OF_CRYSTAL_MINE] = result
        result = self.scheduler.getResultOf(uuidOfDeuMinePrice)['Result']
        result['Energy'] = utilities.getEnergyConsumption(buildingLevelsDict[constants.ATTR_NAME_OF_DEU_MINE] + 1, constants.ATTR_NAME_OF_DEU_MINE)
        priceOFBuildingsDict[constants.ATTR_NAME_OF_DEU_MINE] = result
        priceOFBuildingsDict[constants.ATTR_NAME_OF_SOLAR_PLANT] = self.scheduler.getResultOf(uuidOfSolarPlantPrice)['Result']
        priceOFBuildingsDict[constants.ATTR_NAME_OF_FUSION_REACTOR] = self.scheduler.getResultOf(uuidOfFusionReactorPrice)['Result']
        priceOFBuildingsDict[constants.ATTR_NAME_OF_METAL_STORAGE] = self.scheduler.getResultOf(uuidOfMetalStoragePrice)['Result']
        priceOFBuildingsDict[constants.ATTR_NAME_OF_CRYSTAL_STORAGE] = self.scheduler.getResultOf(uuidOfCrystalStoragePrice)['Result']
        priceOFBuildingsDict[constants.ATTR_NAME_OF_DEU_STORAGE] = self.scheduler.getResultOf(uuidOfDeuStoragePrice)['Result']

        priceOFFacilitiesDict = {}
        priceOFFacilitiesDict[constants.ATTR_NAME_OF_ROBOT_FACTORY] = self.scheduler.getResultOf(uuidOfRobotFactoryPrice)['Result']
        priceOFFacilitiesDict[constants.ATTR_NAME_OF_SHIPYARD] = self.scheduler.getResultOf(uuidOfShipyardPrice)['Result']
        priceOFFacilitiesDict[constants.ATTR_NAME_OF_RESEARCH_LAB] = self.scheduler.getResultOf(uuidOfResearchLabPrice)['Result']
        priceOFFacilitiesDict[constants.ATTR_NAME_OF_MISSILE_SILO] = self.scheduler.getResultOf(uuidOfMissleSiloPrice)['Result']
        priceOFFacilitiesDict[constants.ATTR_NAME_OF_NANITE_FACTORY] = self.scheduler.getResultOf(uuidOfNaniteFactoryPrice)['Result']
        priceOFFacilitiesDict[constants.ATTR_NAME_OF_TERRAFORMER] = self.scheduler.getResultOf(uuidOfTerraformerPrice)['Result']

        priceOFResearchesDict = {}
        priceOFResearchesDict[constants.ATTR_NAME_OF_ENERGY_TECH] = self.scheduler.getResultOf(uuidOfEnergyTechPrice)['Result']
        priceOFResearchesDict[constants.ATTR_NAME_OF_LASER_TECH] = self.scheduler.getResultOf(uuidOfLaserTechPrice)['Result']
        priceOFResearchesDict[constants.ATTR_NAME_OF_ION_Tech] = self.scheduler.getResultOf(uuidOfIonTechPrice)['Result']
        priceOFResearchesDict[constants.ATTR_NAME_OF_HYPER_SPACE_TECH] = self.scheduler.getResultOf(uuidOfHyperSpaceTechPrice)['Result']
        priceOFResearchesDict[constants.ATTR_NAME_OF_PLASMA_TECH] = self.scheduler.getResultOf(uuidOfPlasmaTechPrice)['Result']
        priceOFResearchesDict[constants.ATTR_NAME_OF_COMBUSTION_DRIVE] = self.scheduler.getResultOf(uuidOfCombustionDrivePrice)['Result']
        priceOFResearchesDict[constants.ATTR_NAME_OF_IMPULSE_DRIVE] = self.scheduler.getResultOf(uuidOfImpulseDrivePrice)['Result']
        priceOFResearchesDict[constants.ATTR_NAME_OF_HYPERSPACE_DRIVE] = self.scheduler.getResultOf(uuidOfHyperspaceDrivePrice)['Result']
        priceOFResearchesDict[constants.ATTR_NAME_OF_SPY_TECH] = self.scheduler.getResultOf(uuidOfSpyTechPrice)['Result']
        priceOFResearchesDict[constants.ATTR_NAME_OF_COMPUTER_TECH] = self.scheduler.getResultOf(uuidOfComputerTechPrice)['Result']
        priceOFResearchesDict[constants.ATTR_NAME_OF_ASTROPHYSICS] = self.scheduler.getResultOf(uuidOfAstrophysicsPrice)['Result']
        priceOFResearchesDict[constants.ATTR_NAME_OF_INT_GAL_RESEARCH] = self.scheduler.getResultOf(uuidOfIntGalResearchPrice)['Result']
        priceOFResearchesDict[constants.ATTR_NAME_OF_GRAVITON_TECH] = self.scheduler.getResultOf(uuidOfGravitonTechPrice)['Result']
        priceOFResearchesDict[constants.ATTR_NAME_OF_WEAPON_TECH] = self.scheduler.getResultOf(uuidOfWeaponTechPrice)['Result']
        priceOFResearchesDict[constants.ATTR_NAME_OF_SHIELD_TECH] = self.scheduler.getResultOf(uuidOfShieldTechPrice)['Result']
        priceOFResearchesDict[constants.ATTR_NAME_OF_ARMOUR_TECH] = self.scheduler.getResultOf(uuidOfArmourPrice)['Result']

        resourcesWithHeader =  {'resources': resourcesDict}
        BuildingLevelsWithHeader =  {'buildingLevels': buildingLevelsDict}
        facilityLevelsWithHeader =  {'facilityLevels': facilityLevelsDict}
        researchLevelsWithHeader = {'researchLevels': researchLevelsDict}
        ongoingConstAndResearchWithHeader = {'ongoingConstructionsAndResearch': ongoingConstAndResearchDict}

        #TODO FAKE DATA GET REAL
        fleetValueWIthHeader = {'fleetValue': 0}
        buildingPricesWithHeader = {'buildingPrices': priceOFBuildingsDict}
        facilityPricesWithHeader = {'facilityPrices': priceOFFacilitiesDict}
        researchPricesWithHeader = {'researchPrices': priceOFResearchesDict}

        return {**resourcesWithHeader, **fleetValueWIthHeader, **BuildingLevelsWithHeader, **facilityLevelsWithHeader, **researchLevelsWithHeader, **buildingPricesWithHeader, **facilityPricesWithHeader, **researchPricesWithHeader, **ongoingConstAndResearchWithHeader}

