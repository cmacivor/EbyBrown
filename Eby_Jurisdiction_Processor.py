import GlobalFunctions
import sys, os
import traceback
import mysql.connector
import python_config
from pathlib import Path


config = python_config.read_db_config()
host = config.get('host')
user = config.get('user')
database = config.get('wcsdatabase')
password = config.get('password')



#TODO: what to do if the fields are blank?
#def createFileContents(datrecord):
#    jurisdiction = datrecord[8]
#    carton_quantity = datrecord[9]

#    if jurisdiction is None or jurisdiction.isspace():
#        return "JurisdictionEmpty"
    
#    if carton_quantity is None or carton_quantity.isspace():
#        return "QtyEmpty"

    #fileContents = jurisdiction + "," + "000000" + "," + "000000," + carton_quantity

#    return fileContents




def process(containerId):
    try:
        #get file paths
        datFileConverterConfig = python_config.read_fileconverter_config()

        outputPath = datFileConverterConfig.get('output_path')

        #query the dat_master table against the containerId, get the jurisdiction and qty
        #datFileRecord = getDatFileRecordByContainerId(containerId)

        #if datFileRecord == "ContainerNotFound":
        #    return "ContainerNotFound"

        #create the sub dat file contents
        #fileContents = createFileContents(datFileRecord)

        #if fileContents == "JurisdictionEmpty" or fileContents == "QtyEmpty":
        #    return fileContents

        try:
                connection = mysql.connector.connect(
                    host= host, 
                    user= user, 
                    database= database, 
                    password= password 
                )

                cursor = connection.cursor()

                query_juris = ("SELECT jurisdiction FROM assignment.dat_master WHERE container_id=\"" + containerId + "\"")
                cursor.execute(query_juris)
                extResult = cursor.fetchone()
                jurisdiction = extResult[0]
                print(jurisdiction)

                query_qty = ("SELECT carton_qty FROM assignment.dat_master WHERE container_id=\"" + containerId + "\"")
                cursor.execute(query_qty)
                extResult = cursor.fetchone()
                carton_qty = extResult[0]
                print(carton_qty)
                       
                           
                
                if jurisdiction == None:
                    return "Jurisdiction Empty"
                elif carton_qty == None:
                    return "Carton Qty Empty"
                else:
                    pass

        except Exception as e:
            print(e)                

        temp = containerId + ".dat"
        fileName = temp.replace(" ","")
        print(fileName)

        fileContents = "000" + str(jurisdiction) + ",000000,000000," + str(carton_qty)
        print(fileContents)        

        fullFilePath = outputPath + "\\" + fileName
        print(fullFilePath)

        
        with open(fullFilePath, "w") as containerFile:
            containerFile.write(fileContents)
            print(containerFile.name + " created." )
            return "Success"
        
    except Exception as e:
        print(e)
        exc_type, exc_value, exc_traceback = sys.exc_info()
        lines = traceback.format_exception(exc_type, exc_value, exc_traceback)
        #exceptionMsg = exc_value.msg
        exceptionDetails = ''.join('!! ' + line for line in lines)
        
        #GlobalFunctions.logExceptionStackTrace(exceptionMsg, exceptionDetails)
        return "Unknown"


def deleteFile(containerId):
    datFileConverterConfig = python_config.read_fileconverter_config()

    outputPath = datFileConverterConfig.get('output_path')

    fileName = containerId.strip() + ".dat"

    fullFilePath = outputPath + "\\" + fileName

    if os.path.exists(fullFilePath):
        os.remove(fullFilePath)
    else:
        print(fullFilePath + " not found")










def getDatFileRecordByContainerId(containerId):
    try:
        config = python_config.read_db_config()
        host = config.get('host')
        user = config.get('user')
        database = config.get('database')
        password = config.get('password')

        assignmentConnection = mysql.connector.connect(
            host = host,
            user = user,
            database = database,
            password = password
        )

        cursor = assignmentConnection.cursor()
 
        sql = "select * from dat_master where container_id = %s"

        queryValues = (containerId,)

        cursor.execute(sql, queryValues)

        result = cursor.fetchone()

        if result == None:
            return "ContainerNotFound"

        cursor.close()
        assignmentConnection.close()
        return result
    except Exception as e:
        exc_type, exc_value, exc_traceback = sys.exc_info()
        lines = traceback.format_exception(exc_type, exc_value, exc_traceback)
        exceptionMsg = exc_value.msg
        exceptionDetails = ''.join('!! ' + line for line in lines)
        
        GlobalFunctions.logExceptionStackTrace(exceptionMsg, exceptionDetails)


#if __name__ == "__main__":
    #deleteFile("FB1005530-007")
#    process("FB1005530-007  ")
    #process("FB1005530-00  ")