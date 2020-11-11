import os
import time

directories = ['D:\\Downloads\\Host\\Processed', 'D:\\Downloads\\UnitedSilicone', 'D:\\Downloads\\UnitedSilicone\\Processed']

def delete_dat_files():
    for directory in directories:
        filelist = [ f for f in os.listdir(directory) if f.endswith(".DAT") ]
        for f in filelist:
            os.remove(os.path.join(directory, f))

    return 'All DAT files deleted successfully'


while True:
    print(delete_dat_files())
    time.sleep(5)