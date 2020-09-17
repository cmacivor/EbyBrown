import python_config
import API_02_HostLog as hostLog



def logExceptionStackTrace(exceptionMsg, exceptionDetails):
    loggingConfig = python_config.read_logging_config()
    auth = loggingConfig.get('auth')
    domain = loggingConfig.get('domain')
    hostLog.log(auth, domain, "Socket Listener", "Exception", exceptionMsg + " StackTrace: " + exceptionDetails)