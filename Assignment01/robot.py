"""
This is class Robot for assignment01 - Industrial informatics - Tampere 2022
"""

import requests, time
drawingFinished = True
PEN_HAS_SAME_COLLOR = True
WSNUM = "9" #INSERT Work Station Number
EMPTY = "-1"

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
                result1 = requests.post(f"http://192.168.{WSNUM}.1/rest/services/Draw{frame}", json={"destUrl": ""})
                self.orchestrator.notificateFailure(result1)
                self.recipe += 1
            case 2:
                print("drawing screen")
                time.sleep(3)
                screen = self.orchestrator.currentOrder['screen']
                print(screen, type(screen))
                ds = requests.post(f"http://192.168.{WSNUM}.1/rest/services/Draw{screen}", json={"destUrl": ""})
                self.orchestrator.notificateFailure(ds)
                #print(ds)
                self.recipe += 1
            case 3:
                print("drawing keypad")
                time.sleep(3)
                keypad = self.orchestrator.currentOrder['keypad']
                result3 = requests.post(f"http://192.168.{WSNUM}.1/rest/services/Draw{keypad}", json={"destUrl": ""})
                self.orchestrator.notificateFailure(result3)
                self.recipe += 1


    def set_mobileFinished(self,state):
        self.mobileFinished=state

    def changePen(self, color):
        #resultCP=requests.post(f"http://192.168.{WSNUM}.1/rest/services/ChangePen{color}")
        #self.orchestrator.notificateFailure(resultCP)
        return "RED"

    def getPen(self):
        #color = requests.post(f"http://192.168.{WSNUM}.1/rest/services/GetPenColor", json={})
        #self.orchestrator.notificateFailure(color)
        #return color
        return "RED"

    def calibrate(self):
        print("calibrate")
        resultc=requests.post(f"http://192.168.{WSNUM}.1/rest/services/Calibrate", json={})
        self.orchestrator.notificateFailure(resultc)