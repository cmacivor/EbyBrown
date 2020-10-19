import GlobalFunctions
import sys, os
import traceback
import mysql.connector
import python_config
from pathlib import Path

def process(containerId):
    #get file paths
    datFileConverterConfig = python_config.read_fileconverter_config()
    #inputPath = datFileConverterConfig.get('input_path')
    outputPath = datFileConverterConfig.get('output_path')
    #inputProcessedPath = datFileConverterConfig.get('input_processed_path')
    #outputProcessedPath = datFileConverterConfig.get('output_processed_path')
    #fileDeleteInterval = datFileConverterConfig.get('file_delete_interval')

    #query the dat_master table against the containerId, get the jurisdiction and qty
    datFileRecord = getDatFileRecordByContainerId(containerId)

    #create the sub dat file contents
    fileContents = createFileContents(datFileRecord)

    fileName = containerId.strip() + ".dat"

    fullFilePath = outputPath + "\\" + fileName

    #check if the file exists
    #if fullFilePath.is_file():
    if os.path.exists(fullFilePath):
        #overwrite it
        test = fullFilePath
    else:
        #create a new one
        with open(fullFilePath, "w") as containerFile:
            containerFile.write(fileContents)
            print(containerFile.name + " created." )






    #create the sub dat file

#TODO: what to do if the fields are blank?
def createFileContents(datrecord):
    jurisdiction = datrecord[8]
    carton_quantity = datrecord[9]

    fileContents = jurisdiction + "," + "000000" + "," + carton_quantity

    return fileContents




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

        cursor.close()
        assignmentConnection.close()
        return result
    except Exception as e:
        exc_type, exc_value, exc_traceback = sys.exc_info()
        lines = traceback.format_exception(exc_type, exc_value, exc_traceback)
        exceptionMsg = exc_value.msg
        exceptionDetails = ''.join('!! ' + line for line in lines)
        
        GlobalFunctions.logExceptionStackTrace(exceptionMsg, exceptionDetails)


if __name__ == "__main__":
    process("FB1005530-007  ")