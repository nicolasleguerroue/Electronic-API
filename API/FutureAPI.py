# -*- coding: utf-8 -*-

import requests

from .ItemManager import ItemManager
from .FutureItem import FutureItem
from datetime import datetime

class FutureAPI(ItemManager):
    """!
    @brief Constructor
    @param url of API
    @param apiKey
    @return
    """
    def __init__(self, URL, apiKey):

        ItemManager.__init__(self, FutureItem({}, "", 0, apiName="Future", computeData = False)) 
        
        self.checkType(URL, str)
        self.checkType(apiKey, str)

        self.__URL = URL
        self.__apiKey = apiKey

        self.apiName  ="Future"

        self.__querySuccess = 200   #API return code when succesfull query
        self.__queryLimit = 403     #API return code when overlimit of number of queries
        self.__queryEror = 404      #API retunr code when bad request

    """
    @brief Run the search by part number
    @param Wished part number
    @param Wished quantity
    @return 
    """
    def searchByPartNumber(self, partNumber, wishedQuantity):
        """ Search items by partNumber"""
        self.checkType(partNumber, str)
        self.checkType(wishedQuantity, int)

        #clear old queries
        self.data = None
        self.items = []
        self.similarItems =[]
        self.obsoleteItems = []

        
        self.__queryGetParameters = {
            "part_number": partNumber,
            "lookup_type":"contains"  #or "exact" -> accuracy of result
        }

        result = self.__request(self.__queryGetParameters)

        if (result.status_code == self.__querySuccess ):
            self.writeLogs("Query on "+partNumber)
            self.__data = result.json()

            #print(self.__data["lookup_results"])
            for data in self.__data["offers"]: #Get all items
                
                tmpItem = FutureItem(data, partNumber, wishedQuantity, computeData = False)
                #print("Reading of Item "+partNumber)
                fabricantPartName = tmpItem.fabricantPartNumber

                if(tmpItem.isObsolete):
                    self.appendObsoleteItem(tmpItem)
                
                if(partNumber in fabricantPartName):
                    self.appendItem(tmpItem)  
                else:
                    self.appendSimilarItem(tmpItem)       

            #Update price for all items (after sort)
            for i in self.items:
                i.update()

            #Set default Item for obsolete and similar product
            if(len(self.similarItems)==0):
                self.appendSimilarItem(FutureItem({}, partNumber, wishedQuantity, computeData = True, realItem=False))

            if(len(self.obsoleteItems)==0):
                self.appendObsoleteItem(FutureItem({}, partNumber, wishedQuantity, computeData = True, realItem=False))


            if(len(self.items)==0):
                #Any result
                return [FutureItem({}, partNumber, wishedQuantity, computeData = True, realItem=False)]
            else:
                return self.items
        else:
            print("[FUTURE ERROR] : Code "+str(result.status_code))

            if (result.status_code == self.__queryLimit):
                self.writeLogs("[FUTURE ERROR] Too many requests per second or invalid login !")
                print("[FUTURE ERROR] Too many requests per second or invalid login !")

            if (result.status_code == self.__queryEror):
                self.writeLogs("[FUTURE ERROR] Bad request !")
                print("[FUTURE ERROR] Bad request !")
            
            self.appendObsoleteItem(FutureItem({}, partNumber, wishedQuantity, computeData = False, realItem=False))
            self.appendSimilarItem(FutureItem({}, partNumber, wishedQuantity, computeData = False, realItem=False))
            return [FutureItem({}, partNumber, wishedQuantity, computeData = False)]

    """
    @brief Make the request to API
    @param List of GET parameters 
    @return 
    """
    def __request(self, queryGetParameters):

        self.checkType(queryGetParameters, dict)

        header = {"Accept":"application/json", "Content-Type": "application/json", "x-orbweaver-licensekey":self.__apiKey}  #Set header

        baseURL = self.__URL + "?"                      #baseURL use GET method
        for key, value in queryGetParameters.items():
            baseURL += key + "=" + str(value) + "&"
        baseURL = baseURL[:-1]

        return requests.get(baseURL, headers=header)  #data are sent by POST method


def main():


    api = FutureAPI("https://api.futureelectronics.com/api/v1/pim-future/lookup", "apiKey")

    allItems = api.searchByPartNumber("WR04X40R2FTL", wishedQuantity=32)    #BC337

    api.exportData("Future.html", "w", allItems)


if __name__ == "__main__":
    main()
