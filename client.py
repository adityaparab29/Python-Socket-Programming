# Author
# Name: Aditya Parab

# Import the socket library
import socket
import json

# Constants for API communication
COMMAND = "command"
STATUS = "status"
PAYLOAD = "payload"
API_RESPONSE_OK = "OK"
API_RESPONSE_EMPTY = "EMPTY"


class Client:
    def __init__(self):
        # Cache for proxy
        self.cache = {}

        # Connection host and port
        self.SERVER_HOST = "127.0.0.1"
        self.SERVER_PORT = 8094

        # Socket object
        self.socket = None

        self.connect_server()

    def connect_server(self):
        # Create a socket object
        self.socket = socket.socket()
        # Connect to the server on localhost
        print(f"[*] Connecting to {self.SERVER_HOST}:{self.SERVER_PORT} ...")
        self.socket.connect((self.SERVER_HOST, self.SERVER_PORT))
        print("[+] Connected.")
        # Receive data from the server and decoding to get the string.
        print("Server reply: ", self.socket.recv(1024).decode())

    def process(self, inp):
        if inp is None or len(inp.strip()) == 0:
            print("*** Invalid command. Enter command from available options ***")
            return None

        valid = ["GET", "PUT", "DUMP", "EXIT"]
        command_list = inp.split(" ", 1)
        cmd = command_list[0].upper()
        if cmd not in valid:
            return self.invalid()

        # get name
        if cmd == "GET":
            if len(command_list) != 2:
                return self.invalid()

            command_list = command_list[:1] + [_.strip() for _ in command_list[1:]]
            return self.get(command_list)

        # put name = adi put name=adi
        elif cmd == "PUT":
            if len(command_list) != 2 or "=" not in command_list[1]:
                return self.invalid()

            command_list = command_list[:1] + [_.strip() for _ in command_list[1].split("=")]
            self.put(command_list)

        elif cmd == "DUMP":
            self.dump()

        elif cmd == "EXIT":
            return self.exit()

    """
       GET API Request Format
       {
           "command": "GET",
           "payload": "name"
       }

        GET API Good Response
       {
           "status": "OK",
           "payload": "adi"
       }

        GET API Error Response
       {
           "status": "EMPTY",
           "payload": NONE
       }
    """

    def get(self, command_list):
        key = command_list[1].upper()
        if key in self.cache:
            print("Output (From proxy server):", key, "=", self.cache[key])

        else:
            api_data = {COMMAND: "GET", PAYLOAD: key}
            try:
                self.socket.send(json.dumps(api_data).encode())
                api_response = self.socket.recv(1024).decode()
            except Exception as e:
                # Client no longer connected remove it from the set
                print(f"[!] Error: {e}")
                return self.exit()
            else:
                response = json.loads(api_response)
                if response[STATUS] == API_RESPONSE_OK:
                    self.cache[key] = response[PAYLOAD]
                    print("Output:", key, "=", response[PAYLOAD])
                elif response[STATUS] == API_RESPONSE_EMPTY:
                    print("Output: Key", key, "not found")
                else:
                    print("Something went wrong!")

        return "OK"

    """
        PUT API Request Format
        {
            "command": "PUT"
            "payload": {"name":"adi"}
        }

        PUT API Good Response
        {
            "status": "OK"
            "payload": None
        }
    """

    def put(self, command_list):
        key = command_list[1].upper()
        api_data = {COMMAND: "PUT", PAYLOAD: {key: command_list[2]}}
        try:
            self.socket.send(json.dumps(api_data).encode())
            api_response = self.socket.recv(1024).decode()
        except Exception as e:
            print(f"[!] Error: {e}")
            return self.exit()
        else:
            response = json.loads(api_response)
            if response[STATUS] == API_RESPONSE_OK:
                print("Request forwarded to the Server.")
                self.cache.pop(key, None)

    """
        DUMP API Request Format
        {
            "command": "DUMP"
        }
    
         DUMP API Good Response
        {
            "status": "OK"
            "payload": {"name":"adi"}
        }
    
         DUMP API Error Response
        {
            "status": "EMPTY"
            "payload": NONE
        }
    """

    def dump(self):
        api_data = {"command": "DUMP"}
        try:
            self.socket.send(json.dumps(api_data).encode())
            api_response = self.socket.recv(1024).decode()
        except Exception as e:
            # Client no longer connected remove it from the set
            print(f"[!] Error: {e}")
            return self.exit()
        else:
            response = json.loads(api_response)
            if response[STATUS] == API_RESPONSE_OK:
                print("Output:")
                for k, v in response[PAYLOAD].items():
                    print(k, "=", v, end="\n")
            elif response[STATUS] == API_RESPONSE_EMPTY:
                print("Output: No data found")
            else:
                print("Something went wrong!")

    def invalid(self):
        print("*** Invalid command. Enter command from available options following the exact syntax ***")
        return None

    def exit(self):
        # close the connection
        self.socket.close()
        return "EXIT"


if __name__ == '__main__':
    obj = Client()
    while True:
        inp = input("\nCommand List\n1.PUT (Format: PUT $key = $value)\n"
                    "2.GET (Format: GET $key)\n"
                    "3.DUMP (Format: DUMP)\n"
                    "4.Exit (Format: EXIT)\n"
                    "Enter your command: ")
        result = obj.process(inp)
        if result == "EXIT":
            break
