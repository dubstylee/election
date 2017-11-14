from shared import *
from enum import Enum

class Status(Enum):
  ERROR = -1
  BEGIN = 0
  HOMEFREE = 1

# To keep a track of which node we are 
# monitoring the assert for
assertParam = 0
assertName = None
systemStatus = Status.BEGIN

def on_message(client, userdata, msg):
  global systemStatus
  global assertParam
  message = msg.payload
  print message
  split = message.split(" ")
  if "ELECTION" == split[3]:
    send_message("UPDATEA %s : %s" %(assertName,message))
    recepient = int(split[4])
    if recepient == assertParam and systemStatus == Status.BEGIN:
      systemStatus = Status.HOMEFREE
  elif "LEADER" == split[3]:
    send_message("UPDATEA %s : %s" %(assertName,message))
    recepient = int(split[4])
    print recepient
    print assertParam
    print systemStatus.name
    if recepient == assertParam and systemStatus == Status.BEGIN:
      print "Reporting error"
      systemStatus = Status.ERROR
      send_message("UPDATEA %s : ASSERTFAILED" %assertName)

def main():
  global assertParam
  global assertName
  if len(sys.argv) < 2:
    print "Invalid number of arguments, usage : python assert.py <assert parameter>"
  assertParam = int(sys.argv[1])
  mqtt_client.on_message = on_message
  mqtt_client.will_set(mqtt_topic, "Will of Asserter\n\n", 0, False)
  mqtt_client.loop_start()
  assertName = "(!send_id[%d][k:IDS] W send_leader[%d][k:IDS])" %(assertParam, assertParam);
  send_message("LABELA %s" %assertName);
  while True:
    time.sleep(1)

if __name__ == "__main__" :
  main()