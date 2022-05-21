# -*- coding: utf-8 -*-
from .Item import Item

class FarnellItem(Item):

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
    def __init__(self, partData, wishedPartName, wishedQuantity, computeData = False, apiName = "Farnell", realItem = True):

        Item.__init__(self, wishedPartName, wishedQuantity, apiName, realItem)

        self.__data = partData

        #Init value
        self.initData()

        #Mean lead time
        self.meanLeadTime = "2 semaines"

        #Dict
        self.__priceBreaks = self.getFromDict("prices", self.__data,{u'to': u'9', u'from': u'1', u'cost': 0.0})
        self.warning = self.getFromDict('RestrictionMessage', self.__data, "Any message")


        #computing of data product (price, delays...)
        if(computeData and realItem==True):
            self.__computeUnitPrice()

        self.__computeAvailableQantities()

    """!
        @brief Find data from API
        @return void
    """
    def initData(self):


        #print(self.__data)

        if('datasheets' in self.__data):
            if(len(self.__data['datasheets'])>0):
                self.datasheet = self.__data['datasheets'][0]["url"]
        #self.datasheet = self.getFromDict('datasheets', self.__data, self.datasheet)
        self.category = self.getFromDict('category', self.__data,self.category)  #Any cat
        self.lifeCyle = self.getFromDict('productStatus', self.__data, self.lifeCycle)
        self.description = self.getFromDict('displayName', self.__data,self.description) #OK
        self.manufacturer = self.getFromDict('vendorName', self.__data,self.manufacturer) #OK
        self.infos = self.getFromDict('ProductDetailUrl', self.__data,self.infos)
        self.fabricantPartNumber = self.getFromDict('translatedManufacturerPartNumber', self.__data,self.fabricantPartNumber)
        self.unitWeight = self.getFromDict('UnitWeightKg', self.__data,self.unitWeight)
        self.avaibility = self.getFromDict('inv', self.__data,self.avaibility)
        self.minimalOrderQuantity = self.getFromDict('translatedMinimumOrderQuality', self.__data,self.minimalOrderQuantity)#OK
        self.groupeOrder = self.getFromDict('groupOrder', self.__data,self.groupeOrder)  #Not sure
        self.leadTime = self.getFromDoubleDict("stock", "leastLeadTime", self.__data, self.leadTime)

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
        if(self.lifeCyle=="NO_LONGER_MANUFACTURED"):
            return True
        else:
            return False

    """!
        @brief Compute unit price of item
        @return void
    """
    def __computeUnitPrice(self):
        """Compute unit price of Item"""
        priceInfo = []
        for item in self.__priceBreaks:
            priceInfo.append([item['to'], item['from'], item['cost']])  #Avoir '0.93 \u20ac' for price
        #print(priceInfo)
        #Set higher price for beginning
        if(len(priceInfo)==0):
            self.unitPrice = 0
            return 
        else:
            self.unitPrice = priceInfo[0][2]
        nbPass=0  #Count of pass to set the range

        for p in priceInfo:
            if(p[0]<=self.wishedQuantity):
                nbPass +=1
        if(nbPass==0):
            self.unitPrice = priceInfo[-1][2]
        else:
            self.unitPrice = priceInfo[nbPass][2]

    """!
        @brief Compute available quantities
        @return void
    """
    def __computeAvailableQantities(self):


        if(self.lifeCyle in ["DIRECT_SHIP", "STOCKED"]):
            
            self.availableOrderQuantity = self.avaibility
            if(self.availableOrderQuantity>0):
                self.isAvailableForOrder = True
                #print("Quantity of "+str(self.fabricantPartNumber)+" = "+str(self.availableOrderQuantity))
        else:
            self.availableOrderQuantity = 0
        
        if(self.availableOrderQuantity>=self.wishedQuantity):
                self.directOrder = True
        
