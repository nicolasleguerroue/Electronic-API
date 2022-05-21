# -*- coding: utf-8 -*-

from datetime import datetime
import json

class Utils:

    """!
    @brief Constructor
    """
    def __init__(self):
        pass

    """
    @brief Return a list of [references, quantities]
    @param input JSON file
    @return list of list
    """
    def readJsonFile(self,inputFilename, globalName, attributList):

        inputFile = open(inputFilename, "r")
        rawData = json.loads(inputFile.read())

        lists = [] #output list

        for n in range(0,len(attributList)):
            lists.append([])

        if(not globalName in rawData):
            print(">>>Global '"+globalName+"' index doesn't exist in "+inputFilename+" file !")
            exit(1)

        for ref in rawData[globalName]:

            for l in range(0,len(lists)):
                try:    
                    lists[l].append(str(ref[attributList[l]]))
                except:
                    print(">>>'partNumber' index doesn't exist in "+inputFilename+" file !")


        return lists

    if __name__ == "__main__":
        main()
