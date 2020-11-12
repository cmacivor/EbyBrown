import os
import time
import python_config
import datetime

directories = ['D:\\Downloads\\Host\\Processed', 'D:\\Downloads\\UnitedSilicone', 'D:\\Downloads\\UnitedSilicone\\Processed']

def delete_dat_files():
    config = python_config.read_fileconverter_config()
    interval = config.get('file_delete_interval')

    for directory in directories:
        filelist = [ f for f in os.listdir(directory) if f.endswith(".DAT") ]
        for f in filelist:
            path = os.path.join(directory, f)
            modifiedAt = modification_date(path)
            validFromDate = datetime.datetime.now() - datetime.timedelta(days = int(interval))
            if validFromDate > modifiedAt:
                os.remove(path)

    return 'Expired DAT files deleted successfully'

def modification_date(filename):
    t = os.path.getmtime(filename)
    return datetime.datetime.fromtimestamp(t)



delete_dat_files()
