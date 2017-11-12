from enum import Enum
from shared import mqtt_client, mqtt_topic, send_message, exit_program
import signal
import sys
import time


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
        send_message("ELECTION %d %d" % (self.next_id, id))

    def send_leader(self, id):
        send_message("LEADER %d %d" % (self.next_id, id))


node = None


def control_c_handler(signum, frame):
    exit_program()


signal.signal(signal.SIGINT, control_c_handler)


def on_message(client, userdata, msg):
    splits = msg.payload.split(' ')
    action = splits[3]
    to_id = int(splits[4])

    # we are only interested in messages that are sent to our node id
    if to_id == node.id:
        print(msg.payload)
        leader = int(splits[5])

        if action == "ELECTION":
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
                    node.send_id(leader)
                    node.state = Status.BOWOUT
                elif leader < node.id:
                    node.state = Status.MAIN
                else:
                    node.state = Status.ANNOUNCE
                    node.send_leader(node.id)
                    node.state = Status.WAITING

        elif action == "LEADER":
            if node.state in [Status.MAIN, Status.DECIDE, Status.WORKING,
                               Status.IDLE]:
                # not in a state to accept leader message, cheating?
                print("maybe cheating")
            elif node.state == Status.BOWOUT:
                if leader > node.id:
                    node.send_leader(leader)
                    node.state = Status.WORKING
                elif leader == node.id:
                    print("received invalid leader id")
            elif node.state in [Status.ANNOUNCE, Status.WAITING]:
                if leader == node.id:
                    print("%d sez 'i can haz ldr'" % node.id)
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
    node_timeout = 5

    if node.id % 2 == 0:
        node.initiator = True

    while True:
        if (node.initiator or node_timeout == 0) and node.state == Status.MAIN:
            node.send_id(node.id)

        time.sleep(1)
        node_timeout = node_timeout - 1


if __name__ == "__main__":
    main()
