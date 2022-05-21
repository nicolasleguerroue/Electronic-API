 # -*- coding: utf-8 -*-

import requests
import json

from .ItemManager import ItemManager
from .ArrowItem import ArrowItem
from datetime import datetime
import time

class ArrowAPI(ItemManager):

    """!
    @brief Constructor
    @param Url of API
    @param Login
    @param Apikey
    @param Version
    @return
    """
    def __init__(self, url, login, apiKey):

        ItemManager.__init__(self, ArrowItem({"data":"void"}, "", 0, apiName="Arrow", computeData = False)) 
        
        self.checkType(url, str)
        self.checkType(login, str)
        self.checkType(apiKey, str)

        self.apiName = "Arrow"
        self.__nbQueries = 25       #Number of queries by request
        self.__url = url
        self.__apiKey = apiKey
        self.__login = login
        self.__querySuccess = 200   #API return code when succesfull query
        self.__queryError = 403     #API return code when error of login or overlimit of number of queries
        self.__query  =404

    """
    @brief Run the search by part number
    @param Wished part number
    @param Wished quantity
    @return 
    """
    def searchByPartNumber(self, partNumber, wishedQuantity):

        self.checkType(partNumber, str)
        self.checkType(wishedQuantity, int)

        #clear old queries
        self.items = []
        self.similarItems =[]
        self.obsoleteItems = []

        self.data = None


        queryGetPartParameters = {"login": self.__login,
            "apikey":self.__apiKey,
            "search_token":partNumber,
            "rows":self.__nbQueries,
            "utm_currency" : "EUR"}
            
        result = self.__request(queryGetPartParameters)

        if (result.status_code == self.__querySuccess ):

            self.writeLogs("Query on "+partNumber)
            self.__data = result.json() 
            #print(self.__data)
            #Login error
            if(self.__data["itemserviceresult"]["transactionArea"][0]["response"]["returnMsg"]=="AUTHENTICATION FAILED"):
                print("[Arrow ERROR] Authentification failed !")

            #Any result
            if(self.__data["itemserviceresult"]["transactionArea"][0]["response"]["success"]==False):
                tmpItem = ArrowItem({"data":"void"}, partNumber, wishedQuantity, computeData = False)
                self.appendObsoleteItem(tmpItem)
                self.appendSimilarItem(tmpItem)
                return [ArrowItem({"data":"data"}, partNumber, wishedQuantity, computeData = False, realItem=False)]

            if(len(self.__data["itemserviceresult"]["data"])==0):

                tmpItem = ArrowItem({"data":"void"}, partNumber, wishedQuantity, computeData = False)
                self.appendObsoleteItem(tmpItem)
                self.appendSimilarItem(tmpItem)
                return [ArrowItem({"data":"data"}, partNumber, wishedQuantity, computeData = False, realItem=False)]

            for data in self.__data["itemserviceresult"]["data"][0]["PartList"]: #Get all items

                tmpItem = ArrowItem(data, partNumber, wishedQuantity, computeData = False)
                fabricantPartName = tmpItem.fabricantPartNumber

                if(tmpItem.isObsolete):
                    self.appendObsoleteItem(tmpItem)
                
                if(str(partNumber) in fabricantPartName):
                    self.appendItem(tmpItem)  
                else:
                    self.appendSimilarItem(tmpItem)         

            
            #Update price for all items (after sort)
            for i in self.items:
                i.update()

            #Set default Item for obsolete and similar product
            if(len(self.similarItems)==0):
                self.appendSimilarItem(ArrowItem({"data":"data"}, partNumber, wishedQuantity, computeData = True, realItem=False))

            if(len(self.obsoleteItems)==0):
                self.appendObsoleteItem(ArrowItem({"data":"data"}, partNumber, wishedQuantity, computeData = True, realItem=False))


            if(len(self.items)==0):
                #Any result
                return [ArrowItem({"data":"data"}, partNumber, wishedQuantity, computeData = True, realItem=False)]
            else:
                return self.items
        else:
            print("[ARROW ERROR] : Code "+str(result.status_code))
            if (result.status_code == self.__queryError):
                self.writeLogs("[Arrow ERROR] Too many requests per second or invalid login!")
                print("[Arrow ERROR] Too many requests per second or invalid login!")
            
            self.appendObsoleteItem(ArrowItem({"data":"data"}, partNumber, wishedQuantity, computeData = False, realItem=False))
            self.appendSimilarItem(ArrowItem({"data":"data"}, partNumber, wishedQuantity, computeData = False, realItem=False))
            return [ArrowItem({"data":"data"}, partNumber, wishedQuantity, computeData = False)]

    """
    @brief Make the request to API
    @param List of GET parameters 
    @return 
    """
    def __request(self, queryGetParameters):

        self.checkType(queryGetParameters, dict)

        header = {'Content-Type': 'application/json'}  #Set header

        baseURL = self.__url + "?"                      #baseURL use GET method
        for key, value in queryGetParameters.items():
            baseURL += key + "=" + str(value) + "&"
        baseURL = baseURL[:-1]
        print(baseURL)
        return requests.get(baseURL)  #data are sent by POST method


def main():


    api = ArrowAPI("http://api.arrow.com/itemservice/v3/en/search/token", "login","apiKey")

    allItems = api.searchByPartNumber("BC337", wishedQuantity=32)    #BC337

    api.exportData("Arrow.html", "w", allItems)

    #availableItems = api.searchAvailableProducts(allItems)  
    #api.exportData("Mouser.html", "a", availableItems)

    #directItems = api.searchAvailableDirectOrder(availableItems)    
    #api.exportData("Mouser.html", "a", directItems)

    #result = api.searchBestPrice(directItems)
    #api.exportData("Mouser.html", "a", result)


if __name__ == "__main__":
    main()
