"""
This is class Conveyor for assignment01 - Industrial informatics - Tampere 2022
"""

import requests, time
import json
drawingFinished = True
PEN_HAS_SAME_COLLOR = True
WSNUM = "9" #INSERT Work Station Number
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
        resulttf = requests.post(f"http://192.168.{WSNUM}.2/rest/services/TransZone{start}{end}", json=data)
        self.orchestrator.notificateFailure(resulttf)

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
                print(f"Transferring pallet from 1 to 2")
            elif not zone2state == EMPTY and zone4state == EMPTY:
                self.orchestrator.discardOrder()
                self.transfer_pallet(1, 4)
                print(f"Transferring pallet from 1 to 4")
        else:
            print("Waiting for orders...")
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