class constants:
    #FOR BUILDING MANAGER    
    METAL_MINE = 1
    CRYSTAL_MINE = 2
    DEU_MINE = 3
    SOLAR_PLANT = 4
    FUSION_REACTOR = 12
    SOLAR_SATELLITE = 212
    METAL_STORAGE = 22
    CRYSTAL_STORAGE = 23
    DEU_STORAGE = 24


    ATTR_NAME_OF_METAL_MINE = 'MetalMine'
    ATTR_NAME_OF_CRYSTAL_MINE = 'CrystalMine'
    ATTR_NAME_OF_DEU_MINE = 'DeuteriumSynthesizer'
    ATTR_NAME_OF_SOLAR_PLANT = 'SolarPlant'
    ATTR_NAME_OF_FUSION_REACTOR = 'FusionReactor'
    ATTR_NAME_OF_SOLAR_SATELLITE = 'SolarSatellite'
    ATTR_NAME_OF_METAL_STORAGE = 'MetalStorage'
    ATTR_NAME_OF_CRYSTAL_STORAGE = 'CrystalStorage'
    ATTR_NAME_OF_DEU_STORAGE = 'DeuteriumTank'

    def convertOgameIDToAttrName(ogameID):
        if(ogameID == 1):
            return constants.ATTR_NAME_OF_METAL_MINE
        if(ogameID == 2):
            return constants.ATTR_NAME_OF_CRYSTAL_MINE
        if(ogameID == 3):
            return constants.ATTR_NAME_OF_DEU_MINE
        if(ogameID == 4):
            return constants.ATTR_NAME_OF_SOLAR_PLANT
        if(ogameID == 12):
            return constants.ATTR_NAME_OF_FUSION_REACTOR
        if(ogameID == 212):
            return constants.ATTR_NAME_OF_SOLAR_SATELLITE
        if(ogameID == 22):
            return constants.ATTR_NAME_OF_METAL_STORAGE
        if(ogameID == 23):
            return constants.ATTR_NAME_OF_CRYSTAL_STORAGE
        if(ogameID == 24):
            return constants.ATTR_NAME_OF_DEU_STORAGE

    def getResourceSumInUnitPrice(priceJson):
        sum = 0
        sum += 1 * priceJson['Metal']
        sum += 2 * priceJson['Crystal']
        sum += 3 * priceJson['Deuterium']
        return sum