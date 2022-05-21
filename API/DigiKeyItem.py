# -*- coding: utf-8 -*-
from .Item import Item

class DigiKeyItem(Item):

    def __init__(self, partData, wishedPartName, wishedQuantity, computeData = False, apiName = "Farnell", realItem = True):
        """ New item, if computeData is False, don't compute the price beacuse may raise some errors"""

        Item.__init__(self, wishedPartName, wishedQuantity, apiName, realItem)

        self.__data = partData

        #Init value
        self.initData()

        if('stock' in self.__data):
            if('leastLeadTime' in self.__data['stock']):
                self.leadTime = self.getFromDict('stock', self.__data,'')['leastLeadTime']
        else:
            return None

        #Mean lead time
        self.meanLeadTime = "2 semaines"

        #Dict
        self.__priceBreaks = self.getFromDict("prices", self.__data,{u'to': u'9', u'from': u'1', u'cost': 0.0})
       
        #List
        self.warning = self.getFromDict('RestrictionMessage', self.__data, "Any message")


        #computing of data product (price, delays...)
        if(computeData and realItem==True):
            self.__computeUnitPrice()

        self.__computeAvailableQantities()

    def initData(self):


        self.datasheet = self.getFromDict('datasheets', self.__data, self.datasheet)
        if(self.datasheet!=self.datasheet):
            self.datasheet = self.datasheet[0]["url"]

 

    def getFromDict(self, key, d, defaultValue):

        if(key in d):
            return d[key]
        else:
            return defaultValue

    def __repr__(self):
        return "Item : "+str(self.__data)

    def update(self):
        """Update some info on item"""
        self.__computeUnitPrice()
        self.__computeAvailableQantities()

    @property
    def isObsolete(self):
        """Check if item is obsolete """
        if(self.lifeCyle=="NO_LONGER_MANUFACTURED"):
            return True
        else:
            return False

    @property
    def availableQuantities(self):
        return self.availableOrderQuantity


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
        
