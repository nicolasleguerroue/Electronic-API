# -*- coding: utf-8 -*-

import requests
import json

from .ItemManager import ItemManager
from .MouserItem import MouserItem

class MouserAPI(ItemManager):

    """!
    @brief Constructor
    @param url of API
    @param apiKey
    @param API version
    @return
    """
    def __init__(self, url, apiKey, version):

        ItemManager.__init__(self, MouserItem({}, "", 0, apiName="Mouser", computeData = False)) 
        
        self.checkType(url, str)
        self.checkType(apiKey, str)
        self.checkType(version, float)

        self.apiName  ="Mouser"

        self.__url = url
        self.__apiKey = apiKey
        self.__version = version

        self.__querySuccess = 200   #API return code when succesfull query
        self.__queryError = 403     #API return code when error of login or overlimit of number of queries

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

        

        queryPostParameters = {"SearchByPartRequest": {"mouserPartNumber":partNumber}}
        queryGetParameters = {"apiKey": self.__apiKey,"version:": self.__version}

        result = self.__request(queryGetParameters, queryPostParameters)

        if (result.status_code == self.__querySuccess ):

            self.writeLogs("Query on "+partNumber)
            self.__data = result.json()

            for data in self.__data["SearchResults"]["Parts"]: #Get all items

                tmpItem = MouserItem(data, partNumber, wishedQuantity, computeData = False)
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
                self.appendSimilarItem(MouserItem({}, partNumber, wishedQuantity, computeData = True, realItem=False))

            if(len(self.obsoleteItems)==0):
                self.appendObsoleteItem(MouserItem({}, partNumber, wishedQuantity, computeData = True, realItem=False))


            if(len(self.items)==0):
                #Any result
                return [MouserItem({}, partNumber, wishedQuantity, computeData = True, realItem=False)]
            else:
                return self.items
        else:
            print("[MOUSER ERROR] : Code "+str(result.status_code))
            if (result.status_code == self.__queryError):
                self.writeLogs("[MOUSER ERROR] Too many requests per second or invalid login!")
                print("[MOUSER ERROR] Too many requests per second or invalid login!")
            
            self.appendObsoleteItem(MouserItem({}, partNumber, wishedQuantity, computeData = False, realItem=False))
            self.appendSimilarItem(MouserItem({}, partNumber, wishedQuantity, computeData = False, realItem=False))
            return [MouserItem({}, partNumber, wishedQuantity, computeData = False)]

    """
    @brief Make the request to API
    @param List of GET parameters 
    @param List of POST parameters 
    @return 
    """
    def __request(self, queryGetParameters, queryPostParameters ):

        self.checkType(queryGetParameters, dict)
        self.checkType(queryPostParameters, dict)

        header = {'Content-Type': 'application/json'}  #Set header

        baseURL = self.__url + "?"                      #baseURL use GET method
        for key, value in queryGetParameters.items():
            baseURL += key + "=" + str(value) + "&"
        baseURL = baseURL[:-1]

        return requests.post(baseURL, data=json.dumps(queryPostParameters), headers=header)  #data are sent by POST method


def main():


    api = MouserAPI("https://api.mouser.com/api/v1.0/search/partnumber", "apiKey", 1.0)
    allItems = api.searchByPartNumber("WR04X40R2FTL", wishedQuantity=32, removeObsolete = True)    #BC337
    api.exportData("Mouser.html", "w", allItems)


if __name__ == "__main__":
    
    main()
