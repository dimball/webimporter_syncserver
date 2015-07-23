class c_data():
    def __init__(self):
        self.Jobs = {}
        self.Order = []
        self.WorkData = {}
        self.shutdown = False
        self.clientlist = []

class c_Task():
    def __init__(self):
        self.type = "global"
        self.progress = 0
        self.metadata = {}

