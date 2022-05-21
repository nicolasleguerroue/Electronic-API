# -*- coding: utf-8 -*-
from .Item import Item

class FutureItem(Item):

    """!
    @brief Constructor
    @param Dict of data from reading API
    @param Wished part name
    @param Wished quantity to order
    @param Demand of compute data if true is given
    @param API name
    @param State of Item : True if Item exists (at least 1 component has been found) [default value = True]
    @return
    """
    def __init__(self, partData, wishedPartName, wishedQuantity, computeData = False, apiName="Future", realItem=True):
        """ New item, if computeData is False, don't compute the price beacuse may raise some errors"""

        Item.__init__(self, wishedPartName, wishedQuantity, apiName, realItem)

        self.__data = partData
        self.initData()
        
        #Composed data
        self.__availableItems = ["enstock"]                 #parse available data and check if possible to make order now
        self.__priceBreaks = self.getFromDict("pricing", self.__data,[{u'unit_price': u'0.0', u'quantity_from': 0, u'quantity_to': 0}])

        #computing of data product (price, delays...)
        if(computeData and realItem==True):
            self.__computeUnitPrice()

        self.__computeAvailableQantities()

    """!
    @brief Get a data from Future dict
    @param root of dict
    @param Attribut to search
    @param input dict
    @param Default data when any value found
    @return
    """
    def getFutureDict(self, root, attribut, data, defaultData):

        if(root in data):
            tmpData = data[root]
            if(tmpData!=None and len(tmpData)==1):
                if(attribut in tmpData[0]):
                    index = list(tmpData[0].keys()).index(attribut)
                    return (tmpData[0][attribut])

            if(tmpData!=None and len(tmpData)>1):

                for item in tmpData:
                    if(attribut in item.values()):
                        return item["value"]

        return defaultData

    """!
        @brief Find data from API
        @return void
    """
    def initData(self):
        """Init data with utf-8 format"""


        self.category = self.getFromDoubleDict("categories", "type_name", self.__data,self.category)
        #print(self.__data)

        self.datasheet = self.getFutureDict("documents", "url", self.__data, self.datasheet)
        self.lifeCycle = self.getFutureDict("part_attributes", "productLifeCycle", self.__data, self.lifeCycle)

        self.manufacturer = self.getFutureDict("part_attributes", "manufacturerName", self.__data, self.manufacturer)
        self.description = self.getFutureDict("part_attributes", "description (en)", self.__data, self.description)
        self.category = self.getFutureDict("categories", "id", self.__data, self.description)

        self.fabricantPartNumber = self.getFromDoubleDict("part_id", "mpn", self.__data,self.fabricantPartNumber)  #mpn = manufacturer part number
        self.unitWeight = self.getFromDoubleDict("part_id", "unit_weight", self.__data,self.unitWeight)

        self.avaibility = self.getFromDoubleDict("quantities", "quantity_available", self.__data,self.avaibility)

        self.minimalOrderQuantity = self.getFromDoubleDict("quantities", "quantity_minimum", self.__data,self.minimalOrderQuantity)
        self.groupeOrder = self.getFromDoubleDict("quantities", "order_mult_qty", self.__data,self.groupeOrder)
        self.availableQuantities = "0"


    """!
        @brief Update unit price and available quantities
        @return void
    """
    def update(self):
        """Update some info on item"""
        self.__computeUnitPrice()
        self.__computeAvailableQantities()

    """!
        @brief return obsolte status
        @return Obsolete status of item
    """
    @property
    def isObsolete(self):
        """Check if item is obsolete """
        self.tmp = self.lifeCycle 
        if(self.tmp=="ACTIVE"):
            return False
        if(self.tmp=="Inconnue"):
            return False
        
    """!
        @brief Compute unit price of item
        @return void
    """
    def __computeUnitPrice(self):
        """Compute unit price of Item"""
        priceInfo = []
        for item in self.__priceBreaks:
            priceInfo.append([item['unit_price'], item['quantity_from'], item['quantity_to']])  

        #Set higher price for beginning
        if(len(priceInfo)==1):
            self.unitPrice = 0.0
            return 
        else:
            self.unitPrice = priceInfo[0][0]
        nbPass=0  #Count of pass to set the range

        for p in priceInfo:
            if(p[0]<=self.wishedQuantity):
                nbPass +=1
        if(nbPass==0):
            self.unitPrice = priceInfo[-1][0]
        else:
            self.unitPrice = priceInfo[nbPass-1][0]

    """!
        @brief Compute available quantities
        @return void
    """
    def __computeAvailableQantities(self):
          
        self.availableOrderQuantity = int(self.avaibility)

        if(self.availableOrderQuantity>0):
            self.isAvailableForOrder =True

        if(self.availableOrderQuantity>=self.wishedQuantity):
            self.directOrder = True


