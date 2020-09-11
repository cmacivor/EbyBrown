# EbyBrown

# Sockets Debugging Information

The relevant sockets scripts in this folder, app-server.py, libserver.py, app-client.py, and libclient.py, are from this tutorial:
https://realpython.com/python-sockets/#background

Original source code is here:
https://github.com/realpython/materials/tree/master/python-sockets-tutorial

To set this up for debugging in Visual Studio Code, first create a launch.json launch configuration file. Follow steps 1-3 in this tutorial:
https://code.visualstudio.com/docs/python/debugging


Then modify the created launch.json file to look like this. Note the "args" line at the bottom.
{
    // Use IntelliSense to learn about possible attributes.
    // Hover to view descriptions of existing attributes.
    // For more information, visit: https://go.microsoft.com/fwlink/?linkid=830387
    "version": "0.2.0",
    "configurations": [
        {
            "name": "Python: Current File",
            "type": "python",
            "request": "launch",
            "program": "${file}",
            "console": "integratedTerminal",
            "args": ["127.0.0.1","65432"] //for the server portion
            //"args": ["127.0.0.1","65432", "STX12KEEPALIVETX"] //for the client 
        }
    ]
}

Set the app-server.py file on your active tab, and hit F5 to run it. 

For the KEEPALIV message, open a separate terminal, cd into the directory and run the following: sudo python3 app-client.py 127.0.0.1 65432 "0x200012|KEEPALIV0x3"
Note the quotes- this is because of the | character, which the bash shell interprets as a pipe command.
You should get a response back in the terminal.

For the New Container Data Message:
sudo python3 app-client.py 127.0.0.1 65432 "0x200013|ADDCONTA|307604|1123|SC307604112-006|307604112|006003|SPLITCASE|113205|200x3"

For the Container Complete Data Message:
sudo python3 app-client.py 127.0.0.1 65432 "0x200013|CONTCOMP|SC307604112-006|307604112|10x3"

For the Assignment Complete Data Message:
sudo python3 app-client.py 127.0.0.1 65432 "0x200013|ASGNCOMP|3076041120x3"

For the Order Complete Data Message:
sudo python3 app-client.py 127.0.0.1 65432 "0x200013|ORDRCOMP|30760|41120x3"
