
# -*- coding: utf-8 -*-

from .Item import Item
from datetime import datetime
import sys
import json

"""
!@brief This class is used to manage list of Items
"""
class ItemManager:

    """!
    @brief Constructor
    @param defaultItem
    @return
    """
    def __init__(self, defaultItem=None):
        
        self.__items = []                #List of Item found
        self.__obsoleteItems = []        #List of obsolete Items
        self.__similarItems = []         #List of similar Items
        self.__data = None #All data array

        self.defaultItem = defaultItem   

        self.__apiNumber = 3
        self.__apiNames = ["Mouser","Farnell", "Future"]

    """!
        @brief Set the filename of log file
        @param Filename
        @return
    """
    def setLogFile(self, filename):
        """Set the path and filename of log file"""
        self.checkType(filename, str)

        self.__logFilename = filename
        
    """!
        @brief Write a string in file log
        @param data to write (str) 
        @return
    """
    def writeLogs(self, message, writeDate = True):

        self.checkType(message, str)
        self.checkType(writeDate, bool)
        
        try:
            tmpFile = open(self.__logFilename, "a")
        except OSError as e:
            print("Can not create '"+self.__logFilename+"' file : "+e)
            sys.exit()
        if(writeDate):
            tmpFile.write(datetime.today().strftime('%Y-%m-%d %H:%M:%S')+" : "+message+"\n")
        else:
            tmpFile.write(message+"\n")
        tmpFile.close()

    """!
        @brief This method is used to check the type of argument passed in function
        @param Variable to check
        @param Type to check
        @return Assert error
    """
    def checkType(self, arg, typeArg):
        
        assert isinstance(arg, typeArg), "Expected "+str(typeArg)+" but real type is "+str(type(arg))

    """!
        @brief Return the raw data from API
        @return The raw data
    """
    @property
    def data(self):
        return self.__data

    """!
        @brief This method is used to set the raw data from API
        @param The raw data
        @return
    """
    @data.setter
    def data(self, data):
        self.__data = data

    """!
        @brief Return the list of items stored
        @return The list of items
    """
    @property
    def items(self):
        return self.__items

    """!
        @brief Set the Item list
        @param List of Item
    """
    @items.setter
    def items(self, itemList):
        self.__items = itemList

    """!
        @brief Return the list of items stored
        @return The list of items
    """
    @property
    def obsoleteItems(self):
        return self.__obsoleteItems

    """!
        @brief Set the obsolete Item list
        @param List of obsolte Item
    """
    @obsoleteItems.setter
    def obsoleteItems(self, itemList):
        self.__obsoleteItems = itemList

    """!
        @brief Return the list of similar items stored
        @return The list of items
    """
    @property
    def similarItems(self):
        return self.__similarItems

    """!
        @brief Set the obsolete Item list
        @param List of obsolte Item
    """
    @similarItems.setter
    def similarItems(self, itemList):
        self.__similarItems = itemList

    """!
        @brief Append one item in internal list
        @return item to append in internal list
    """
    def appendItem(self, item):
        self.items.append(item)

    """!
        @brief Append one obsolete item in internal list
        @return item to append in internal list
    """
    def appendObsoleteItem(self, item):
        self.obsoleteItems.append(item)

    """!
        @brief Append one obsolete item in internal list
        @return item to append in internal list
    """
    def appendSimilarItem(self, item):
        item.similarItem = True
        self.similarItems.append(item)

    """!
        @brief Clean the useless item properties
        @return list clean
    """
    def cleanItems(self, itemList):
        self.checkType(itemList,list)

        for item in itemList:

            item.isBestPrice = False

    """!
        @brief Update price and quantity
        @return list updated
    """ 
    def update(self, itemList):

        for item in itemList:

            if(item.realItem==True):
                item.update()

        return itemList

    """!
        @brief remove all obsolete items in internal
        @param Update internal list : If True, update and delete all obsolete items in internal list
        @return All no obsolete Item 
    """
    def removeObsoleteItems(self, update=True):

        self.checkType(update, bool)

        noObsoleteItems=[]
        for item in self.items:
            if(item.isObsolete):
                pass
            else:
                noObsoleteItems.append(item)

        if(update):
            self.items = noObsoleteItems
        return noObsoleteItems

    """!
        @brief This method is used to search all available Item by direct order (Direct order Item is an Item wich available quantity is higher or equal to wished quantity)
        @param Item list to filter
        @return All available direct order
    """
    def searchAvailableProducts(self, itemList, all=True):
        self.checkType(itemList, list)

        outputList = []
        #print("Length of available input list = "+str(len(itemList)))
        if(itemList[0].realItem==False and len(itemList)==1):  #return same item if first item  if one item item not available
            return [itemList[0]]

        #Similar manager
        if(itemList[0].similarItem and itemList[0].realItem==False and len(itemList)==1):  #return if fisrt item not available
                return [itemList[0]]

        if(itemList[0].similarItem and itemList[0].realItem and len(itemList)==1):  
            if(not itemList[0].isAvailableForOrder):    #Similar item with not enought quantity
                tmpItem = self.defaultItem
                tmpItem.realItem = False
                tmpItem.similarItem = False  #True
                return [tmpItem]

        if(itemList[0].realItem and len(itemList)==1):   
            #CHANGES
            return [itemList[0]]

        for item in itemList:
            if(item.isAvailableForOrder):
                outputList.append(item)

        if(len(outputList)==0): #Any product available -> return best price item
            return [self.searchBestPrice(itemList)] 

        return outputList

    """!
        @brief This method is used to search all available Item by direct order (Direct order Item is an Item wich available quantity is higher or equal to wished quantity)
        @param Item list to filter
        @return All available direct order
    """
    def searchAvailableDirectOrder(self, itemList):
        self.checkType(itemList, list)

        outputList = []

        if(itemList[0].realItem==False and len(itemList)==1):  #return if fisrt item not available
            return [itemList[0]]

        if(itemList[0].realItem and len(itemList)==1):   
            return [itemList[0]]

        for item in itemList:
            if(item.isAvailableForOrder):
                if(item.directOrder):

                    #Change status if similar Item -> change to available item
                    if(item.similarItem):
                        #item.similarItem = False
                        item.similarAvailableItem = True
                    outputList.append(item)

        if(len(outputList)==0): #Any product available -> return best price item
            tmpItem = self.searchBestPrice(itemList)
            tmpItem.isAvailableForOrder = False  
            tmpItem.setBestPrice(False)
            return [tmpItem] 

        return outputList


    """!
        @brief Compute Item with best price among a given list of Item
        @param Update internal list : If True, update and delete all obsolete items in internal list
        @return The item with best price
    """
    def searchBestPrice(self, itemList):


        if(itemList[0].realItem==False and len(itemList)==1):  #return if first item not available
            return itemList[0]

        minimalPrice = itemList[0].unitPrice
        minimalItem = itemList[0]

        numberItemMOQ = 0 #Number of item with MOQ > 1

        #try to delete item with MOQ > 1
        tmpListMOQ = []         #List of item with MOQ==1

        bestMOQ = 10000000      #Impossible MOQ

        tmpItemBestMOQ =  itemList[0]

        tmpItemList = itemList[0]
        index=0
        for item in itemList:

            if(int(item.minimalOrderQuantity)>1):
                numberItemMOQ+=1
                if(int(item.minimalOrderQuantity)<int(bestMOQ)):
                    tmpItemBestMOQ = item
            else:
                tmpListMOQ.append(item)    
            index+=1

        if(len(tmpListMOQ)==0):
            tmpItemList = tmpItemBestMOQ
        else:
            tmpItemList = tmpListMOQ

        #Compute best price
        for item in tmpListMOQ:  #itemList
            if(float(item.unitPrice)<float(minimalPrice)):
                minimalPrice = item.unitPrice
                minimalItem = item

        


        if(minimalItem.similarItem):
            minimalItem.setBestSimilarPrice(True)
        else:
            minimalItem.setBestPrice(True)


        return minimalItem

    """!
        @brief Export item list under HTML format
        @param Output filename 
        @return The item with best price
    """
    def exportData(self, filename, method, itemList, searchMethod="", exportFormat = "html"):
        """Write result in HTML file"""

        self.checkType(filename, str)
        self.checkType(method, str)
        self.checkType(itemList, list)


        partNumber = ""
        apiName = ""


        if(exportFormat=="json"):
            #export json data
            data = {}
            data["status"] = "OK"
            data["message"] = "Message"
            tmpResult = []
            for item in itemList:

                tmpResult.append({
                    "fabricantPartNumber": item.fabricantPartNumber,
                    "unitPrice": item.unitPrice,
                    "isBestPrice": item.isBestPrice,
                    "availableOrderQuantity": item.availableOrderQuantity,
                    "isAvailableForOrder": item.isAvailableForOrder,
                    "wishedQuantity": item.wishedQuantity,
                    "searchedPartNumber": item.searchedPartNumber,
                    "directOrder": item.directOrder,
                    "minimalOrderQuantity" : item.minimalOrderQuantity,
                    "groupeOrder" : item.groupeOrder,
                    "datasheet" : item.datasheet,
                    "apiName": item.apiName,
                    "warning": item.warning,
                    "realItem": item.realItem,
                    "similarItem" : item.similarItem,
                    "isObsolete" : item.isObsolete
                })
            data["result"] = tmpResult

            with open(filename, method) as outfile:
                json.dump(data, outfile)
            return

        if(exportFormat=="csv"):
            #export json data

            with open(filename, "w") as csvfile:

                #Create Header
                
                header = "Reference demandee;"

                #Ref found
                for item in range(self.__apiNumber):
                    header += "REF "+self.__apiNames[item]+";"    
                #Unit price
                for item in range(self.__apiNumber):
                    header += "PU "+self.__apiNames[item]+";"
                #MOQ
                for item in range(self.__apiNumber):
                    header += "MOQ "+self.__apiNames[item]+";"

                #Quantity
                for item in range(self.__apiNumber):
                    header += "Quantitee "+self.__apiNames[item]+";"        

                #delai
                for item in range(self.__apiNumber):
                    header += "Delais "+self.__apiNames[item]+";" 

                #Descr
                for item in range(self.__apiNumber):
                    header += "Description "+self.__apiNames[item]+" ;"      

                #Obsolete
                for item in range(self.__apiNumber):
                    header += "Obsolete "+self.__apiNames[item]+" ?;"            

                #Fournisseur;Prix unitaire;MOQ;Quantite disponible;Delai;Obsolete ?\n"
                csvfile.write(header+"\n")
                i=0

                refSearched = ""
                refFound = ""
                data=""
                ref = []
                pu = []
                moq = []
                qty = []
                delai = []
                description = []
                obs = []

                delimiter = ";"

                nbPass=0
                for item in itemList:

                    if(i%3==0):
                        for tmpRef in ref:
                            data += str(tmpRef)  + delimiter 
                        for tmpPu in pu:
                            data += str(tmpPu)  + delimiter 
                        for tmpMoq in moq:
                            data += str(tmpMoq)   + delimiter 
                        for tmpQty in qty:
                            data += str(tmpQty)   + delimiter 
                        for tmpDelai in delai:
                            data += str(tmpDelai)  + delimiter  
                        for tmpDescription in description:
                            data += str(tmpDescription)  + delimiter  
                        for tmpObs in obs:
                            data += str(tmpObs)   + delimiter 

                        csvfile.write(refSearched+";"+data+"\n")

                        ref=[]
                        delai = []
                        moq = []
                        obs = []
                        pu = []
                        qty  =[]
                        description = []

                        data=""

                    if(i%3==0):
                        refSearched = item.searchedPartNumber

                    if(i%3==0):
                        refFound = item.fabricantPartNumber
                    
                    ref.append(item.fabricantPartNumber)
                    pu.append(item.unitPrice)
                    moq.append(item.minimalOrderQuantity)
                    qty.append(item.availableOrderQuantity)
                    delai.append(item.meanShippingTime)
                    description.append(item.description)
                    obs.append(item.isObsolete)

                    i+=1

                data = ""
                for tmpRef in ref:
                    data += str(tmpRef)  + delimiter 
                for tmpPu in pu:
                    data += str(tmpPu)  + delimiter 
                for tmpMoq in moq:
                    data += str(tmpMoq)   + delimiter 
                for tmpQty in qty:
                    data += str(tmpQty)   + delimiter 
                for tmpDelai in delai:
                    data += str(tmpDelai)  + delimiter  
                for tmpDescription in description:
                    data += str(tmpDescription)  + delimiter  
                for tmpObs in obs:
                    data += str(tmpObs)   + delimiter 

                csvfile.write(refSearched+";"+data+"\n")
                return
        
        if(len(itemList)==0):
            pass
        else:

            partNumber = str(itemList[0].searchedPartNumber)
            apiName = str(itemList[0].apiName)

        out = '<table style="width:100%; border-collapse:collapse;" border="1">\n\t<caption>\n\t\tRésultats API '+str(apiName)+' - '
        out += str(partNumber)+' - '+str(searchMethod)+'\n\t</caption>\n<thead> \n<tr style="text-align:center;">\n\t<th>N°</th>\n\t<th>API</th>\n\t<th>Référence souhaitée</th>\n\t<th>Référence trouvée</th>\n\t<th>Désignation</th>\n\t<th style="text-align:left;">Catégorie</th>\n\t<th style="text-align:left;">Prix unitaire</th>\n\t<th style="text-align:left;">MOQ</th>\n\t<th>Conditionnement</th><th style="text-align:left;">Quantité disponible</th>\n\t<th style="text-align:left;">Temps d\'approvisionnement</th>\n\t<th style="text-align:left;">Fabricant</th>\n\t<th style="text-align:left">Obsolète ?</th>\n\t<th>Disponible pour une commande ?</th>\n<th style="text-align:left;">Temps de livraison</th>\n\t<th>Composant existant ?</th><th>Sim</th>\n\t<th>Datasheet</th>\n\t</tr>\n\t</thead>\n<tbody>'
        i=0
        for item in itemList:
            i+=1
            partNumber = str(item.searchedPartNumber)

           
            if(item.isBestPrice and item.directOrder==True):
                out+='<tr style="color:green">'
            elif(item.isBestPrice and item.directOrder==False):
                out+='<tr style="color:black">'
            elif(item.isObsolete):
                out+='<tr style="color:red">'
            elif(item.similarItem and item.isBestSimilarPrice==False):
                out+='<tr style="color:orange">'
            elif(item.realItem==False and item.similarItem):
                out+='<tr style="color:grey">'
            elif(item.realItem==False):
                out+='<tr style="color:grey">'
            elif(item.isBestSimilarPrice):
                out+='<tr style="color:blue">'
            else:
                 out+='<tr style="color:black">'

            out+="<td><b>"+str(i)+"</b></td>"
            out+="<td>"+str(item.apiName)+"</td>"
            out+="<td>"+str(item.searchedPartNumber)+"</td>"
            out+="<td>"+str(item.fabricantPartNumber)+"</td>"
            out+="<td>"+str(item.description)+"</td>"
            out+="<td>"+str(item.category)+"</td>"
            out+="<td>"+str(item.unitPrice)+"</td>"
            out+="<td>"+str(item.minimalOrderQuantity)+"</td>"
            out+="<td>"+str(item.groupeOrder)+"</td>"
            out+="<td>"+str(item.availableOrderQuantity)+"</td>"
            out+="<td>"+str(item.leadTime)+"</td>"
            out+="<td>"+str(item.manufacturer)+"</td>"
            out+="<td>"+str(item.isObsolete)+"</td>"
            out+="<td>"+str(item.directOrder)+"</td>"
            out+="<td>"+str(item.meanShippingTime)+"</td>"
            out+="<td>"+str(item.realItem)+"</td>"
            out+="<td>"+str(item.similarItem)+"</td>"
            if(item.datasheet!=""):
                out+='<td><a download="true" href="'+item.datasheet+'"><button>Datasheet</button></a></td>'
            else:
                out +='<td>Aucune datasheet</td>'
            #else:
            #    out+="<td>Aucune datasheet</td>"
            out+="</tr>"
            i+=1
        
        out += """</table>"""
        file = open(filename, method)
        file.write(out)

        #print(out)
        file.close()

