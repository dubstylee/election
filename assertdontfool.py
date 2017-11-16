from shared import mqtt_client, mqtt_topic, send_message
import time


def on_message(client, userdata, msg):
    message = msg.payload

    # we are only interested in leader actions for this assert
    split = message.split(" ")
    if not split[3] == "LEADER":
        return

    send_message("UPDATEA DONT_GET_FOOLED : %s" % message)

    recipient = int(split[4])
    leader = int(split[5])
    if recipient > leader:
        send_message("UPDATEA DONT_GET_FOOLED : ASSERTFAILED")


def main():
    mqtt_client.on_message = on_message
    mqtt_client.will_set(mqtt_topic, "Will of Asserter\n\n", 0, False)
    mqtt_client.loop_start()

    description = "assert DONT_GET_FOOLED = " \
                  "forall[i:1..Max] forall[j:0..(i-1)] []!(send_leader[i][j])"
    send_message("LABELA %s" % description)

    while True:
        time.sleep(1)


if __name__ == "__main__":
    main()
