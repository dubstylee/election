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
    state = Status.NONE

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
        leader = int(splits[5])

        if action == "ELECTION":
            if node.status == Status.DECIDE:
                print("trying to decide")
            elif node.status == Status.BOWOUT:
                node.send_id(leader)
            elif node.status in [Status.ANNOUNCE, Status.WAITING,
                                 Status.WORKING, Status.IDLE]:
                print("already had an election, cheating?")
            else:  # node.status == Status.MAIN
                node.status = Status.DECIDE
                if leader > node.id:
                    node.send_id(leader)
                    node.status = Status.BOWOUT
                elif leader < node.id:
                    node.status = Status.MAIN
                else:
                    node.status = Status.ANNOUNCE
                    node.send_leader(node.id)
                    node.status = Status.WAITING

        elif action == "LEADER":
            if node.status in [Status.MAIN, Status.DECIDE, Status.WORKING,
                               Status.IDLE]:
                # not in a state to accept leader message, cheating?
                print("maybe cheating")
            elif node.status == Status.BOWOUT:
                if leader > node.id:
                    send_leader(leader)
                    node.status == Status.WORKING:
                elif leader == node.id:
                    print("received invalid leader id")
            elif node.status in [Status.ANNOUNCE, Status.WAITING]:
                if leader == node.id:
                    print("i can haz ldr")
                else:
                    print("should not receive multiple leaders")


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
