from shared import mqtt_client, mqtt_topic, send_message, exit_program
import time
import sys
import signal


class Node():
    id = 0
    next_id = 0
    prev_id = 0
    initiator = False

    def __init__(self, id, next_id):
        self.id = id
        self.next_id = next_id

    def send_id(self, id):
        send_message("ELECTION %d" % id)

    def send_leader(self, id):
        send_message("LEADER %d" % id)


node = None


def control_c_handler(signum, frame):
    exit_program()


signal.signal(signal.SIGINT, control_c_handler)


def on_message(client, userdata, msg):
    splits = msg.payload.split(' ')
    if splits[3] == "ELECTION":
        from_id = int(splits[4])
        leader = int(splits[5])

        if node.prev_id == -1:
            node.prev_id = from_id
        elif node.prev_id != from_id:
            send_message("CAUGHT CHEATER %d" % from_id)
        else:
            if leader > node.id:
                send_message("ELECTION %d %d" % (node.id, leader))
            elif leader < node.id:
                send_message("dropping message")
            else:
                send_message("LEADER %d %d" % (node.id, node.id))


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
