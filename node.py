from enum import Enum
from shared import mqtt_client, mqtt_topic, send_message, exit_program, ON, OFF
import signal
import sys
import time

EDISON = False

if EDISON:
    import mraa


class Status(Enum):
    MAIN = 0      # starting state
    DECIDE = 1    # compare ids
    BOWOUT = 2    # can't be leader
    ANNOUNCE = 3  # sent leader message
    WAITING = 4   # waiting to get leader message back
    WORKING = 5   # election complete, working
    IDLE = 6      # done working


class Node():
    id = 0
    next_id = 0
    # prev_id = 0
    initiator = False
    sent_id = False
    state = Status.MAIN

    def __init__(self, id, next_id):
        self.id = id
        self.next_id = next_id

    def send_id(self, id):
        time.sleep(0.5)
        send_message("ELECTION %d %d" % (self.next_id, id))

    def send_leader(self, id):
        time.sleep(0.5)
        send_message("LEADER %d %d" % (self.next_id, id))


node = None

if EDISON:
    # set up leds
    leds = []
    for i in range(2, 10):
        led = mraa.Gpio(i)
        led.dir(mraa.DIR_OUT)
        led.write(OFF)
        leds.append(led)


def control_c_handler(signum, frame):
    if EDISON:
        for i in range(0, 8):
            leds[i].write(OFF)
    exit_program()


signal.signal(signal.SIGINT, control_c_handler)


def on_message(client, userdata, msg):
    message = msg.payload
    splits = message.split(' ')
    action = splits[3]
    if action in ["LABELA", "LABELB", "UPDATEA", "UPDATEB"]:
        return
    to_id = int(splits[4])

    # we are only interested in messages that are sent to our node id
    if to_id == node.id:
        print(msg.payload)

        if action == "ELECTION":
            leader = int(splits[5])
            if node.state == Status.DECIDE:
                print("trying to decide")
            elif node.state == Status.BOWOUT:
                node.send_id(leader)
            elif node.state in [Status.ANNOUNCE, Status.WAITING,
                                Status.WORKING, Status.IDLE]:
                print("already had an election, cheating?")
            else:  # node.state == Status.MAIN
                node.state = Status.DECIDE
                if leader > node.id:
                    if EDISON:
                        for i in range(0, 8):
                            if i == 0:
                                leds[i].write(ON)
                            else:
                                leds[i].write(OFF)
                    node.send_id(leader)
                    node.state = Status.BOWOUT
                elif leader < node.id:
                    node.state = Status.MAIN
                    node.send_id(node.id)
                else:
                    node.state = Status.ANNOUNCE
                    node.send_leader(node.id)
                    node.state = Status.WAITING

        elif action == "LEADER":
            leader = int(splits[5])
            if node.state in [Status.MAIN, Status.DECIDE, Status.WORKING,
                              Status.IDLE]:
                # not in a state to accept leader message, cheating?
                print("maybe cheating")
            elif node.state == Status.BOWOUT:
                if leader > node.id:
                    node.send_leader(leader)
                    send_message("WORKING %d" % node.id)
                    node.state = Status.WORKING
                elif leader == node.id:
                    print("received invalid leader id")
            elif node.state in [Status.ANNOUNCE, Status.WAITING]:
                if leader == node.id:
                    if EDISON:
                        for i in range(0, 8):
                            if i < 3:
                                leds[i].write(ON)
                            else:
                                leds[i].write(OFF)
                    send_message("WORKING %d" % node.id)
                    node.state = Status.WORKING
                else:
                    print("should not receive multiple leaders")


def main():
    global node
    if len(sys.argv) != 3:
        print "Usage: node <id> <next_id>"
        exit_program()

    node = Node(int(sys.argv[1]), int(sys.argv[2]))
    mqtt_client.will_set(mqtt_topic, "__WILL OF NODE %d__" % node.id, 0, False)
    mqtt_client.on_message = on_message
    mqtt_client.loop_start()

    if node.id == 0:
        node.initiator = True

    # start election in contention
    if EDISON:
        leds[0].write(ON)
        leds[1].write(ON)

    if node.initiator and node.state == Status.MAIN:
        time.sleep(1)
        node.send_id(node.id)

    while True:
        time.sleep(0.5)


if __name__ == "__main__":
    main()
