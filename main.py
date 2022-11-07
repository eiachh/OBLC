from distutils.command.config import config
import os
from threading import Thread
from time import sleep
from common_lib.logger import OBLC_Logger
import requests
from flask import Flask
import json
from Configuration import Configuration
from buildingPipeline import BuildingPipeline

import wrapper.interractorWrapper as InterractorWrapper
from wrapper.schedulableInterractor import SchedulableInterractor

class OBLC:

    def __init__(self):
        self.logger = OBLC_Logger('Init', 'OBLC')
        self.config = self.setup()

        self.interractor = InterractorWrapper.Interractor(self.config.INTERRACTOR_IP, self.config.INTERRACTOR_PORT)
        self.buildingPipeline = BuildingPipeline(self.interractor, self.logger, self.config)

        self.waitForRequiredServices()
        self.resumeBuildPipeline()

        self.runBody()

    def setVariableFromEnvVar(self, defaultValue, envVarName):
        envValue = os.environ.get(envVarName)
        if envValue is not None:
            self.logger.logMainInfo(f'{envVarName} is {envValue}')
            return envValue
        else:
            self.logger.logWarn(f'{envVarName} not found returning default: {defaultValue}')
            return defaultValue

    def setup(self):
        config = Configuration()
        config.INTERRACTOR_IP = self.setVariableFromEnvVar(config.INTERRACTOR_IP, 'INTERRACTOR_IP')
        config.INTERRACTOR_PORT = self.setVariableFromEnvVar(config.INTERRACTOR_PORT, 'INTERRACTOR_PORT')
        config.RESOURCE_LIMITER_ADDR = self.setVariableFromEnvVar(config.RESOURCE_LIMITER_ADDR, 'RESOURCE_LIMITER_ADDR')
        config.BUILDING_MANAGER_ADDR = self.setVariableFromEnvVar(config.BUILDING_MANAGER_ADDR, 'BUILDING_MANAGER_ADDR')
        config.PROGRESSION_MANAGER_ADDR = self.setVariableFromEnvVar(config.PROGRESSION_MANAGER_ADDR, 'PROGRESSION_MANAGER_ADDR')
        config.RESEARCH_MANAGER_ADDR = self.setVariableFromEnvVar(config.RESEARCH_MANAGER_ADDR, 'RESEARCH_MANAGER_ADDR')
        config.INVESTMENT_MANAGER_ADDR = self.setVariableFromEnvVar(config.INVESTMENT_MANAGER_ADDR, 'INVESTMENT_MANAGER_ADDR')
        config.LOG_LEVEL = self.setVariableFromEnvVar(config.LOG_LEVEL, 'OGAME_LOG_LEVEL')
        config.BUILD_PIPELINE_REACTIVATION = int(self.setVariableFromEnvVar(config.BUILD_PIPELINE_REACTIVATION, 'BUILD_PIPELINE_REACTIVATION'))
        config.SERVICE_AVAILIBILITY_RETRY = int(self.setVariableFromEnvVar(config.SERVICE_AVAILIBILITY_RETRY, 'SERVICE_AVAILIBILITY_RETRY'))

        self.logger.setLogLevel(config.LOG_LEVEL)

        return config

    def resumeBuildPipeline(self):
        thread = Thread(target=self.buildingPipeline.resume)
        thread.start()

        self.isAttackPipelineResumed = False

    def pauseBuildPipeline(self):
        self.buildingPipeline.pause()
        #self.isAttackPipelineResumed = True

    def waitForRequiredServices(self):
        
        if(not self.interractor.checkIfRequiredServiceIsAvailable(self.logger)):
            self.waitAndRetryServiceAvailibility()
        self.logger.logMainInfo('Ogame-interractor services OK')

        if(not self.buildingPipeline.checkIfRequiredServiceIsAvailable()):
            self.waitAndRetryServiceAvailibility()
        self.logger.logMainInfo('BuildPipeline services OK')

    def waitAndRetryServiceAvailibility(self):
        sleep(self.config.SERVICE_AVAILIBILITY_RETRY)
        self.waitForRequiredServices()

    def runBody(self):
        counter = 0
        #while(True):
            #print("MAIN started2")
            #counter = counter + 1
            #if(counter == 3):
            #    self.pauseBuildPipeline()
            #    print("paused for some time")
            #    sleep(10)
            #    #self.resumeBuildPipeline()
            #sleep(4)

    def justTestTmp(self):
        print("test func ran")

oblc = OBLC()






