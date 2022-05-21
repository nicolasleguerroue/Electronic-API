# -*- coding: utf-8 -*-
import threading


class ThreadAPI (threading.Thread):

    """!
    @brief Constructor
    @param threadID : ID of thread
    @param threadName : Name of thread
    @param itemManager : Instance of ItemManager (may be MouserAPI, FarnellAPI...)
    @param references : List of references
    @param quantities : List of quantities
    @param exportFile : Output filename
    @param itemList : List of item where data will be stored
    @return
    """
    def __init__(self, threadID, threadName, itemManager, references, quantities, exportFile, itemList, function=None):

        threading.Thread.__init__(self)

        self.threadID = threadID
        self.threadName = threadName

        self.itemManager = itemManager
        self.references = references
        self.quantities = quantities
        self.exportFile  = exportFile
        self.itemList = itemList
        self.__function = function

    """!
    @brief Call API and execute running thread
    @return
    """
    def run(self):

        print("Starting " + self.threadName+"\n")
        self.__function(self.itemManager, self.references, self.quantities, self.exportFile, self.itemList)
        print("Exiting " + self.threadName)