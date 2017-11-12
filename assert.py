from shared import *

#Global bounds for a ring of 3
totalMsgAllowed = 12
maxProcesses = 3

#Runtime paramenters for a ring of 3
messagesLeft = 12
processesWorking = 0

#parameter for assert on messages
assertParam = None

def checkAssertStatus() :
  if processesWorking == 3:
    if messagesLeft == assertParam:
      #print "Assert Failure : messeges = %d, working=%d" %(messagesLeft, processesWorking)
      send_message("UPDATEA ASSERTFAILED");

def on_message(client, userdata, msg):
  global messagesLeft
  global processesWorking
  message = msg.payload
  split = message.split(" ")
  if "ELECTION" == split[3] or "LEADER" == split[3]:
    #print message
    messagesLeft = messagesLeft - 1
    send_message("UPDATEA %s" %message)
    #print "Messages : %d" %messagesLeft
  elif "WORKING" == split[3]:
    #print message
    processesWorking = processesWorking + 1
    send_message("UPDATEA %s" %message)
    #print "Working : %d" %processesWorking
  checkAssertStatus()

def main():
  global assertParam
  if len(sys.argv) < 2:
    print "Invalid number of arguments, usage : python assert.py <assert parameter>"
  assertParam = int(sys.argv[1])
  mqtt_client.on_message = on_message
  mqtt_client.will_set(mqtt_topic, "Will of Asserter\n\n", 0, False)
  mqtt_client.loop_start()
  send_message("LABELA []!final_count[%d]" %assertParam);
  while True:
    time.sleep(1)

if __name__ == "__main__" :
  main()
