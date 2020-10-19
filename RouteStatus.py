import python_config
import mysql.connector
import traceback
import sys
import GlobalFunctions

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

