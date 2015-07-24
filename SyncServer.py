import threading
import socketserver
import json
import uuid
import helper as hfn
import os
import shutil
import socket
try:
    import xml.etree.cElementTree as ET
except ImportError:
    import xml.etree.ElementTree as ET



import dataclasses
import logging
import time
logging.basicConfig(level=logging.DEBUG,
                    format='(%(threadName)-10s) %(message)s',
                    )
class ThreadedTCPRequestHandler(socketserver.BaseRequestHandler,hfn.c_HelperFunctions):
    def m_add_task_to_list(self,ID,Payload):
        #adds a Task from a client into the global list.
        #Task only gets the data on progress, ID and metadata
        Tasks.Jobs[ID] = Payload
    def m_send_tasklist(self):
        #sends the whole task list to client
        self.request.sendall(bytes(json.dumps(self.Output),'utf-8'))
    def m_setpriority(self,prioritylist):
        #reorders the task list from incoming priority list array and then sets a flag to show that the list has changed and update is needed
        #prioritylist is an array of ID's
        Tasks.Order = prioritylist
    def m_getpriority(self):
        logging.debug("Sending task priority order")
        #return the order of the tasks in the global list
        self.Output = []
        for ID in Tasks.Order:
            self.TaskData = {}
            self.TaskData["ID"] = ID
            self.Output.append(self.TaskData)

        self.request.sendall(bytes(json.dumps(self.Output),'utf-8'))

    # def setup(self):
    def handle(self):
        #print("handling request")
        self.buffersize = 1024*1024*5
        self.data = self.request.recv(self.buffersize).decode('utf-8')
        self.data = json.loads(self.data)
        self.Command = self.data["command"]
        self.Payload = self.data["payload"]
        self.Output = {}

        if self.Command == "/syncserver/v1/global/queue/task/put":
            #when a new task is put into the global task list, then it needs to notify this to all registered clients (except for the one that sent the
            #request in the first place.

            logging.debug("number of global tasks:%s", len(Tasks.Jobs))
            self.Payload = json.loads(self.Payload)
            if len(self.Payload)>0:
                for data in self.Payload:
                    if not self.m_Is_ID_In_List(Tasks.Order,data["ID"]):
                        Tasks.Order.append(data["ID"])
                        Tasks.Jobs[data["ID"]] = dataclasses.c_Task()
                        logging.debug("Adding a task to the global list from:%s", self.client_address[0])

            if len(Tasks.Jobs)>0:
                for cl in Tasks.clientlist:
                    #if cl["ip"] == self.client_address[0]:
                    self.Client = hfn.Client(cl["ip"],cl["port"],Tasks)
                    logging.debug("Sending tasks to:%s", self.client_address[0])
                    self.Client.m_send(self.Client.m_create_data("/webimporter/v1/global/queue/put", self.Client.m_SerialiseSyncTasks()))


        elif self.Command == "/syncserver/v1/global/queue/task/get":
            logging.debug("Sending tasks to client:%s", self.client_address[0])

        elif self.Command == "/syncserver/v1/global/queue/set_priority":
            logging.debug("Set priority list")
        elif self.Command == "/syncserver/v1/global/queue/get_priority":
            self.m_getpriority()
        elif self.Command == "/syncserver/v1/server/register":
            self.client = {}
            self.client["ip"] = self.client_address[0]
            self.client["port"] = int(self.Payload)
            self.bFoundClient = False
            for cl in Tasks.clientlist:
                if cl["ip"] == self.client_address[0] and cl["port"] == int(self.Payload):
                    self.bFoundClient = True

            if self.bFoundClient == False:
                logging.debug("Registering client:%s:%s", self.client_address[0],self.Payload)
                Tasks.clientlist.append(self.client)
            else:
                logging.debug("[%s:%s]Client already exists", self.client_address[0],self.Payload)

        elif self.Command == "/webimporter/syncserver/v1/server/shutdown":
            logging.debug("Shutting down server")
            #go to each line manager and ask it to shut down
            Tasks.shutdown = True
    # def finish(self):
    #     print("cleaning up request")

class ThreadedTCPServer(socketserver.ThreadingMixIn, socketserver.TCPServer):
    allow_reuse_address = True
    pass

class server(hfn.c_HelperFunctions):
    def __init__(self):
        global Tasks
        Tasks = dataclasses.c_data()
    def run(self):
        # Port 0 means to select an arbitrary unused port
        HOST, PORT = "localhost",  8908
        server = ThreadedTCPServer((HOST, PORT), ThreadedTCPRequestHandler)
        ip, port = server.server_address
        # Start a thread with the server -- that thread will then start one
        # more thread for each request
        server_thread = threading.Thread(target=server.serve_forever)
        # Exit the server thread when the main thread terminates
        server_thread.daemon = True
        server_thread.start()
        server_thread.name = "Sync_Server"
        logging.debug("Sync Server loop running in thread:%s", server_thread.name)

        while not Tasks.shutdown:
             time.sleep(1)
             continue

        server.shutdown()
        logging.debug("Sync Server is shutdown")

serverThread = server()
serverThread.run()

