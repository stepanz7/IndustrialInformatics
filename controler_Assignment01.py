import requests, time
import json
from flask import Flask, request
drawingFinished = True
PEN_HAS_SAME_COLLOR = True
WSNUM = "10" #INSERT Work Station Number
EMPTY = "-1"

class Conveyor:
    def __init__(self, orchestrator):
        self.orchestrator = orchestrator

    def get_zone_state(self, zoneNumber):
        data = {}
        # Store response in variable
        zoneState = requests.post(f"http://192.168.{WSNUM}.2/rest/services/Z{zoneNumber}", json=data)
        # convert variable to dict using json library
        zoneState = json.loads(zoneState.content)
        return zoneState['PalletID']

    def transfer_pallet(self, start, end):
        data = {}
        start = str(start)
        end = str(end)
        requests.post(f"http://192.168.{WSNUM}.2/rest/services/TransZone{start}{end}", json=data)

    def z1_handler(self):
        """
        This function handles everything around zone 1
        """
        zone1state = self.get_zone_state(1)
        zone2state = self.get_zone_state(2)
        zone4state = self.get_zone_state(4)

        print("--------------------------------------------------------------------------------------------")
        print(f"Z1_Handler: zone1state: {zone1state}, zone2state: {zone2state}, zone4state: {zone4state} ")
        if not zone1state == EMPTY and not len(self.orchestrator.orders) == 0:
            if zone2state == EMPTY:  # if zone2 is empty transfer to zone 2:
                self.orchestrator.assignOrder()
                self.transfer_pallet(1, 2)
                print(f"Transfering pallet from 1 to 2")
            elif not zone2state == EMPTY and zone4state == EMPTY:
                self.orchestrator.discardOrder()
                self.transfer_pallet(1, 4)
                print(f"Transfering pallet from 1 to 4")
        else:
            print("Nothing to do")
        print("--------------------------------------------------------------------------------------------")

    def z2_handler(self):
        """
        This function handles everything around zone 2
        """
        zone1state = self.get_zone_state(1)
        zone2state = self.get_zone_state(2)
        zone3state = self.get_zone_state(3)
        print("--------------------------------------------------------------------------------------------")
        print(f"Z2_Handler: zone1state: {zone1state}, zone2state: {zone2state}, zone3state: {zone3state} ")

        if zone2state == EMPTY and not zone1state == EMPTY:
            print("Starting z1_handler:")
            self.z1_handler()
        elif not zone2state == EMPTY and zone3state == EMPTY:
            print("Transfering pallet 2->3")
            self.transfer_pallet(2, 3)
            self.orchestrator.currentOrder = self.orchestrator.nextOrder
        print("--------------------------------------------------------------------------------------------")

    def z3_handler(self):
        """
        This function handles everything around zone 2
        """
        zone3state = self.get_zone_state(3)
        zone5state = self.get_zone_state(5)
        print("--------------------------------------------------------------------------------------------")
        print(f"Z3_Handler: zone3state: {zone3state}, zone5state: {zone5state}, mobileStatus: {self.orchestrator.getMobileStatus()}")
        if zone3state == EMPTY:
            print("Starting z2_handler")
            self.z2_handler()
        elif zone5state == EMPTY and self.orchestrator.getMobileStatus() and not zone3state == EMPTY:
            print("--------------------------------DrawingFinished-----------------------------------------------------")
            print(f"Drawing finished. Zone 5 state: {zone5state}. robotWorking = {self.orchestrator.getRobotStatus()},mobileFinished = {self.orchestrator.getMobileStatus()}")
            self.transfer_pallet(3, 5)
            self.orchestrator.setMobileStatus(False)
            print("--------------------------------------------------------------------------------------------")
        elif not self.orchestrator.getMobileStatus():
            print("starting draw operation")
            self.orchestrator.robotDraw()
        print("--------------------------------------------------------------------------------------------")

    def z4_handler(self):
        """
        This function handles everything around zone 2
        """
        zone5state = self.get_zone_state(5)
        zone4state = self.get_zone_state(4)
        zone1state = self.get_zone_state(1)
        print("--------------------------------------------------------------------------------------------")
        print(f"Z4_Handler: zone1state: {zone1state}, zone4state: {zone4state}, zone5state: {zone5state} ")
        if zone4state == EMPTY:
            print("Starting z1_handler")
            self.z1_handler()
        else:
            print(f"robotWorking = {self.orchestrator.getRobotStatus()}, zone5state = {zone5state}")
            if self.orchestrator.getRobotStatus() and zone5state == EMPTY:
                print("Transfering pallet 4 -> 5")
                self.transfer_pallet(4, 5)
        print("--------------------------------------------------------------------------------------------")

    def z5_handler(self):
        """
        This function handles everything around zone 2
        """

        zone5state = self.get_zone_state(5)
        zone4state = self.get_zone_state(4)
        zone3state = self.get_zone_state(3)

        print("--------------------------------------------------------------------------------------------")
        print(f"Z5_Handler: zone5state: {zone5state}, zone4state: {zone4state}, zone3state: {zone3state} , robot status: {self.orchestrator.getRobotStatus()} ")
        if zone5state == EMPTY:
            if self.orchestrator.getRobotStatus() and not zone4state == EMPTY:
                print("Transfering 4 -> 5")
                self.transfer_pallet(4, 5)
            elif not self.orchestrator.getRobotStatus() and not zone3state == EMPTY:
                print("transfering 3->5")
                self.z3_handler()
        print("--------------------------------------------------------------------------------------------")


class Robot:
    def __init__(self, orchestrator):
        self.robotWorking = bool
        self.mobileFinished = False
        self.orchestrator = orchestrator
        self.penColor = None
        self.recipe = 1

    def drawMobile(self):
        match self.recipe:
            case 1:
                print("drawing frame")
                frame = self.orchestrator.currentOrder['frame']
                requests.post(f"http://192.168.{WSNUM}.1/rest/services/Draw{frame}", json={"destUrl": ""})
                self.recipe += 1
            case 2:
                print("drawing screen")
                time.sleep(3)
                screen = self.orchestrator.currentOrder['screen']
                print(screen, type(screen))
                ds = requests.post(f"http://192.168.{WSNUM}.1/rest/services/Draw{screen}", json={"destUrl": ""})
                print(ds)
                self.recipe += 1
            case 3:
                print("drawing keypad")
                time.sleep(3)
                keypad = self.orchestrator.currentOrder['keypad']
                requests.post(f"http://192.168.{WSNUM}.1/rest/services/Draw{keypad}", json={"destUrl": ""})
                self.recipe += 1


    def set_mobileFinished(self,state):
        self.mobileFinished=state

    def changePen(self, color):
        #requests.post(f"http://192.168.{WSNUM}.1/rest/services/ChangePen{color}")
        return "RED"

    def getPen(self):
        #color = requests.post(f"http://192.168.{WSNUM}.1/rest/services/GetPenColor", json={})
        #return color
        return "RED"

    def calibrate(self):
        print("calibrate")
        requests.post(f"http://192.168.{WSNUM}.1/rest/services/Calibrate", json={})

class Orchestrator:
    def __init__(self):
        self.orders = []
        self.nextOrder = None
        self.currentOrder = None
        self.ordersFinished = []
        self.ordersDiscarded = []
        self.conveyor = Conveyor(self)
        self.robot = Robot(self)
        self.conveyor.orchestrator = self
        self.robot.orchestrator = self
        self.calibrate()
        self.flask()



    def discardOrder(self):
        discarded = self.orders.pop(0)
        self.ordersDiscarded.append(discarded)

    def assignOrder(self):
        self.nextOrder = self.orders.pop(0)


    def notificateFailure(self):
        pass
        #weshould implement this

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
            # self.robot.mobileFinished = True #just for testing, mmight be deleted later
            # self.robot.robotWorking = False #just for testing, will be deleted later
            if self.robot.recipe == 4:
                self.robot.mobileFinished = True
                self.robot.recipe = 1
                self.robot.robotWorking = False

            self.conveyor.z3_handler()
        elif eventID == "PenChangeStarted":
            print("Changing pen.")
        elif eventID == "PenChangeEnded":
            self.conveyor.z2_handler()
        elif eventID == "Order":
            self.orders.append(event)
            self.conveyor.z1_handler()
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
if __name__ == '__main__':
    main()



