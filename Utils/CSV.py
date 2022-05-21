# -*- encoding: utf-8 -*-
#####################################################################################################
#################################### Includes #######################################################
#####################################################################################################
import csv
import sys
#####################################################################################################
#################################### Make       #####################################################
#####################################################################################################
# manage encoding
# throw exceptions or errors
# 
#####################################################################################################
#################################### Class CSV  #####################################################
#####################################################################################################

class CSV():

    ########################################################
    ################## Initializer #########################
    ########################################################
    def __init__(self):
        """ New instance of Mail class"""

        #Internal 
        self.__logFilename = ""     #Default filename of logs (+path)

        self.__rows = []            #default raws
        self.__titles = None         #Titles of columns
        #Data
        self.__cursor = 0       #Cursor to begin data reading

    ########################################################
    ################## Internal ############################
    ########################################################
    def __checkType(self, arg, typeArg):
        
        """This method is allowed to check the type of argument passed in function"""
        assert type(arg) is typeArg, "Expected "+str(typeArg)+" but real type is "+str(type(arg))

    def setLogFile(self, filename):
        """This method is allowed to set the path and filename of log file"""
        self.__checkType(filename, str)

        self.__logFilename = filename
        
    def __writeLogs(self, message):
        """Write log message in file"""
        self.__checkType(message, str)
        
        try:
            tmpFile = open(self.__logFilename, "a")
        except OSError as e:
            print("Can not create '"+self.__logFilename+"' file : "+e)
            sys.exit()
        tmpFile.write(message+"\n")
        tmpFile.close()

    def titles(self):
        """Return titles (header)"""
        return self.__titles

    def row(self):

        return self.__rows
    ########################################################
    ################## Data ################################
    ########################################################
    def searchRowsByValue(self, rowName, value):
        """ Get all lines where rownName value is equal to value"""
        self.__checkType(rowName, str)

        if(rowName not in self.__titles):
            print(self.__titles)
            return []
        else:

            index = self.__titles.index(rowName)
            outputLines = []

            for line in self.__rows:

                if(line[index]==str(value)):
                    outputLines.append(line)
            return outputLines

    def extractColumn(self, rows, column):
        """ Return a lits with column data"""

        self.__checkType(rows, list)
        self.__checkType(column, str)

        if(column not in self.__titles):
            return []
        else:
            index = self.__titles.index(column)
            outputList = []

            for row in rows:
                outputList.append(row[index])
                self.__writeLogs(column+" : "+str(row[index]))
        
            return outputList


    def setCursor(self, line):
        """ Set cursor """
        self.__checkType(line, int)

        self.__cursor = line

    def __rowDecode(self, row):
        """Decode row in UTF8"""
        #print("decode")
        return [cell for cell in row]   #return [unicode(cell, 'utf8') for cell in row]
        
    def parse(self, filename, delimiterChar=","):
        """ Parse filename"""
        self.__checkType(filename, str)

        csvFile = open(filename, "rb")    
        csvData = csv.reader(csvFile, delimiter=delimiterChar)
        lineCursor = 0

        for row in csvData:
            if(lineCursor<self.__cursor):
                lineCursor+=1

            elif(lineCursor==self.__cursor):
                self.__titles = row
                lineCursor += 1

            else:
                lineCursor += 1
                self.__rows.append(row)

        #self.__rows.pop(0)
        #print(self.__titles)
        #print("This file has "+str(lineCursor)+" lines")




