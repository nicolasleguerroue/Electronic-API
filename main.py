#############################################################################
############################## Includes #####################################
#############################################################################
from API.ItemManager import ItemManager

from API.MouserAPI import MouserAPI
from API.FarnellAPI import FarnellAPI
from API.FutureAPI import FutureAPI

from Utils.Utils import Utils
from Utils.CSV import CSV

from datetime import datetime
import os.path as path
import os
import time

from API.ThreadAPI import ThreadAPI

#############################################################################
############################## Settings #####################################
#############################################################################
inputPartNumberFilename = "JSON/inputPartNumbers.json"              #Input references and quantities
outputPartNumberFilename = "JSON/outputPartNumbers.json"            #Output Json result

#JSON files
outputFile = open(outputPartNumberFilename, "w")

backupsDirectory = "Results"      #relative backups directory
couterFilename = backupsDirectory+"/counter.txt"                                                 #Counter of queries

#Error code
exitOK = 0                  #Any error
exitTooManyQueries = 1      #Too many queries
exitBadInputFormat = 2      #Bad input format

#############################################################################
############################## Multi Threadings #############################
#############################################################################


"""!
@brief Call API to get prices and availabilities
@param ItemManager instance : MouserAPI, FarnelAPI... (inherit from ItemManager)
@param references : list of references
@param quantities : list of quantities
@param HTML output file
@param List of item (passed by reference) to get data later
@return
"""
def execThread(itemManager, references, quantities, exportFile, itemList):

    assert isinstance(itemManager, ItemManager), "Expected "+str("ItemManager")+" but real type is "+str(type(itemManager))

    file = open(exportFile, "w")
    header  = "<h3>Légende</h3>\n"
    header +="<span style='color:green;'>IRF520N</span> : Composant trouvé en ayant le meilleur prix et en quantité suffisante<br>\n"
    header +="<span style='color:black;'>IRF520N</span> : Composant trouvé mais quantité insuffisante<br>\n"
    header +="<span style='color:red;'>IRF520N</span> : Composant obsolète<br>\n"
    header +="<span style='color:blue;'>IRF520N</span> : Composant équivalent au meilleur prix et en quantité suffisante<br>\n"
    header +="<span style='color:orange;'>IRF520N</span> : Composant équivalent<br>\n<hr>\n"
    file.write(header)
    file.close()
    
    #For each reference
    for ref in range(0,len(references)):

        time.sleep(2)         #Delay to avoid make too queries per second
        tmpItemList = []        #List of tmp Item

        print("Requête pour la référence "+references[ref]+" sur "+str(itemManager.apiName))

        #All items
        allItems = itemManager.searchByPartNumber(references[ref], quantities[ref])
        itemManager.exportData(exportFile, "a", allItems, "Recherche globale ")

        #Available items
        availableItems = itemManager.searchAvailableProducts(allItems)  
        itemManager.exportData(exportFile, "a", availableItems, "Tous les produits non obsolètes")

        #Direct Items
        directItems = itemManager.searchAvailableDirectOrder(availableItems)
        itemManager.exportData(exportFile, "a", directItems, "Tous les produits directement disponibles (en stock)")

        #Best price
        bestPriceItem = itemManager.searchBestPrice(directItems)
        itemManager.exportData(exportFile, "a", [bestPriceItem], "Meilleur prix")

        #Obsolete
        #itemManager.exportData(exportFile, "a", itemManager.obsoleteItems, "Obsolete items")

        #Similar items
        itemManager.exportData(exportFile, "a", itemManager.update(itemManager.similarItems), "Tous les composants similaires")
        availableSimilarItems = itemManager.searchAvailableProducts(itemManager.similarItems)

        #itemManager.exportData(exportFile, "a",availableSimilarItems, "searchAvailableSimilarProducts")
        availableDirectOrderSimilarItem = itemManager.searchAvailableDirectOrder(availableSimilarItems)
        itemManager.exportData(exportFile, "a",availableDirectOrderSimilarItem, "TOus les composants similaires disponibles (en stock)")

        bestPriceSimilarItem = itemManager.searchBestPrice(availableDirectOrderSimilarItem)
        itemManager.exportData(exportFile, "a",availableDirectOrderSimilarItem, "Meilleur prix parmi les composants similaires")

        itemManager.update([bestPriceSimilarItem])

        #Return obsolete item if only item found
        if(bestPriceItem.realItem==False and len(itemManager.obsoleteItems)==1 and itemManager.obsoleteItems[0].isObsolete==True and bestPriceSimilarItem.realItem==False):
            tmpItemList.append(itemManager.obsoleteItems[0])
            #print("ADD1")
            continue
        #Choose of best item accroding the state and length of result
        if(bestPriceItem.realItem==True):
            #print("ADD2")
            tmpItemList.append(bestPriceItem)
        else:
            if(bestPriceSimilarItem.realItem==True):
                #print("ADD3")
                tmpItemList.append(bestPriceSimilarItem)
            else:
                #print("ADD4")
                tmpItemList.append(bestPriceItem)
        itemList.append(tmpItemList[0])
        itemManager.exportData(exportFile, "a", tmpItemList, "Meilleur composant")

##############################################################################
##################### MAIN
##############################################################################

utils = Utils()
#Date init
currentDate = datetime.utcnow()

year = currentDate.strftime("%Y")
month = currentDate.strftime("%m")
day = currentDate.strftime("%d")
minute = currentDate.strftime("%M")
second = currentDate.strftime("%S")

logsDirectory = backupsDirectory

#Get references
listDataInput = utils.readJsonFile(inputPartNumberFilename, "components", ["partNumber", "quantity"])
references = listDataInput[0]
quantities = listDataInput[1]

qua = []
for q in quantities:
    qua.append(int(q))
quantities = qua


apiList = []

apiList.append(MouserAPI("https://api.mouser.com/api/v1.0/search/partnumber", "apiKey", 1.0))
apiList.append(FarnellAPI("https://api.element14.com/catalog/products", "apiKey", "clientID", "secretID"))
apiList.append(FutureAPI("https://api.futureelectronics.com/api/v1/pim-future/lookup", "apiKey"))

start_time = time.time()

itemList = [] #List of item [[Item for Mouser], [item for Farnell]]
threads = []  #List of threads


for index in range(0,len(apiList)):

    itemList.append([])  #create slot for next API result

    apiList[index].setLogFile(logsDirectory+"/logs-"+str(apiList[index].apiName)+".txt")  #Set log file for each API
    file = open(logsDirectory+"/"+year+"-"+month+"-"+day+"-"+minute+"-"+second+"-"+str(apiList[index].apiName)+".html", "w")
    file.close()
    threads.append(ThreadAPI(index, apiList[index].apiName+" Thread", apiList[index],references, quantities, logsDirectory+"/"+year+"-"+month+"-"+day+"-"+minute+"-"+second+"-"+str(apiList[index].apiName)+".html", itemList[-1], execThread))
    #threads.append(ThreadAPI(index, str(apiList[index].apiName)+" Thread", apiList[index],references, quantities, logsDirectory+"/DATA"+str(apiList[index].apiName)+".html", itemList[-1], execThread))

outputFile = logsDirectory+"/"+year+"-"+month+"-"+day+"-"+minute+"-"+second+"-Resultats.html"
file = open(outputFile,"w"); file.close()      #Clean output file
#Start all threads
for t in threads:
    t.start()

#Wait end of all trheads
for t in threads:
    t.join()

elapsedTime = ">>> Temps d'éxécution : "+str(time.time() - start_time)+" s - "+str((time.time() - start_time)/len(references))+" s / Composant"
print(elapsedTime)
countResult = [] #Real result for each API
countSimilar = 0

mouser = 0.0
farnell = 0.0
future = 0.0
arrow = 0.0
similar = 0

for api in range(len(apiList)):
    countResult.append(0)
    for i in itemList[api]:

        if(i.realItem and i.apiName==apiList[api].apiName):
            countResult[-1]+=1.0
        if(i.similarItem):
            countSimilar+=1
    
data = "<h2>Resultats</h2><b>Nombre total de composants : "+str(len(references))+"</b><br>"
for apiIndex in range(len(apiList)):
    data += apiList[apiIndex].apiName+" : "+str(int(countResult[apiIndex]))+" composant(s) trouve(s)<br>"
data += "Equivalent : "+str(int(countSimilar))+" composants(s)<br><br><br> <a href='Result.html' download><button>Telecharger le fichier</button></a><br><br>"
data += elapsedTime
data += "<h3>Legende</h3>"
data +="<span style='color:green;'>IRF520N</span> : Composant trouvee en ayant le meilleur prix et en quantite suffisante<br>"
data +="<span style='color:black;'>IRF520N</span> : Composant trouve mais quantite insuffisante<br>"
data +="<span style='color:red;'>IRF520N</span> : Composant obsolete<br>"
data +="<span style='color:blue;'>IRF520N</span> : Composant equivalent au meilleur prix et en quantite suffisante<br>"
data +="<span style='color:orange;'>IRF520N</span> : Composant equivalent<br><hr>"
file = open(outputFile, "a")
file.write(data)
file.close()

#update price :

outputItemList = []

for index in range(0,len(itemList[0])):
    for item in itemList:
        outputItemList.append(item[index])


apiList[0].update(outputItemList) #price update
apiList[0].exportData(outputFile, "a", outputItemList, "Tous les meilleurs produits")  #HTML Resultats.html
apiList[0].exportData(outputPartNumberFilename, "a", outputItemList, "Tous les meilleurs produits", "json")  #HJSON output



