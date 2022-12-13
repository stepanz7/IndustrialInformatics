
from flask import Flask, render_template,request
import store_data
import threading
import datetime
import KPI

import paho.mqtt.client as mqtt
import json

app = Flask(__name__)

threadStarted=False


@app.route('/<string:page_name>/')
def static_page(page_name):
    nID = request.args.get('nID')
    return render_template('%s.html' % page_name, nID=nID)


@app.route('/hello', methods=['GET'])
def helloWorld():
    print("Hello world endpoint")
    return "Hello World"

@app.route('/measurement-history', methods=[ 'POST', 'GET'])
def measurementHistory():
    nID = request.args.get('nID')
    return render_template('measurement-history.html', nID=nID)

@app.route('/event-history', methods=[ 'POST', 'GET'])
def eventHistory():
    nID = request.args.get('nID')
    return render_template('event-history.html', nID=nID)

@app.route('/dashboard', methods=[ 'POST', 'GET'])
def dashboard():
    nID = request.args.get('nID')
    return render_template('dashboard.html', nID=nID)


@app.route('/start', methods=['GET'])
def startThreads():
    print("Start threads attempt")
    global threadStarted
    if (threadStarted):
        return "Threads have started already"
    else:
        threadStarted=True
        #Mqtt
        x = threading.Thread(target=startSubscription)
        x.start()

        return "Starting threads"

#Mqtt on message
def on_message(client, userdata, msg):
    print("Message received-> " + msg.topic + " " + str(msg.payload))  # Print a received msg
    topic = msg.topic.split("/")
    robot_id = topic[2]
    message = json.loads(msg.payload)
    state = message['state']
    ts = string_to_epoch(message['time'])
    # print(robot_id, state, ts)
    # conn = store_data.sqlite3.connect('robots_messages_testing.db', check_same_thread=False)
    # conn.row_factory = store_data.dict_factory
    store_data.insert_robot_message(robot_id, state, ts)

def string_to_epoch(string):
    year = int(string[0:4])
    month = int(string[5:7])
    day = int(string[8:10])
    hour = int(string[11:13])
    minute = int(string[14:16])
    second = int(string[17:19])
    millisecond = int(string[20:23])
    # epoch = int(datetime.datetime(year, month, day, hour, minute, second).strftime('%s'))
    epoch = int(datetime.datetime(year, month, day, hour, minute, second).timestamp())
    return epoch

#Mqtt thread
def startSubscription():
    print("Mqtt subscription started....")
    client = mqtt.Client()
    client.on_message = on_message
    client.connect("broker.mqttdashboard.com")
    client.subscribe("ii22/telemetry/#")#subscribe all nodes

    rc = 0
    while rc == 0:
        rc = client.loop()



#bellow here everything is for testing purposes!

@app.route("/api/latestMessage/<string:robot>")
def placeLatest(robot):
    data = KPI.get_latest_event(robot)
    data = data[0]
    data_dict = json.dumps(data)
    return data_dict


@app.route("/api/historicalData/<string:id>/<start>/<end>")
def placeHistorical(id, start, end):
    data = KPI.get_historical_data(id, start, end)
    data_dict = json.dumps(data)
    return data_dict

@app.route("/api/kpi/<string:id>/<start>/<end>")
def placeKPI(id, start, end):
    data = KPI.calculate_KPI(id, start, end)
    data_dict = json.dumps(data)
    return data_dict

@app.route("/api/exceededDownStates/<string:id>/<start>/<end>")
def placeExceededDowns(id, start, end):
    data = KPI.log_all_exceeding_DOWN_messages(id, start, end)
    data_dict = json.dumps(data)
    return data_dict

@app.route("/api/exceededIdleStates/<string:id>/<start>/<end>")
def placeExceededIdles(id, start, end):
    data = KPI.log_all_exceeding_idle_messages(id, start, end)
    data_dict = json.dumps(data)
    return data_dict

if __name__ == '__main__':
    app.run()