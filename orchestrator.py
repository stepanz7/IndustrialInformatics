"""
This is class Orchestrator for assignment01 - Industrial informatics - Tampere 2022
"""
import requests, conveyor, robot
from flask import Flask, request
drawingFinished = True
PEN_HAS_SAME_COLLOR = True
WSNUM = "9" #INSERT Work Station Number
EMPTY = "-1"
server = "http://192.168.0.90"


class Orchestrator:
    def __init__(self):
        self.orders = []
        self.nextOrder = None
        self.currentOrder = None
        self.ordersFinished = []
        self.ordersDiscarded = []
        self.conveyor = conveyor.Conveyor(self)
        self.robot = robot.Robot(self)
        self.conveyor.orchestrator = self
        self.robot.orchestrator = self
        self.subscriber()
        self.calibrate()
        print("Initialising Flask")
        self.flask()



    def discardOrder(self):
        discarded = self.orders.pop(0)
        self.ordersDiscarded.append(discarded)

    def assignOrder(self):
        self.nextOrder = self.orders.pop(0)


    def notificateFailure(self, status):
        if status.status_code != 202 or status.status_code != 200:
            print("Error: " + str(status.status_code))
        else:
            print("Request Successful")

    def robotDraw(self):
        self.robot.drawMobile()

    def changePen(self, color):
        self.robot.changePen(color)

    def getMobileStatus(self):
        return self.robot.mobileFinished

    def getRobotStatus(self):
        return self.robot.robotWorking

    def setMobileStatus(self, state):
        self.robot.set_mobileFinished(state)

    def getPenColor(self):
        return self.robot.getPen()

    def calibrate(self):
        self.robot.calibrate()

    def printHistory(self):
        print("Thank you for using our system")
        print("Here is a summary of all requests and completed orders")
        if len(self.ordersFinished) == 0:
            print("No completed orders")
        else:
            print("Completed Orders:")
            for order in self.ordersFinished:
                print('\tReference Number: ', order["Ref"])
                print('\t\tFrame Recipe: ', order["frame"])
                print('\t\tScreen Recipe: ', order["screen"])
                print('\t\tKeypad Recipe: ', order["keypad"])
                print('\t\tColor: ', order["color"])

        if len(self.ordersDiscarded) == 0:
            print("No discarded orders")
        else:
            print("Discarded Orders:")
            for order in self.ordersDiscarded:
                print('\tReference Number: ', order["Ref"])
                print('\t\tFrame Recipe: ', order["frame"])
                print('\t\tScreen Recipe: ', order["screen"])
                print('\t\tKeypad Recipe: ', order["keypad"])
                print('\t\tColor: ',order["color"])
        

    def subscriber(self):
        print("Deleting all previous requests from the controller")
        z1delete = requests.delete(f"http://192.168.{WSNUM}.2/rest/events/Z1_Changed/notifs",
                                   json={"destUrl": f"{server}:5000/events"})
        z2delete = requests.delete(f"http://192.168.{WSNUM}.2/rest/events/Z2_Changed/notifs",
                                   json={"destUrl": f"{server}:5000/events"})
        z3delete = requests.delete(f"http://192.168.{WSNUM}.2/rest/events/Z3_Changed/notifs",
                                   json={"destUrl": f"{server}:5000/events"})
        z4delete = requests.delete(f"http://192.168.{WSNUM}.2/rest/events/Z4_Changed/notifs",
                                   json={"destUrl": f"{server}:5000/events"})
        z5delete = requests.delete(f"http://192.168.{WSNUM}.2/rest/events/Z5_Changed/notifs",
                                   json={"destUrl": f"{server}:5000/events"})
        PCSdelete = requests.delete(f"http://192.168.{WSNUM}.1/rest/events/PenChangeStarted/notifs",
                                    json={"destUrl": f"{server}:5000/events"})
        PCEdelete = requests.delete(f"http://192.168.{WSNUM}.1/rest/events/PenChangeEnded/notifs",
                                    json={"destUrl": f"{server}:5000/events"})
        DSEdelete = requests.delete(f"http://192.168.{WSNUM}.1/rest/events/DrawStartExecution/notifs",
                                    json={"destUrl": f"{server}:5000/events"})
        DESdelete = requests.delete(f"http://192.168.{WSNUM}.1/rest/events/DrawEndExecution/notifs",
                                    json={"destUrl": f"{server}:5000/events"})
        print("Delete status:", z1delete, z2delete, z3delete, z4delete, z5delete, PCSdelete, PCEdelete, DSEdelete, DESdelete)

        print("Subscribing for all notifications")
        resultZ1 = requests.post(f"http://192.168.{WSNUM}.2/rest/events/Z1_Changed/notifs",
                                 json={"destUrl": f"{server}:5000/events"})
        resultZ2 = requests.post(f"http://192.168.{WSNUM}.2/rest/events/Z2_Changed/notifs",
                                 json={"destUrl": f"{server}:5000/events"})
        resultZ3 = requests.post(f"http://192.168.{WSNUM}.2/rest/events/Z3_Changed/notifs",
                                 json={"destUrl": f"{server}:5000/events"})
        resultZ4 = requests.post(f"http://192.168.{WSNUM}.2/rest/events/Z4_Changed/notifs",
                                 json={"destUrl": f"{server}:5000/events"})
        resultZ5 = requests.post(f"http://192.168.{WSNUM}.2/rest/events/Z5_Changed/notifs",
                                 json={"destUrl": f"{server}:5000/events"})
        resultPCS = requests.post(f"http://192.168.{WSNUM}.1/rest/events/PenChangeStarted/notifs",
                                  json={"destUrl": f"{server}:5000/events"})
        resultPCE = requests.post(f"http://192.168.{WSNUM}.1/rest/events/PenChangeEnded/notifs",
                                  json={"destUrl": f"{server}:5000/events"})
        resultDSE = requests.post(f"http://192.168.{WSNUM}.1/rest/events/DrawStartExecution/notifs",
                                  json={"destUrl": f"{server}:5000/events"})
        resultDES = requests.post(f"http://192.168.{WSNUM}.1/rest/events/DrawEndExecution/notifs",
                                  json={"destUrl": f"{server}:5000/events"})
        print("Subscribe status:", resultZ1, resultZ2, resultZ3, resultZ4, resultZ5, resultPCS, resultPCE, resultDSE, resultDES)

    def eventHandler(self, event):
        eventID = event['id']
        if eventID == "Z1_Changed":
            print("Starting Z1_handler")
            self.conveyor.z1_handler()
        elif eventID == "Z2_Changed":
            print("Starting Z2_handler")
            self.conveyor.z2_handler()
        elif eventID == "Z3_Changed":
            print("Starting Z3_handler")
            self.conveyor.z3_handler()
        elif eventID == "Z4_Changed":
            print("Starting Z4_handler")
            self.conveyor.z4_handler()
        elif eventID == "Z5_Changed":
            print("Starting Z5_handler")
            self.conveyor.z5_handler()
        elif eventID == "DrawStartExecution":
            print("Starting DrawStartExecution")
            self.robot.robotWorking=True
            print("--------------------------------------------------------------------------------------------")
            print(f"Starting to draw and calling z4_handler. robotWorking = { self.robot.robotWorking},mobileFinished = {self.robot.mobileFinished}")
            self.conveyor.z4_handler()
            print("--------------------------------------------------------------------------------------------")
        elif eventID == "DrawEndExecution":
            print("Starting DrawEndExecution")
            # self.robot.mobileFinished = True #just for testing, might be deleted later
            # self.robot.robotWorking = False #just for testing, will be deleted later
            if self.robot.recipe == 4:
                self.robot.mobileFinished = True
                self.robot.recipe = 1
                self.robot.robotWorking = False
                self.ordersFinished.append(self.currentOrder)
            self.conveyor.z3_handler()
        elif eventID == "PenChangeStarted":
            print("Changing pen.")
        elif eventID == "PenChangeEnded":
            self.conveyor.z2_handler()
        elif eventID == "Order":
            self.orders.append(event)
            self.conveyor.z1_handler()
        elif eventID == "EndSystem":
            self.printHistory()
            print("\nSystem Paused\n")
        else:
            print("Those events are not handled yet")

    def flask(self):
        @app.route('/events', methods=['POST'])
        def subscription():
            event = request.json
            self.eventHandler(event)
            return "hello"

app = Flask(__name__)
def main():
    orchestrator = Orchestrator()
    app.run("192.168.0.90", debug=True)
    # app.run(server)
if __name__ == '__main__':
    main()


