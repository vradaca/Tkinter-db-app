import socket
from datetime import datetime
import json


def authenticate(perm, user, pas):
    token = "False"
    auth_info = []

    with open(r"C:\Users\WIN 10\Desktop\FP_projekt\dat\user.txt", 'r') as file:
        for line in file:
            line = line.strip()
            if line:  # Ignore empty lines
                permission, username, password = line.split('_')
                auth_info.append([permission, username, password])

    for info in auth_info:
        auth = tuple(info)
        if perm == auth[0] and user == auth[1] and pas == auth[2]:
            token = "True"
            log = logs(perm, user)
            break

        else:
            token = "False"
            log = 'x'

    return [token, log]

def logs(perm, user):

    logged_entry = {"Permission": perm, "Username": user, "Date": datetime.now().strftime("%d.%m.%Y."), "Time": datetime.now().strftime("%H:%M:%S")}

    with open(r"C:\Users\WIN 10\Desktop\FP_projekt\dat\log.txt", 'a') as file:
        for key, data in logged_entry.items():
            file.write(key + ": " + data + "\n")
        file.write("\n")
        json_log = json.dumps(logged_entry)
    return json_log

server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

host = socket.gethostname()
port = 12345

server_socket.bind((host, port))

server_socket.listen(1)

while True:
    client_socket, addr = server_socket.accept()

    authentication_data = client_socket.recv(1024).decode()
    permission, username, password = authentication_data.split(',')

    received_data = authenticate(permission, username, password)

    authentication_result = received_data.pop(0)
    json_log = received_data.pop(0)

    client_socket.send(authentication_result.encode())
    client_socket.send(json_log.encode('utf-8'))

    client_socket.close()