# -*- coding: utf-8 -*-
from .Item import Item

class MouserItem(Item):

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
    def __init__(self, partData, wishedPartName, wishedQuantity, computeData = False, apiName="Mouser", realItem=True):
        """ New item, if computeData is False, don't compute the price beacuse may raise some errors"""

        Item.__init__(self, wishedPartName, wishedQuantity, apiName, realItem)

        self.__data = partData
        self.initData()
        
        #Composed data
        self.__availableItems = ["enstock"]                 #parse available data and check if possible to make order now
        self.__priceBreaks = self.getFromDict("PriceBreaks", self.__data,{u'Currency': u'EUR', u'Price': u'0,0', u'Quantity': 0})
        self.warning = self.getFromDict('RestrictionMessage', self.__data, "Aucune information")

        #computing of data product (price, delays...)
        if(computeData and realItem==True):
            self.__computeUnitPrice()

        self.__computeAvailableQantities()

    """!
        @brief Find data from API
        @return void
    """
    def initData(self):
        """Init data with utf-8 format"""

        self.datasheet = self.getFromDict("DataSheetUrl", self.__data, self.datasheet)
        self.category = self.getFromDict("Category", self.__data, self.category)
        self.lifeCyle = self.getFromDict("LifecycleStatus", self.__data, self.lifeCycle)
        self.description = self.getFromDict("Description", self.__data,self.description)
        self.manufacturer = self.getFromDict("Manufacturer", self.__data,self.manufacturer)
        self.infos = self.getFromDict("ProductDetailUrl", self.__data,self.infos)
        self.fabricantPartNumber = self.getFromDict("MouserPartNumber", self.__data,self.fabricantPartNumber)
        self.avaibility = self.getFromDict("Availability", self.__data,self.avaibility)
        self.unitWeight = self.getFromDict("UnitWeightKg", self.__data,self.unitWeight)
        self.minimalOrderQuantity = self.getFromDict("Min", self.__data,self.minimalOrderQuantity)
        self.groupeOrder = self.getFromDict("Mult", self.__data,self.groupeOrder)
        self.leadTime = self.getFromDict("LeadTime", self.__data,self.leadTime)

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
        if(self.lifeCyle=="Obsolete"):
            return True
        else:
            return False

    """!
        @brief Compute unit price of item
        @return void
    """
    def __computeUnitPrice(self):
        priceInfo = []
        for item in self.__priceBreaks:
            priceInfo.append([item['Quantity'], item['Price'].split()[0], item['Currency']])  

        #Set higher price for beginning
        if(len(priceInfo)==0):
            self.unitPrice = 0.0
            return 
        else:
            self.unitPrice = float(priceInfo[0][1].replace(",", "."))
        nbPass=0  #Count of pass to set the range

        for p in priceInfo:
            if(p[0]<=self.wishedQuantity):
                nbPass +=1
        if(nbPass==0):
            self.unitPrice = float(priceInfo[-1][1].replace(",", "."))
        else:
            self.unitPrice = float(priceInfo[nbPass-1][1].replace(",", "."))

    """!
        @brief Compute available quantities
        @return void
    """
    def __computeAvailableQantities(self):

        quantities = [int(data) for data in self.avaibility.split() if data.isdigit()]
        info = [data.lower() for data in self.avaibility.split() if not data.isdigit()]

        strInfo = "".join(info)

        if(strInfo in self.__availableItems):

            self.isAvailableForOrder =True
            self.availableOrderQuantity = int(quantities[0])

            if(self.availableOrderQuantity>=self.wishedQuantity):
                self.directOrder = True


