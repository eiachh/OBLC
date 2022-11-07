from wrapper.interractorWrapper import Interractor
import requests
import json

class SchedulableInterractor(Interractor):
    def __init__(self, ip, port):
        super().__init__(ip,port)
    
    def __str__(self):
        return f"Server addr: {self.ip}:{self.port}"

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

    def POSTbuild(self, dataDict):
        return super().POSTbuild(dataDict['planetID'], dataDict['objectToBuildOgameID'], dataDict['nbr'])

    def POSTcancelBuild(self, dataDict):
        return super().POSTcancelBuild(dataDict['planetID'], dataDict['objectToBuildOgameID'])

    def production(self, dataDict):
        return super().production(dataDict['planetID'])

    def constructionAndResearch(self, dataDict):
        return super().constructionAndResearch(dataDict['planetID'])

    def resources(self, dataDict):
        return super().resources(dataDict['planetID'])

    #-d 'ships=204,1&ships=205,2&speed=10&galaxy=4&system=208&position=8&mission=3&metal=1&crystal=2&deuterium=3'
    def POSTSendFleet(self, dataDict):
        return super().POSTSendFleet(dataDict['planetID'], dataDict['fleetData'])