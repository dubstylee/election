from enum import Enum
from shared import mqtt_client, mqtt_topic, send_message, exit_program
import signal
import sys
import time


class Status(Enum):
    NONE = 0     # starting state
    DECIDE = 0   # compare ids
    BOWOUT = 0   # can't be leader
    ANNOUNCE = 0 # sent leader message
    WAITING = 0  # waiting to get leader message back
    WORKING = 0  # election complete, working
    IDLE = 0     # done working


class Node():
    id = 0
    next_id = 0
    prev_id = 0
    initiator = False
    sent_id = False
    state = Status.NONE

    def __init__(self, id, next_id):
        self.id = id
        self.next_id = next_id

    def send_id(self, id):
        send_message("ELECTION %d %d %d" % (self.id, self.next_id, id))

    def send_leader(self, id):
        send_message("LEADER %d %d %d" % (self.id, self.next_id, id))


node = None


def control_c_handler(signum, frame):
    exit_program()


signal.signal(signal.SIGINT, control_c_handler)


def on_message(client, userdata, msg):
    splits = msg.payload.split(' ')
    if splits[3] == "ELECTION":
        if node.status in [Status.WORKING, Status.IDLE]:
            print("already had an election, cheating?")
        elif node.status == Status.BOWOUT:
            print("bowout")
            # if id is less than node.id, drop message
        elif node.status in [Status.NONE, Status.DECIDE, Status.ANNOUNCE, Status.WAITING]:
            print("do stuff here")

        from_id = int(splits[4])
        to_id = int(splits[5])
        leader = int(splits[6])

        if node.prev_id == -1:
            node.prev_id = from_id
        elif node.prev_id != from_id:
            send_message("CAUGHT CHEATER %d" % from_id)
        else:
            if leader > node.id:
                node.send_id(leader)
                node.status = Status.BOWOUT
            elif leader < node.id:
                send_message("dropping message")
            else:
                node.send_leader(node.id)
                node.status = Status.ANNOUNCE
                node.status = Status.WAITING
    elif splits[3] == "LEADER":
        if node.status in [Status.NONE, Status.DECIDE, Status.WORKING, Status.IDLE]:
            # not in a state to accept leader message, cheating?
            print("maybe cheating")
        elif node.status == Status.BOWOUT:
            print("id should be > node.id")
        elif node.status == Status.ANNOUNCE:
            print("might combine ANNOUNCE and WAITING")
        elif node.status == Status.WAITING:
            print("id should be == node.id")


def main():
    if len(sys.argv) != 3:
        print "Usage: node <id> <next_id>"
        exit_program()

    node = Node(sys.argv[1], sys.argv[2])
    mqtt_client.will_set(mqtt_topic, "__WILL OF NODE %d__" % node.id, 0, False)
    mqtt_client.on_message = on_message
    mqtt_client.loop_start()

    while True:
        time.sleep(1)


if __name__ == "__main__":
    main()
