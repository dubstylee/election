import Tkinter as tk
import sys
import time
from enum import Enum
from shared import exit_program, mqtt_client, mqtt_topic, send_message, ON, OFF


leds = []


class Status(Enum):
    MAIN = 0      # starting state
    DECIDE = 1    # compare ids
    BOWOUT = 2    # can't be leader
    ANNOUNCE = 3  # sent leader message
    WAITING = 4   # waiting to get leader message back
    WORKING = 5   # election complete, working
    IDLE = 6      # done working


class Circle:
    off_color = "#BBB"
    status = OFF

    def __init__(self, gui, pos, x, y, r, fill, outline, width):
        self.gui = gui
        self.pos = pos
        self.x = x
        self.y = y
        self.r = r
        self.on_color = fill
        self.fill = fill
        self.outline = outline
        self.width = width

    def __str__(self):
        return "Circle <%d,%d> radius (%d)" % (self.x, self.y, self.r)

    def write(self, status):
        self.status = status
        if self.status == ON:
            self.fill = self.on_color
        elif status == OFF:
            self.fill = self.off_color
        self.gui.draw_circle(self)
        self.gui.update()


class Ledison(tk.Frame):
    id = 0
    next_id = 0
    initiator = False
    sent_id = False
    state = Status.MAIN

    def draw_circle(self, c):
        return self.draw_circle_internal(c.x, c.y, c.r, fill=c.fill,
                                         outline=c.outline, width=c.width)

    def draw_circle_internal(self, x, y, r, **kwargs):
        return self.canvas.create_oval(x - r, y - r, x + r, y + r, **kwargs)

    def __init__(self, master, id, next_id):
        tk.Frame.__init__(self, master)
        master.title("LEDison")
        self.master = master
        self.canvas = tk.Canvas(master, width=360, height=80, borderwidth=0,
                                highlightthickness=0, bg="#DDD")
        self.canvas.grid()
        self._job = None
        self.id = id
        self.next_id = next_id

    def send_id(self, id):
        time.sleep(1)
        send_message("ELECTION %d %d" % (self.next_id, id))

    def send_leader(self, id):
        time.sleep(1)
        send_message("LEADER %d %d" % (self.next_id, id))


def on_message(client, userdata, msg):
    message = msg.payload
    splits = message.split(' ')
    action = splits[3]
    if action in ["LABELA", "LABELB", "UPDATEA", "UPDATEB"]:
        return
    to_id = int(splits[4])

    # we are only interested in messages that are sent to our node id
    if to_id == gui.id:
        print(msg.payload)

        if action == "ELECTION":
            leader = int(splits[5])
            if gui.state == Status.DECIDE:
                print("trying to decide")
            elif gui.state == Status.BOWOUT:
                gui.send_id(leader)
            elif gui.state in [Status.ANNOUNCE, Status.WAITING,
                               Status.WORKING, Status.IDLE]:
                print("already had an election, cheating?")
            else:  # gui.state == Status.MAIN
                gui.state = Status.DECIDE
                if leader > gui.id:
                    for i in range(0, 8):
                        if i == 0:
                            leds[i].write(ON)
                        else:
                            leds[i].write(OFF)
                    gui.send_id(leader)
                    gui.state = Status.BOWOUT
                elif leader < gui.id:
                    gui.state = Status.MAIN
                    gui.send_id(gui.id)
                else:
                    gui.state = Status.ANNOUNCE
                    gui.send_leader(gui.id)
                    gui.state = Status.WAITING

        elif action == "LEADER":
            leader = int(splits[5])
            if gui.state in [Status.MAIN, Status.DECIDE, Status.WORKING,
                             Status.IDLE]:
                # not in a state to accept leader message, cheating?
                print("maybe cheating")
            elif gui.state == Status.BOWOUT:
                if leader > gui.id:
                    gui.send_leader(leader)
                    send_message("WORKING %d" % gui.id)
                    gui.state = Status.WORKING
                elif leader == gui.id:
                    print("received invalid leader id")
            elif gui.state in [Status.ANNOUNCE, Status.WAITING]:
                if leader == gui.id:
                    for i in range(0,8):
                        if i < 3:
                            leds[i].write(ON)
                        else:
                            leds[i].write(OFF)
                    send_message("WORKING %d" % gui.id)
                    gui.state = Status.WORKING
                else:
                    print("should not receive multiple leaders")


def main():
    global gui
    if len(sys.argv) != 3:
        print "Usage: ledison <id> <next_id>"
        exit_program()

    mqtt_client.will_set(mqtt_topic, '___Will of LEDison___', 0,
                         False)
    mqtt_client.on_message = on_message
    mqtt_client.loop_start()

    root = tk.Tk()
    gui = Ledison(root, int(sys.argv[1]), int(sys.argv[2]))
    for i in range(0, 8):
        c = Circle(gui, i, 40 + 40 * i, 40, 15, fill="#BBB", outline="white",
                   width=1)
        if i in range(0, 2):
            c.on_color = "green"
        elif i in range(2, 4):
            c.on_color = "blue"
        elif i in range(4, 6):
            c.on_color = "orange"
        else:
            c.on_color = "red"
        leds.append(c)
        c.write(OFF)

    # start election in contention
    leds[0].write(ON)
    leds[1].write(ON)
    root.mainloop()
    exit_program()


if __name__ == "__main__":
    main()
