
from turtle import pos
import requests
import json

class Interractor:
    def __init__(self, ip, port):
        self.ip = ip
        self.port = port
        self.apiUrl = f"{self.ip}:{self.port}"
    
    def __str__(self):
         return f"Basic interractor wrapper ,wrapped interractor addr: {self.ip}:{self.port}"

    def checkIfRequiredServiceIsAvailable(self, logger):
        try:
            self.isUnderAttack()
            return True
        except Exception as e:
            logger.logWarn(f'Ogame-interractor service: {self.apiUrl} is not running')
            return False

    def isSchedulable(self):
        return False

    def isUnderAttack(self, dataDict=None):
        resp = requests.get(self.apiUrl + '/bot/is-under-attack')
        respJson = json.loads(resp.text)
        return respJson['Result']

    def serverTime(self, dataDict=None):
        resp = requests.get(self.apiUrl + '/bot/server/time')
        respJson = json.loads(resp.text)
        return respJson['Result']

    def userInfos(self, dataDict=None):
        resp = requests.get(self.apiUrl + '/bot/user-infos')
        respJson = json.loads(resp.text)
        return respJson['Result']

    def fleets(self, dataDict=None):
        resp = requests.get(self.apiUrl + '/bot/fleets')
        respJson = json.loads(resp.text)
        return respJson['Result']

    def ourAttacks(self, dataDict=None):
        resp = requests.get(self.apiUrl + '/bot/attacks')
        respJson = json.loads(resp.text)
        return respJson['Result']

    def galaxyInfo(self, galaxy, system):
        resp = requests.get(self.apiUrl + f"/bot/galaxy-infos/{galaxy}/{system}")
        respJson = json.loads(resp.text)
        return respJson['Result']

    def research(self, dataDict=None):
        resp = requests.get(self.apiUrl + '/bot/get-research')
        respJson = json.loads(resp.text)
        return respJson['Result']

#hours := (metalCost + crystalCost) / (2500 * (1 + roboticLvl) * float64(universeSpeed) * math.Pow(2, naniteLvl))
    def price(self, ogameID, nbr):
        resp = requests.get(self.apiUrl + f"/bot/price/{ogameID}/{nbr}")
        respJson = json.loads(resp.text)
        return respJson['Result']

    def planets(self, dataDict=None):
        resp = requests.get(self.apiUrl + '/bot/planets')
        respJson = json.loads(resp.text)
        return respJson['Result']

    def planetAtCoord(self, galaxy, system, position):
        resp = requests.get(self.apiUrl + f"/bot/planets/{galaxy}/{system}/{position}")
        respJson = json.loads(resp.text)
        return respJson['Result']

    def planetById(self, planetID):
        resp = requests.get(self.apiUrl + f"/bot/planets/{planetID}")
        respJson = json.loads(resp.text)
        return respJson['Result']

    #The operation %, eg all at 100% unless changed
    def resourceSettings(self, planetID):
        resp = requests.get(self.apiUrl + f"/bot/planets/{planetID}/resource-settings")
        respJson = json.loads(resp.text)
        return respJson['Result']

    def resourceBuildings(self, planetID):
        resp = requests.get(self.apiUrl + f"/bot/planets/{planetID}/resources-buildings")
        respJson = json.loads(resp.text)
        return respJson['Result']

    def ships(self, planetID):
        resp = requests.get(self.apiUrl + f"/bot/planets/{planetID}/ships")
        respJson = json.loads(resp.text)
        return respJson['Result']

    def facilities(self, planetID):
        resp = requests.get(self.apiUrl + f"/bot/planets/{planetID}/facilities")
        respJson = json.loads(resp.text)
        return respJson['Result']

    def POSTbuild(self, planetID, objectToBuildOgameID, nbr):
        resp = requests.post(self.apiUrl + f"/bot/planets/{planetID}/build/{objectToBuildOgameID}/{nbr}")
        respJson = json.loads(resp.text)
        return respJson['Result']

    def POSTcancelBuild(self, planetID, objectToBuildOgameID):
        resp = requests.post(self.apiUrl + f"/bot/planets/{planetID}/build/cancelable/{objectToBuildOgameID}")
        respJson = json.loads(resp.text)
        return respJson['Result']

    def production(self, planetID):
        resp = requests.get(self.apiUrl + f"/bot/planets/{planetID}/production")
        respJson = json.loads(resp.text)
        return respJson['Result']

    def constructionAndResearch(self, planetID):
        resp = requests.get(self.apiUrl + f"/bot/planets/{planetID}/constructions")
        respJson = json.loads(resp.text)
        return respJson['Result']

    def resources(self, planetID):
        resp = requests.get(self.apiUrl + f"/bot/planets/{planetID}/resources")
        respJson = json.loads(resp.text)
        return respJson['Result']

    #-d 'ships=204,1&ships=205,2&speed=10&galaxy=4&system=208&position=8&mission=3&metal=1&crystal=2&deuterium=3'
    def POSTSendFleet(self, planetID, fleetData):
        resp = requests.post(self.apiUrl + f"/bot/planets/{planetID}/send-fleet", data = fleetData)
        respJson = json.loads(resp.text)
        return respJson['Result']


    # TEST NEEDED
    def POSTcancelFleet(self, fleetID):
        resp = requests.post(self.apiUrl + f"/bot/fleets/{fleetID}/cancel")
        respJson = json.loads(resp.text)
        return respJson['Result']

    def POSTGetPageContent(self, pageUrl):
        resp = requests.post(self.apiUrl + f"/bot/page-content", data = pageUrl)
        respJson = json.loads(resp.text)
        return respJson['Result']

    def test1(self, planetID):
        resp = requests.post(self.apiUrl + f"/bot/planets/{planetID}/lifeform-buildings",)
        respJson = json.loads(resp.text)
        return respJson['Result']

    def espionageReport(self, dataDict=None):
        resp = requests.get(self.apiUrl + f"/bot/espionage-report")
        respJson = json.loads(resp.text)
        return respJson['Result']

#/bot/espionage-report

    ##/bot/delete-report/:messageID
    ##POST /bot/delete-all-espionage-reports
    ##POST /bot/delete-all-reports/:tabIndex
    #POST /bot/planets/:planetID/resource-settings
    #POST /bot/planets/:planetID/send-ipm
    ##POST /bot/planets/:planetID/teardown/:ogameID
    ##GET  /bot/moons/:moonID/phalanx/:galaxy/:system/:position
    ##GET  /bot/get-auction
    ##POST /bot/do-auction

    #lol
    #/bot/planets/:planetID/defence