import store_data
import datetime
def total_time(robID, start, end):
    database = store_data.get_all_messages_by_robotID_and_time(robID, start, end)
    total_time = database[-1]["timeStamp"] - database[0]["timeStamp"]
    return total_time

def states_total_time(robID, start, end):
    database = store_data.get_all_messages_by_robotID_and_time(robID, start, end)
    processing = 0
    idle = 0
    down = 0
    for i in range(len(database)-1):
        if database[i]["state"] == "READY-PROCESSING-EXECUTING":
            processing += database[i+1]["timeStamp"] - database[i]["timeStamp"]
        elif database[i]["state"] == "READY-IDLE-STARVED":
            idle += database[i+1]["timeStamp"] - database[i]["timeStamp"]
        elif database[i]["state"] == "DOWN":
            down += database[i+1]["timeStamp"] - database[i]["timeStamp"]
    return processing, idle, down

def calculate_KPI(robID, start, end):
    totalTime = total_time(robID, start, end)
    processing, idle, down = states_total_time(robID, start, end)

    percentageWorking = '{:.2f}'.format(processing/totalTime*100)
    percentageIdle = '{:.2f}'.format(idle/totalTime*100)
    percentageDown = '{:.2f}'.format(down/totalTime*100)
    dictData = {"percWork": percentageWorking, "percIdle": percentageIdle, "percDown": percentageDown}
    # print(dictData)
    return dictData

def calculate_mean_failure(robID, start, end):
    database = store_data.get_all_messages_by_robotID_and_time(robID, start, end)


    #store all "DOWN" messages in database
    downMessages = [msg for msg in database if msg["state"] == "DOWN"]
    # print(downMessages)

    #For each i in downMessages find how long i lasts and add this to key endTime in i
    for i in downMessages:
        index = database.index(i)
        try:
            i["endTime"] = database[index+1]["timeStamp"]
        except IndexError:
            pass

    time_without_failures = 0
    gaps_between_failures = 0  #

    for i in range(len(downMessages)-1):
        time_without_failures += downMessages[i+1]["timeStamp"] - downMessages[i]["endTime"]
        gaps_between_failures += 1
    mean_time = round(time_without_failures/gaps_between_failures)
    data_dict = {"meanTimeToFailure": mean_time}
    # print(data_dict)
    return data_dict

def log_all_exceeding_idle_messages(robID, start, end, limit=20):
    database = store_data.get_all_messages_by_robotID_and_time(robID, start, end)
    #go through database and for each idle state do:
    for i in range(len(database)-1):
        try:
            while database[i]["state"] == "READY-IDLE-STARVED":
                try:
                    if database[i-1]["state"] == "READY-IDLE-STARVED":
                        database.remove(database[i])
                    else:
                        break
                except IndexError:
                    pass
        except IndexError:
            pass


    for i in range(len(database)-1):
        if database[i]["state"] == "READY-IDLE-STARVED":
            endTime = database[i+1]["timeStamp"]
            duration = endTime - database[i]["timeStamp"]
            database[i]["endTime"] = endTime
            database[i]["duration"] = duration
    try:
        database.remove(database[-1])
        all_idle_states = [msg for msg in database if msg["state"] == "READY-IDLE-STARVED"]
        exceeded_idle_states = [msg for msg in all_idle_states if msg["duration"] > limit]

        for data in exceeded_idle_states:
            timeStamp = datetime.datetime.fromtimestamp(data["timeStamp"]+7200)
            endTime = datetime.datetime.fromtimestamp(data["endTime"]+7200)
            data["timeStamp"] = str(timeStamp)
            data["endTime"] = str(endTime)
        print(exceeded_idle_states)
        return exceeded_idle_states
    except:
        pass

def log_all_exceeding_DOWN_messages(robID, start, end, limit=300):
    database = store_data.get_all_messages_by_robotID_and_time(robID, start, end)
    #go through database and for each idle state do:
    for i in range(len(database)-1):
        try:
            while database[i]["state"] == "DOWN":
                try:
                    if database[i-1]["state"] == "DOWN":
                        database.remove(database[i])
                    else:
                        break
                except IndexError:
                    pass
        except IndexError:
            pass



    for i in range(len(database)-1):
        if database[i]["state"] == "DOWN":
            endTime = database[i+1]["timeStamp"]
            duration = endTime - database[i]["timeStamp"]
            database[i]["endTime"] = endTime
            database[i]["duration"] = duration

    try:
        database.remove(database[-1])
        all_down_states = [msg for msg in database if msg["state"] == "DOWN"]
        exceeded_down_states = [msg for msg in all_down_states if msg["duration"] > limit]

        for data in exceeded_down_states:
            timeStamp = datetime.datetime.fromtimestamp(data["timeStamp"]+7200)
            endTime = datetime.datetime.fromtimestamp(data["endTime"]+7200)
            data["timeStamp"] = str(timeStamp)
            data["endTime"] = str(endTime)
        print(exceeded_down_states)
        for i in exceeded_down_states:
            print(i["duration"])
        return exceeded_down_states
    except:
        pass

def get_historical_data(id, start, end):
    data = store_data.get_all_messages_by_robotID_and_time(id, start, end)
    for i in data:
        timeStamp = datetime.datetime.fromtimestamp(i["timeStamp"]+7200)
        i["timeStamp"] = str(timeStamp)
    # print(data)
    return data

def get_latest_event(robID):
    data = store_data.get_latest_message_by_robotID(robID)
    for i in data:
        timeStamp = datetime.datetime.fromtimestamp(i["timeStamp"]+7200)
        i["timeDate"] = str(timeStamp)
    print(data)
    return data

# calculate_KPI("rob1", 1669476872, 1669811095)
# calculate_mean_failure("rob1", 1669476872, 1669811095)
#
# calculate_KPI("rob2", 1669476872, 1669811095)
# calculate_mean_failure("rob2", 1669476872, 1669811095)
# log_all_exceeding_idle_messages("rob2",1669474799,1670086800,15)
# log_all_exceeding_DOWN_messages("rob1", 1669476871, 1669557114)
# get_historical_data("rob1", 1669467600, 1669471200 )
# get_latest_event("rob1")
# print(store_data.get_all_messages())
# print(store_data.get_latest_message_by_robotID("rob1"))
# rob2/1669474800/1669482000
# http://127.0.0.1:5000/api/exceededIdleStates/rob2/1669474800/1670086800