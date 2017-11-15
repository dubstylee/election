from shared import *
from enum import Enum

class AssertStatus(Enum):
  ERROR = -1
  BEGIN = 0
  HOMEFREE = 1

class FluentStatus(Enum):
  ON = 1
  OFF = 0

# To keep a track of which node we are 
# monitoring the assert for
assertParam = 0
assertName = None
systemStatus = AssertStatus.BEGIN

class Fluent():
  status = FluentStatus.OFF
  identifier = 0;
  def __init__ (seld, param):
    self.identifier = param

  def checkFluent(self, message):
    split = message.split(" ")
    if split[3] == "ELECTION" :
      recepient = int(split[5])
      if recepient == self.identifier:
        self.status = FluentStatus.ON
    elif split[3] == "LEADER" :
      sender = int(split[4])
      elected = int(split[5])
      if sender == identfier || elected == identifier
        self.status = FluentStatus.OFF

fluent = None

def on_message(client, userdata, msg):
  global systemStatus
  global assertParam
  global fluent
  message = msg.payload
  # Check the status of the fluent here after receiving the
  # messages
  fluent.checkFluent(message)
  if(fluent.status == FluentStatus.ON) :
    systemStatus = AssertStatus.HOMEFREE
  
  if systemStatus == AssertStatus.HOMEFREE :
    send_message("UPDATEA %s : %s" %(assertName,message))

  elif systemStatus != AssertStatus.HOMEFREE :
    send_message("UPDATEA %s : %s" %(assertName,message))
    split = message.split(" ")
    if "LEADER" == split[3]:
     recepient = int(split[4])
     if recepient == assertParam and systemStatus == AssertStatus.BEGIN:
        print "Reporting error"
        systemStatus = AssertStatus.ERROR
        send_message("UPDATEA %s : ASSERTFAILED" %assertName)

def main():
  global assertParam
  global assertName
  global fluent
  if len(sys.argv) < 2:
    print "Invalid number of arguments, usage : python assert.py <assert parameter>"
  assertParam = int(sys.argv[1])
  fluent = Fluent(assertParam)
  mqtt_client.on_message = on_message
  mqtt_client.will_set(mqtt_topic, "Will of Asserter\n\n", 0, False)
  mqtt_client.loop_start()
  assertName = "(!send_leader[%d][k:IDS] W send_id[%d][k:IDS])" %(assertParam, assertParam);
  send_message("LABELA %s" %assertName);
  while True:
    time.sleep(1)

if __name__ == "__main__" :
  main()
