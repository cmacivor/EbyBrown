class route_status:
    def __init__(self, id, route, dockDoor, trailerNumber, priority, enable, status, date_at, created_at, updated_at, numberLines, existingRecordCount):
        self.ID = id
        self.Route = route
        self.DockDoor = dockDoor
        self.TrailerNumber = trailerNumber
        self.Priority = priority  #+ numberLines - existingRecordCount + 1
        self.Enable = enable
        self.Status = status
        self.DateAt = date_at
        self.CreatedAt = created_at
        self.UpdatedAt = updated_at

    def getUnCompletedRouteStatuses(self):
        try:
            config = python_config.read_db_config()
            host = config.get('host')
            user = config.get('user')
            #database = config.get('database')
            wcsDatabase = config.get('wcsdatabase')
            password = config.get('password')

            connection = mysql.connector.connect(
                host= host, 
                user= user, 
                database= wcsDatabase, 
                password= password 
            )

            cursor = connection.cursor()

            getRouteStatusesSQL = "select * from route_statuses where status != 'Complete' order by priority"

            cursor.execute(getRouteStatusesSQL)

            result = cursor.fetchall()

            return result

        except Exception as e:
            print(e)
            exc_type, exc_value, exc_traceback = sys.exc_info()
            lines = traceback.format_exception(exc_type, exc_value, exc_traceback)
            exceptionMsg = exc_value.msg
            exceptionDetails = ''.join('!! ' + line for line in lines)
            
            GlobalFunctions.logExceptionStackTrace(exceptionMsg, exceptionDetails) 