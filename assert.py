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
      print "Assert Failure : messeges = %d, working=%d" %(messagesLeft, processesWorking)
    else:
      print "Assert Success : messeges = %d, working=%d" %(messagesLeft, processesWorking)

def on_message(client, userdata, msg):
  global messagesLeft
  global processesWorking
  message = msg.payload
  split = message.split(" ")
  if "ELECTION" == split[3] or "LEADER" == split[3]:
    print message
    messagesLeft = messagesLeft - 1
    print "Messages : %d" %messagesLeft
  elif "WORKING" == split[3]:
    print message
    processesWorking = processesWorking + 1
    print "Working : %d" %processesWorking
  checkAssertStatus()

def main():
  global assertParam
  if len(sys.argv) < 2:
    print "Invalid number of arguments, usage : python assert.py <assert parameter>"
  assertParam = int(sys.argv[1])
  mqtt_client.on_message = on_message
  mqtt_client.will_set(mqtt_topic, "Will of Asserter\n\n", 0, False)
  mqtt_client.loop_start()
  while True:
    time.sleep(1)

if __name__ == "__main__" :
  main()
