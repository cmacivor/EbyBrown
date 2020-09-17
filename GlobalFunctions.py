import python_config
import API_02_HostLog as hostLog



def logExceptionStackTrace(exceptionMsg, exceptionDetails):
    loggingConfig = python_config.read_logging_config()

    enabled = loggingConfig.get('enabled')

    auth = loggingConfig.get('auth')
    domain = loggingConfig.get('domain')

    if enabled == "1":
        hostLog.log(auth, domain, "Socket Listener", "Exception", exceptionMsg + " StackTrace: " + exceptionDetails)
    else:
        print("Exception", exceptionMsg + " StackTrace: " + exceptionDetails)