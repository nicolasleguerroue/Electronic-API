# -*- coding: utf-8 -*-

import requests
import json

from .ItemManager import ItemManager
from .DigiKeyItem import DigiKeyItem
from datetime import datetime


class DigiKeyAPI(ItemManager):

    def __init__(self, URL, userID, userKey, redirectedURI):

        ItemManager.__init__(self, DigiKeyItem({}, "", 1, apiName="Digi-key", computeData = False)) 
        
        self.checkType(URL, str)
        self.checkType(userID, str)
        self.checkType(userKey, str)
        self.checkType(redirectedURI, str)

        self.__URL = URL
        self.__userID = userID
        self.__userKey = userKey
        self.__redirectedURI = redirectedURI

        self.apiName  ="DigiKey"

        self.__querySuccess = 200   #API return code when succesfull query
        self.__queryLimit = 403     #API return code when overlimit of number of queries
        self.__queryEror = 404      #API retunr code when bad request
        self.__tooManyQueries = 429 

    """
    Per default, remove obsolete item and remove similar product
    """
    def searchByPartNumber(self, partNumber, wishedQuantity):
        """ Search items by partNumber"""
        self.checkType(partNumber, str)
        self.checkType(wishedQuantity, int)

        #print("FUTURE")
        #clear old queries
        self.items = []
        self.similarItems =[]
        self.obsoleteItems = []

        self.data = None

        self.__queryLoginParameters = {
            "response_type": "code",
            "client_id": self.__userID,
            "redirect_uri" : requests.utils.quote(self.__redirectedURI) 
        }
        self.__queryPostParameters = {
            "includes": "IRF520",
        }



        result = self.__requestForAuth(self.__queryLoginParameters)

        #result2 = self.__request(self.__queryPostParameters)
        #print(result2.status_code)

        if (result.status_code == self.__querySuccess ):
            self.writeLogs("Query on "+partNumber)
            #print(result.text)
            #self.__data = result.json()
            #print(result.text.encode("utf-8"))

            return 
            for data in self.__data["offers"]: #Get all items

                
                
                tmpItem = DigiKeyItem(data, partNumber, wishedQuantity, computeData = False)
                #print("Reading of Item "+partNumber)
                fabricantParName = tmpItem.fabricantPartNumber

                if(tmpItem.isObsolete):
                    self.appendObsoleteItem(tmpItem)
                
                if(not partNumber in fabricantParName):
                    self.appendSimilarItem(tmpItem)

                #similar product manager
                if(partNumber in fabricantParName):
                    self.appendItem(tmpItem)

            
            #Update price for all items (after sort)
            for i in self.items:
                i.update()

            #Set default Item for obsolete and similar product
            if(len(self.similarItems)==0):
                self.appendSimilarItem(DigiKeyItem({}, partNumber, wishedQuantity, computeData = True, realItem=False))

            if(len(self.obsoleteItems)==0):
                self.appendObsoleteItem(DigiKeyItem({}, partNumber, wishedQuantity, computeData = True, realItem=False))


            if(len(self.items)==0):
                #Any result
                return [DigiKeyItem({}, partNumber, wishedQuantity, computeData = True, realItem=False)]
            else:
                return self.items
        else:
            
            
            if (result.status_code == self.__queryLimit):
                self.writeLogs("[DIGI-KEY ERROR] Too many requests per second or invalid login !")
                print("[DIGI-KEY ERROR] Too many requests per second or invalid login !")

            if (result.status_code == self.__queryEror):
                self.writeLogs("[DIGI-KEY ERROR] Bad request !")
                print("[DIGI-KEY ERROR] Bad request !")
            
            self.appendObsoleteItem(DigiKeyItem({}, partNumber, wishedQuantity, computeData = False, realItem=False))
            self.appendSimilarItem(DigiKeyItem({}, partNumber, wishedQuantity, computeData = False, realItem=False))
            return [DigiKeyItem({}, partNumber, wishedQuantity, computeData = False)]

    def __requestForAuth(self, queryGetParameters):

        self.checkType(queryGetParameters, dict)

        header = {
            "Accept":"application/json",
            "X-DIGIKEY-Client-Id": "cliendID",
            "X-DIGIKEY-Customer-Id": "customerID",
            }

        baseURL = self.__URL + "?"                      #baseURL use GET method
        for key, value in queryGetParameters.items():
            baseURL += key + "=" + str(value).replace("/", "%2F") + "&"
        baseURL = baseURL[:-1]
        print(baseURL)


        return requests.get(baseURL, header)  #data are sent by POST method


    def __request(self, queryGetParameters):

        self.checkType(queryGetParameters, dict)


        header = {
            "Accept":"application/json",
            "Authorization": "code",
            "X-DIGIKEY-Client-Id": "clientID",
            "X-DIGIKEY-Customer-Id": "customerID",
            "authorization": "Bearer bearer",
            }
        self.__URL = "https://sandbox-api.digikey.com/Search/v3/Products/Keyword"
        baseURL = self.__URL + "?"                      #baseURL use GET method
        for key, value in queryGetParameters.items():
            baseURL += key + "=" + str(value) + "&"
        baseURL = baseURL[:-1]
        print(baseURL)

        return requests.post(baseURL, headers=header)  #data are sent by POST method


def main():


    clientID = "cliendID"
    key = "key"
    Bearer = "Bearer RalaqLI5XZMPs3P8AearIg9bch6D"
    api = DigiKeyAPI("https://sandbox-api.digikey.com/v1/oauth2/authorize", clientID, key, "url")

    allItems = api.searchByPartNumber("WR04X40R2FTL", wishedQuantity=32)    #BC337


                
    #URL = https://sandbox-api.digikey.com/v1/oauth2/authorize

    #https://api.digikey.com/v1/oauth2/authorize?response_type=code&client_id=h7E4dTHl4UNGf6SV7byTr05JS3KyKrGr&redirect_uri=https%3A%2F%2F//api.digikey.com/v1/oauth2/authorize

    #api.exportData("Digi.html", "w", allItems)  #https%3A%2F%2F//api.digikey.com/v1/oauth2/authorize -> Ca't load the authorization key with API tools online


    #availableItems = api.searchAvailableProducts(allItems)  
    #api.exportData("Mouser.html", "a", availableItems)

    #directItems = api.searchAvailableDirectOrder(availableItems)    
    #api.exportData("Mouser.html", "a", directItems)

    #result = api.searchBestPrice(directItems)
    #api.exportData("Mouser.html", "a", result)


if __name__ == "__main__":
    main()
