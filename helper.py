import socket
import select
import json
import logging
class c_HelperFunctions():
    def m_Is_ID_In_List(self,list,ID):
        self.bIsFound = False
        for CheckID in list:
            if CheckID == ID:
                self.bIsFound = True
                return True

        return self.bIsFound
class Client():
    def __init__(self, ip, port, Tasks):
        self.ip = ip
        self.port = port
        self.Tasks = Tasks
    def m_SerialiseSyncTasks(self):
        self.output = []
        for ID in self.Tasks.Order:
            self.TaskData = {}
            self.TaskData["ID"] = ID
            self.TaskData["Data"] = {}
            self.TaskData["Data"]["type"] = self.Tasks.Jobs[ID].type
            self.TaskData["Data"]["progress"] = self.Tasks.Jobs[ID].progress
            self.TaskData["Data"]["metadata"] = self.Tasks.Jobs[ID].metadata
            self.output.append(self.TaskData)

        return json.dumps(self.output)
    def m_receive_all(self, sock):
        self.data = ""
        self.part = None
        while self.part != "":
            self.part = sock.recv(4096).decode('utf8')
            self.data += self.part
            if self.part == "":
                break
        return self.data

    def m_create_data(self, command, payload=0):
        self.data = {}
        self.data["command"] = command
        self.data["payload"] = payload
        return json.dumps(self.data)

    def m_send(self, payload):
        # SOCK_STREAM == a TCP socket
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        #sock.setblocking(0)  # optional non-blocking
        self.sock.connect((self.ip, int(self.port)))
        logging.debug("sending data => %s", (payload))
        try:
            self.sock.send(bytes(payload, 'utf8'))
        except:
            print("")


        #sock.setblocking(0)
        self.ready = select.select([self.sock],[],[],2)
        if self.ready[0]:

            self.reply = self.m_receive_all(self.sock)
            if len(self.reply)>0:
                return self.reply
        else:
            print("request timed out")

        if self.sock != None:
            self.sock.close()
        #return reply




