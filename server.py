# Author
# Name: Aditya Parab

# Import the socket library
import socket
from threading import Thread
import json

# Constants for API communication
COMMAND = "command"
STATUS = "status"
PAYLOAD = "payload"
API_RESPONSE_OK = "OK"
API_RESPONSE_EMPTY = "EMPTY"


class Server:
    def __init__(self):
        # initialize set for all connected client's sockets
        self.client_sockets = set()

        # Server Connection host and port
        self.SERVER_HOST = "0.0.0.0"
        self.SERVER_PORT = 8094

        # Create a socket object
        self.socket = socket.socket()
        print("Socket successfully created")

        # make the port as reusable port
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        # Bind the port
        self.socket.bind((self.SERVER_HOST, self.SERVER_PORT))
        # Put the socket into listening mode
        self.socket.listen(6)
        print(f"[*] Listening at {self.SERVER_HOST}:{self.SERVER_PORT}")

        self.run()

    def listen_for_client(self, cs):
        data = {}
        # This function keep listening for a message from `cs` socket
        while True:
            try:
                # Keep listening for a message from `cs` socket
                msg = cs.recv(1024).decode()
                if not msg:
                    host, port = cs.getpeername()
                    print(f"[-] Disconnecting client ('{host}', {port})")
                    cs.close()
                    self.client_sockets.remove(cs)
                    break
            except Exception as e:
                # Client no longer connected remove it from the set
                print(f"[!] Error: {e}")
                self.client_sockets.remove(cs)
            else:
                # if we received a message
                result = self.process(data, msg)
                cs.send(result.encode())

    # Request
    # {
    #     "command": "PUT"
    #     "payload": {"name":"adi"}
    # }

    # Request
    # {
    #     "command": "GET"
    #     "payload": "name"
    # }

    # Response
    # {
    #     "status": "OK"
    #     "payload": {"name":"adi"}
    # }

    # Error Response
    # {
    #     "status": "EMPTY"
    #     "payload": NONE
    # }
    def process(self, data, msg):
        data_rcv = json.loads(msg)
        command = data_rcv[COMMAND]

        if command == "PUT":
            data.update(data_rcv[PAYLOAD])
            return json.dumps({STATUS: API_RESPONSE_OK, PAYLOAD: None})

        elif command == "GET":
            key = data_rcv[PAYLOAD]
            if key in data:
                return json.dumps({STATUS: API_RESPONSE_OK, PAYLOAD: data[key]})
            else:
                return json.dumps({STATUS: API_RESPONSE_EMPTY, PAYLOAD: None})

        elif command == "DUMP":
            if data:
                return json.dumps({STATUS: API_RESPONSE_OK, PAYLOAD: data})
            else:
                return json.dumps({STATUS: API_RESPONSE_EMPTY, PAYLOAD: None})

    def run(self):
        while True:
            # Keep listening for new connections all the time
            client_socket, client_address = self.socket.accept()
            print(f"[+] {client_address} connected.")
            client_socket.send('Connection established. Session Started.'.encode())

            # Add the new connected client to connected sockets
            self.client_sockets.add(client_socket)

            # Start a new thread that listens for each client's messages
            t = Thread(target=self.listen_for_client, args=(client_socket,))

            # Make the thread daemon, so it ends whenever the main thread ends
            t.daemon = True

            # Start the thread
            t.start()

        # # close client sockets
        # for cs in client_sockets:
        #     cs.close()
        # # close server socket
        # s.close()


if __name__ == '__main__':
    serverObj = Server()
