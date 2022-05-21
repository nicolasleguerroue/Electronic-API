# -*- coding: utf-8 -*-
import requests
from hashlib import sha1
import hmac
import base64
from datetime import datetime
from .ItemManager import ItemManager
from .FarnellItem import FarnellItem

class FarnellAPI(ItemManager):

    """!
    @brief Constructor
    @param url of API
    @param apiKey
    @param Customer ID
    @param SecretKey
    @return
    """
    def __init__(self, url, apiKey, customerId, secretKey):

        ItemManager.__init__(self, FarnellItem({},"", 0, computeData = False, apiName="Farnell", realItem=False)) 

        self.checkType(url, str)
        self.checkType(apiKey, str)
        self.checkType(customerId, str)
        self.checkType(secretKey, str)

        self.__url = url
        self.__apiKey = apiKey
        self.__secretKey = secretKey
        self.__customerId = customerId
        self.__storeInfo = "fr.farnell.com"

        self.apiName  ="Farnell"

        self.__querySuccess = 200   #API return code when succesfull query
        self.__queryError = 403     #API return code when error of login or overlimit of number of queries

    """
    @brief Run the search by part number
    @param Wished part number
    @param Wished quantity
    @return 
    """
    def searchByPartNumber(self, partNumber, wishedQuantity):

        self.checkType(partNumber, str)
        self.checkType(wishedQuantity, int)
        #Update of name
        self.defaultItem.searchedPartName = partNumber

        #clear old queries
        self.data = None
        self.items = []
        self.similarItems =[]
        self.obsoleteItems = []

        timestamp = self.__generateTimestamp()
        signature = self.__generateSignature(timestamp, "searchByManufacturerPartNumber")

        queryParameters = {
            "term": "manuPartNum:" + partNumber,
            "storeInfo.id": self.__storeInfo,
            "resultsSettings.responseGroup": "large",
            "callInfo.responseDataFormat": "JSON",
            "callinfo.apiKey": bytes(self.__apiKey,"utf-8"),
            "userInfo.customerId": self.__customerId,
            "userInfo.timestamp": timestamp,
            "userInfo.signature": signature
        }

        result = self.__request(queryParameters)

        if result.status_code == self.__querySuccess:

            self.writeLogs("Query on "+partNumber)
            self.data = result.json()
            print(self.data)

            if("products" in self.data["manufacturerPartNumberSearchReturn"]):
                pass
            else:
                #Manage of obsolete and similar items (in case of any product found)
                self.appendObsoleteItem(FarnellItem({}, partNumber, wishedQuantity, computeData = False, realItem=False))
                self.appendSimilarItem(FarnellItem({}, partNumber, wishedQuantity, computeData = False, realItem=False))
                return [FarnellItem({}, partNumber, wishedQuantity, computeData = False, realItem=False)]

            for data in self.data["manufacturerPartNumberSearchReturn"]["products"]: #Get all items
                tmpItem = FarnellItem(data,partNumber, wishedQuantity, computeData = False, apiName=self.apiName, realItem=True)

                fabricantPartName = str(tmpItem.fabricantPartNumber)

                if(tmpItem.isObsolete):
                    self.appendObsoleteItem(tmpItem)
                
                if(partNumber in fabricantPartName):
                    self.appendItem(tmpItem)  
                else:
                    self.appendSimilarItem(tmpItem)       

            #Update price for all items (after sort)
            for i in self.items:
                i.update()

            #Check if at least one item is available (qty >0)
            #Set default Item for obsolete and similar product
            if(len(self.similarItems)==0):
                self.appendSimilarItem(FarnellItem({}, partNumber, wishedQuantity, computeData = True, realItem=False))

            if(len(self.obsoleteItems)==0):
                self.appendObsoleteItem(FarnellItem({}, partNumber, wishedQuantity, computeData = True, realItem=False))


            if(len(self.items)==0):
                #Any result
                return [FarnellItem({}, partNumber, wishedQuantity, computeData = True, realItem=False)]
            else:
                return self.items

        else:
            print("[FARNELL ERROR] : Code "+str(result.status_code))

            print(result.json())
            if (result.status_code == self.__queryError):
                self.writeLogs("[FARNELL ERROR] Too many requests per second or invalid login!")
                print("[FARNELL ERROR] Too many requests per second or invalid login!")

            self.appendObsoleteItem(FarnellItem({}, partNumber, wishedQuantity, computeData = False, realItem=False))
            self.appendSimilarItem(FarnellItem({}, partNumber, wishedQuantity, computeData = False, realItem=False))
            return [FarnellItem({}, partNumber, wishedQuantity, computeData = False, realItem=False)]
    """!
    @brief Generate timestamp for UTC
    @param Timestamp
    @return Timestamp
    """
    def __generateTimestamp(self):
        return datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S.000")

    """!
    @brief Generate signature based on timestamp and specidic string
    @param Timestamp
    @param Specific string
    """
    def __generateSignature(self, timestamp, operationName):

        data = bytes(operationName + timestamp, "utf-8")
        b = bytes(self.__secretKey, "utf-8")

        hashed = hmac.new(b, data, sha1)
        signature1 = hashed.digest()
        signature2 = base64.urlsafe_b64encode(signature1) 
        return str(signature2, "utf-8")

    """
    @brief Make the request to API
    @param List of GET parameters 
    @return 
    """
    def __request(self, queryParameters):
        requestURL = self.__url + "?"
        for key, value in queryParameters.items():
            requestURL += requests.utils.quote(key) + "=" + requests.utils.quote(value) + "&"
        requestURL = requestURL[:-1]
        print(requestURL)
        res = requests.get(requestURL)
        return res


def main():

    api = FarnellAPI("https://api.element14.com/catalog/products", b"apiKey", "customerId", "secretKey")


    allItems = api.searchByPartNumber("LM324", 10, True, True)
    api.exportData("Farnell.html", "w", allItems, "searchByPartNumber")


    directItems = api.searchAvailableProducts(allItems)    

if __name__ == "__main__":
    main()
