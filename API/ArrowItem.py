# -*- coding: utf-8 -*-
from .Item import Item

class ArrowItem(Item):

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
    def __init__(self, partData, wishedPartName, wishedQuantity, computeData = False, apiName="Arrow", realItem=True):

        Item.__init__(self, wishedPartName, wishedQuantity, apiName, realItem)

        #Composed data
        self.__availableItems = ["enstock"]                 #parse available data and check if possible to make order now
        self.__priceBreaks = []


        self.__data = partData
        self.initData()
        


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
        #print(self.__data['PartList'][1])
        if(len(self.__data)>0):

            #print(self.__data)

            if("InvOrg" in self.__data):


                #Detect website [Arrow or Verical]
                #print("LEN")
                #print(len(self.__data['InvOrg']["webSites"]))
                index=0
                if(len(self.__data['InvOrg']["webSites"])==1):
                    self.minimalOrderQuantity = self.__data['InvOrg']["webSites"][0]["sources"][0]["sourceParts"][0]["minimumOrderQuantity"]
                else:
                    self.minimalOrderQuantity = self.__data['InvOrg']["webSites"][1]["sources"][0]["sourceParts"][0]["minimumOrderQuantity"]
                    index=1

                #Prices
                if("Prices" in self.__data['InvOrg']["webSites"][index]["sources"][0]["sourceParts"][0]):

                    for p in self.__data['InvOrg']["webSites"][index]["sources"][0]["sourceParts"][0]["Prices"]["resaleList"]:
                        self.__priceBreaks.append(p) 
                else:
                    self.__priceBreaks.append({'displayPrice': '0.0', 'price': 0.0, 'maxQty': 99999999, 'minQty': 0})

                #Avaibility
                if("Availability" in self.__data['InvOrg']["webSites"][index]["sources"][0]["sourceParts"][0]):
                    self.availableOrderQuantity = self.__data['InvOrg']["webSites"][index]["sources"][0]["sourceParts"][0]["Availability"][0]["fohQty"]

                    #print(self.availableOrderQuantity)

                self.isAvailableForOrder = self.__data['InvOrg']["webSites"][index]["sources"][0]["sourceParts"][0]["inStock"]
                
            else:
                self.__priceBreaks.append({'displayPrice': '0.0', 'price': 0.0, 'maxQty': 99999999, 'minQty': 0})
                #print("ERREUR INV")

            self.category = self.getFromDict("categoryName", self.__data, self.category)
            self.fabricantPartNumber = self.getFromDict("partNum", self.__data,self.fabricantPartNumber)

            self.manufacturer = self.getFromDoubleDict("manufacturer","mfrName", self.__data,self.manufacturer)


            self.datasheet = self.getFromDict("hasDataSheet",  self.__data, self.datasheet)
            self.lifeCyle = self.getFromDict("status", self.__data, self.lifeCycle)
            self.description = self.getFromDict("desc",self.__data,self.description)
            
            self.infos = self.getFromDict("ProductDetailUrl", self.__data,self.infos)

            self.groupeOrder = self.getFromDict("Mult", self.__data,self.groupeOrder)
            self.leadTime = self.getFromDict("arrowLeadTime",self.__data,self.leadTime)

            if(self.minimalOrderQuantity==""):
                self.minimalOrderQuantity = 0
            else:
                self.minimalOrderQuantity = int(float((self.minimalOrderQuantity)))


    """!
        @brief Update unit price and available quantities
        @return void
    """
    def update(self):
        """Update some info on item"""
        self.__computeUnitPrice()
        #self.__computeAvailableQantities()

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
        #print("BEGIN")
        #print(self.__priceBreaks)
        for item in self.__priceBreaks:
            priceInfo.append([item['price'], item['minQty'], item['maxQty']])  
            #print("SUB")
            #print(item['price'], item['minQty'], item['maxQty'])
        #Set higher price for beginning
        if(len(priceInfo)==1):
            self.unitPrice = self.__priceBreaks[0]["price"]
            return 
        else:
            self.unitPrice = priceInfo[0][0]
        nbPass=0  #Count of pass to set the range

        for p in priceInfo:
            if(p[2]<=self.wishedQuantity):
                nbPass +=1
        if(nbPass==0):
            self.unitPrice = priceInfo[0][0]
        else:
            self.unitPrice = priceInfo[nbPass-1][0]
    """!
        @brief Compute available quantities
        @return void
    """
    def __computeAvailableQantities(self):

        if(self.availableOrderQuantity>=self.wishedQuantity):
            self.directOrder = True


