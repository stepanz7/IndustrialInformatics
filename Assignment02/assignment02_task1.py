from flask import Flask, request
import paho.mqtt.publish as publish
import json
import xmltodict

server = Flask(__name__)
sequenceNumber = {}
"""For subscription"""

# simmilar comand as can be seen beneath might be used for subscribing to robots events

# r = post(f'http://192.168.6.2/rest/events/rob1/notifs',
# json={"destUrl": f"http://127.0.0.1:5000/Changed_status"})


def seq_number_store(robId):
    if robId not in sequenceNumber:
        sequenceNumber.update({f'{robId}': 0})
    sequenceNumber[f'{robId}'] += 1
    return sequenceNumber[f'{robId}']

def prep_json_message(mess):
    robID = mess['@deviceId']
    timeStamp = mess['@dateTime']
    state = mess['@currentState']
    sequenceNumber = seq_number_store(robID)

    message ={}
    message['deviceID'] = robID
    message['state'] = state
    message['time'] = timeStamp
    message['sequenceNumber'] = sequenceNumber

    return message


@server.route("/event", methods=['GET', 'POST'])
def parse_xml() -> str:
    content_dict = xmltodict.parse(request.data)
    mess = content_dict['Envelope']['Message']['IPC2541:EquipmentInitializationComplete']
    message = json.dumps(prep_json_message(mess))
    publish.single(f"ii22/stepan/{mess['@deviceId']}", message, hostname="broker.mqttdashboard.com")
    return f"Message recieved"

def main():
    server.run()

if __name__ == "__main__":
    main()