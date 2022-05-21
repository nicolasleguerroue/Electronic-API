# -*- coding: utf-8 -*-

"""
!@brief This class represent a generic item
"""
class Item:
    """!
    @brief Constructor
    @param Searched part number (from fabricant)
    @param Wished quantity to order
    @param API name
    @param State of Item : True if Item exists (at least 1 component has been found) [default value = True]
    @return
    """
    def __init__(self, searchedPartNumber, wishedQuantity, apiName, realItem = True):
        
        #Generic data
        self.__searchedPartNumber = searchedPartNumber  #Name of part number that we want to find, may be different that part number found
        self.__unitPrice = 0.0                          #Unit price of item
        self.__isBestPrice = False                      #If Item in list and value to True, best price of the list
        self.__isBestSimilarPrice = False               #If Item in list and value to True, best price of the list - For similar items
        self.__availableOrderQuantity = 0               #Quantity that may be ordered immediatly (don't depend of the needed quantities)
        self.__isAvailableForOrder = False              #Per default, nothing is available
        self.__wishedQuantity = wishedQuantity          #Wished quantity
        self.__directOrder = False                      #If true, can order as available quantity are higher than wished quantity
        self.__apiName = apiName                        #Name of API
        self.__warning = ""                             #Information about item 

        #By user
        self.__meanShippingTime = "2 semaines"
        #Status
        self.__realItem = realItem                      #If true, real item exist, else mean that is not found in db
        self.__similarItem = False                      #If true, real item exist, else mean that is not found in db - For similar items
        self.__similarAvailableItem = False

        #Specific data (Compute)
        self.__datasheet =""                                    #Datasheet url
        self.__category ="Inconnue"                             #item category
        self.__lifeCycle = "Inconnue"                            #Life cycle of Item (obsolete, new product...)
        self.__description = "Inconnue"                         #description of product
        self.__manufacturer = "Inconnu"                         #Manufacturer
        self.__infos = "Aucune information"                     #Infos
        self.__fabricantPartNumber = "Aucune reference trouvee" #fabricant part Number 
        self.__avaibility = "0"                                 #Avaibility (raw data from API)
        self.__unitWeight = "Inconnu"                           #Unit unitWeight
        self.__minimalOrderQuantity = ""                        #MOQ
        self.__groupeOrder = "1"                                 #Group order
        self.__leadTime = ""                                    #Lead time


    """!
        @brief Encode a unicode str to utf-8 str
        @param String to encode
        @return Encoded string
    """
    def utf8(self, unicodeToStr):
        return unicodeToStr.encode("utf-8", "ignore")

    """!
        @brief This method is used to check the type of argument passed in function
        @param Variable to check
        @param Type to check
        @return Assert error
    """
    def checkType(self, arg, typeArg):

        assert isinstance(arg, typeArg), "Expected "+str(typeArg)+" but real type is "+str(type(arg))

    """!
        @brief Return a dictionnary value with given key
        @param Key
        @param Dict to read
        @param Default value if given key doesn't exist
        @return Dict value
    """
    def getFromDict(self, key, dictionnary, defaultValue=""):

        self.checkType(key, str)
        self.checkType(dictionnary, dict)

        if(key in dictionnary):
            return dictionnary[key]
        else:
            return defaultValue


    def getFromList(self, key, inputList, defaultValue=""):

        self.checkType(key, str)
        self.checkType(inputList, list)

        if(key in inputList):
            return inputList[key]
        else:
            return defaultValue

    """!
        @brief Return a dictionnary value with two given keys
        @param Key 1
        @param Key 2
        @param Dict to read
        @param Default value if given keys don't exist
        @return Dict value
    """
    def getFromDoubleDict(self, key1, key2, dictionnary, defaultValue):

        self.checkType(key1, str)
        self.checkType(key2, str)
        self.checkType(dictionnary, dict)

        if(key1 in dictionnary and key2 in dictionnary[key1]):
            return dictionnary[key1][key2]
        else:
            return defaultValue

    """!
        @brief Return the searched part number of item
        @return Searched part number
    """
    @property
    def searchedPartNumber(self):

        return self.__searchedPartNumber

    """!
        @brief Return the unit price of item
        @return Unit price of Item
    """
    @property
    def unitPrice(self):

        return self.__unitPrice

    """!
        @brief Set the unit price of item
        @param New unit price
        @return 
    """
    @unitPrice.setter
    def unitPrice(self, unitPrice):
        """set the unit price of Item"""
        self.checkType(unitPrice, float)

        self.__unitPrice = unitPrice


    """!
        @brief Return the mean shipping time
        @return Unit price of Item
    """
    @property
    def meanShippingTime(self):

        return self.__meanShippingTime

    """!
        @brief Set the mean shipping time
        @param New mean shipping time
        @return 
    """
    @meanShippingTime.setter
    def meanShippingTime(self, meanShippingTime):
        """set the unit price of Item"""
        self.checkType(meanShippingTime, float)

        self.__meanShippingTime = meanShippingTime

    """!
        @brief Return if item is best price among items list
        @return True if best price
    """
    @property
    def isBestPrice(self):

        return self.__isBestPrice

    """!
        @brief Set the best price status of item (True if best price)
        @return best price status
    """
    def setBestPrice(self, state):
        self.checkType(state, bool)

        self.__isBestPrice = state

    """!
        @brief Return if item is best price among items list
        @return True if best price
    """
    @property
    def isBestSimilarPrice(self):

        return self.__isBestSimilarPrice

    """!
        @brief Set the best price status of item (True if best price)
        @return best price status
    """
    def setBestSimilarPrice(self, state):
        self.checkType(state, bool)

        self.__isBestSimilarPrice = state

    """!
        @brief Return the available order quantity that may be ordered immediatly (don't depend of the needed quantities)
        @return The available order quantity
    """
    @property
    def availableOrderQuantity(self):

        return self.__availableOrderQuantity

    """!
        @brief Set the available order quantity
        @param The new available order quantity
        @return
    """
    @availableOrderQuantity.setter
    def availableOrderQuantity(self, quantity):

        self.checkType(quantity, int)

        self.__availableOrderQuantity = quantity

    """!
        @brief Return the available order status (If True, available quantity higher than 0)
        @return The available order status
    """
    @property
    def isAvailableForOrder(self):
        return self.__isAvailableForOrder

    """!
        @brief Set the available order status
        @param The new available order status
        @return
    """
    @isAvailableForOrder.setter
    def isAvailableForOrder(self, state):

        self.checkType(state, bool)
        self.__isAvailableForOrder = state

    """!
        @brief Return the wished quantity of given item
        @return The wished quantity
    """
    @property
    def wishedQuantity(self):
        return self.__wishedQuantity

    """!
        @brief Return the direct order status (If True, available quantity from provider is higher than wished quantity)
        @return The direct order status
    """
    @property
    def directOrder(self):

        return self.__directOrder

    """!
        @brief Set the direct order status (If True, available quantity from provider is higher than wished quantity)
        @param The direct order status
        @return 
    """
    @directOrder.setter
    def directOrder(self, state):
        self.checkType(state, bool)

        self.__directOrder = state

    """!
        @brief Return the API name
        @return The API name
    """
    @property
    def apiName(self):

        return self.__apiName

    """!
        @brief Return the provider message
        @return The provider message
    """
    @property
    def warning(self):
        return self.__warning

    """!
        @brief Set the provider message
        @param The provider message
    """
    @warning.setter
    def warning(self, warning):
        """Set the provider message"""
        self.checkType(warning, str)

        self.__warning = warning

    """!
        @brief This method is used to Item state (If True, is a real Item with quantity available)
        @return The similar Item state
    """
    @property
    def realItem(self):
        return self.__realItem

    @realItem.setter
    def realItem(self, state):
        self.__realItem = state

    """!
        @brief Return similar Item state (If True, is a similar Item)
        @return The similar Item state
    """
    @property
    def similarItem(self):
        return self.__similarItem

    """!
        @brief Set the similar item state
        @param The similar item state
    """
    @similarItem.setter
    def similarItem(self, state):
        self.__similarItem =state

    """!
        @brief This method is used to similar Item state (If True, is a similar Item)
        @return The similar Item state
    """
    @property
    def similarAvailableItem(self):
        return self.__similarAvailableItem

    """!
        @brief Set the similar available item state
        @param The similar available item state
    """
    @similarAvailableItem.setter
    def similarAvailableItem(self, state):
        self.__similarAvailableItem =state


    """!
        @brief Return the description of Item
        @return The description of Item
    """
    @property
    def description(self):
        """ Get item description"""
        return self.__description

    """!
        @brief Set the description of Item
        @param The description of Item
    """
    @description.setter
    def description(self, description):
        """ Get item description"""
        self.__description = description

    """!
        @brief Return the datasheet of the item
        @return The datasheet of the item
    """
    @property
    def datasheet(self):
        """ Get datasheet URL"""
        return self.__datasheet

    """!
        @brief Set the datasheet url
        @param The datasheet url
    """
    @datasheet.setter
    def datasheet(self, datasheet):
        """ Get datasheet URL"""
        self.__datasheet = datasheet

    """!
        @brief Return the datasheet of the item
        @return The datasheet of the item
    """
    @property
    def minimalOrderQuantity(self):
        return self.__minimalOrderQuantity

    """!
        @brief Set the minimal order quantity
        @param The minimal order quantity
    """
    @minimalOrderQuantity.setter
    def minimalOrderQuantity(self, minimalOrderQuantity):
        self.__minimalOrderQuantity = minimalOrderQuantity

    """!
        @brief Return the lead time of the item
        @return The lead time of the item
    """
    @property
    def leadTime(self):

        return self.__leadTime

    """!
        @brief Set the lead time
        @param The lead time
    """
    @leadTime.setter
    def leadTime(self, leadTime):

        self.__leadTime = leadTime

    """!
        @brief Return the group order quantity of the item
        @return The group order quantity of the item
    """
    @property
    def groupeOrder(self):
        """number in package """
        return self.__groupeOrder

    """!
        @brief Set the group order quantity
        @param The group order quantity
    """
    @groupeOrder.setter
    def groupeOrder(self, groupeOrder):
        """number in package """
        self.__groupeOrder = groupeOrder

    """!
        @brief Return the category of the item
        @return The category of the item
    """
    @property
    def category(self):
        """ Get item category"""
        return self.__category
    
    """!
        @brief Set the category
        @param The category
    """
    @category.setter
    def category(self, category):
        """ Get item category"""
        self.__category = category

    """!
        @brief Return the life cycle of the item
        @return The life cycle of the item
    """
    @property
    def lifeCycle(self):
        """ Get item lifeCycle"""
        return self.__lifeCycle

    @lifeCycle.setter
    def lifeCycle(self, lifeCycle):
        """ Get item lifeCycle"""
        self.__lifeCycle = lifeCycle

    """!
        @brief Return the manufacturer
        @return The manufacturer
    """
    @property
    def manufacturer(self):
        """ Get item manufacturer"""
        return self.__manufacturer

    """!
        @brief Set the manufacturer
        @param The manufacturer
    """
    @manufacturer.setter
    def manufacturer(self, manufacturer):
        """ Get item manufacturer"""
        self.__manufacturer = manufacturer

    """!
        @brief Return some infos on item
        @return Some infos on item
    """
    @property
    def infos(self):
        return self.__infos

    """!
        @brief Set the informations about item
        @param The informations about item
    """
    @infos.setter
    def infos(self, infos):
        """ Get item infos"""
        self.__infos = infos

    """!
        @brief Return fabricant part number
        @return Fabricant part number
    """
    @property
    def fabricantPartNumber(self):
        return self.__fabricantPartNumber

    """!
        @brief Set the fabricant part number found
        @param The fabricant part number found
    """
    @fabricantPartNumber.setter
    def fabricantPartNumber(self, fabricantPartNumber):
        """ Get item fabricantPartNumber"""
        self.__fabricantPartNumber = fabricantPartNumber

    """!
        @brief Return item avaibility
        @return Item avaibility
    """
    @property
    def avaibility(self):
        return self.__avaibility

    """!
        @brief Set the avaibility of item
        @param The avaibility of item
    """
    @avaibility.setter
    def avaibility(self, avaibility):
        """ Get item avaibility"""
        self.__avaibility = avaibility

    """!
        @brief Return unit weight
        @return Unit weight
    """
    @property
    def unitWeight(self):
        return str(self.__unitWeight)

    """!
        @brief Set the unit weight of Item
        @param The unit weight of Item
    """
    @unitWeight.setter
    def unitWeight(self, unitWeight):
        """ Get item unitWeight"""
        self.__unitWeight = unitWeight