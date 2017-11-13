from shared import *
from enum import Enum

class Status(Enum):
  ERROR = -1
  BEGIN = 0
  HOMEFREE = 1

# To keep a track of which node we are 
# monitoring the assert for
assertParam = 0
systemStatus = Status.BEGIN

def on_message(client, userdata, msg):
  global systemStatus
  global assertParam
  message = msg.payload
  split = message.split(" ")
  if "ELECTION" == split[3]:
    send_message("UPDATEA %s" %message)
    recepient = int(split[4])
    if recepient == assertParam and systemStatus == Status.BEGIN:
      systemStatus = Status.HOMEFREE
  elif "LEADER" == split[3]:
    send_message("UPDATEA %s" %message)
    recepient = int(split[4])
    if recepient == assertParam and systemStatus == Status.BEGIN:
      systemStatus = Status.ERROR
      send_message("UPDATEA ASSERTFAILED");
      exit_program()

def main():
  global assertParam
  if len(sys.argv) < 2:
    print "Invalid number of arguments, usage : python assert.py <assert parameter>"
  assertParam = int(sys.argv[1])
  mqtt_client.on_message = on_message
  mqtt_client.will_set(mqtt_topic, "Will of Asserter\n\n", 0, False)
  mqtt_client.loop_start()
  #send_message("LABELA (!send_id[%d][k:IDS] W send_leader[%d][k:IDS])" %(assertParam, assertParam));
  while True:
    time.sleep(1)

if __name__ == "__main__" :
  main()
