import threading
import socketserver
import json
import uuid
import helper as hfn
import os
import shutil
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
    def setup(self):
    def handle(self):
        #print("handling request")
        self.buffersize = 1024*1024*5
        self.data = self.request.recv(self.buffersize).decode('utf-8')
        self.data = json.loads(self.data)
        self.Command = self.data["command"]
        self.Payload = self.data["payload"]
        self.Output = {}
        if self.Command == "/webimporter/syncserver/v1/global/queue/task/put":
            self.ID = str(uuid.uuid4())
            logging.debug("Adding a task to the global list")
        elif self.Command == "/webimporter/syncserver/v1/global/queue/task/get":
            logging.debug("Getting all tasks")
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
        HOST, PORT = "localhost",  '8908'
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

server()

