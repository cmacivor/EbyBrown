import sys
import socket
import selectors
import traceback

import libclient

#to run this, enter: sudo python3 app-client.py 127.0.0.1 65432 search morpheus

sel = selectors.DefaultSelector()


# def create_request(action, value):
#     if action == "search":
#         return dict(
#             type="text/json",
#             encoding="utf-8",
#             content=dict(action=action, value=value),
#         )
#     else:
#         return dict(
#             type="binary/custom-client-binary-type",
#             encoding="binary",
#             content=bytes(action + value, encoding="utf-8"),
#         )

def create_request(action):
    if action == "search":
        return dict(
            type="text/json",
            encoding="utf-8",
            content=dict(action=action, value=action),
        )
    else:
        return dict(
            type="binary/custom-client-binary-type",
            encoding="binary",
            content=bytes(action, encoding="utf-8"),
        )


def start_connection(host, port, request):
    addr = (host, port)
    print("starting connection to", addr)
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.setblocking(False)
    sock.connect_ex(addr)
    events = selectors.EVENT_READ | selectors.EVENT_WRITE
    message = libclient.Message(sel, sock, addr, request)
    sel.register(sock, events, data=message)


if len(sys.argv) != 4:
    print("usage:", sys.argv[0], "<host> <port> <action> <value>")
    sys.exit(1)

host, port = sys.argv[1], int(sys.argv[2])
#action, value = sys.argv[3], sys.argv[4]
action = sys.argv[3]
#request = create_request(action, value)
request = create_request(action)
start_connection(host, port, request)

try:
    while True:
        events = sel.select(timeout=1)
        for key, mask in events:
            message = key.data
            try:
                message.process_events(mask)
            except Exception:
                print(
                    "main: error: exception for",
                    f"{message.addr}:\n{traceback.format_exc()}",
                )
                message.close()
        # Check for a socket being monitored to continue.
        if not sel.get_map():
            break
except KeyboardInterrupt:
    print("caught keyboard interrupt, exiting")
finally:
    sel.close()