import Tkinter as tk
import sys
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
        send_message("ELECTION %d %d" % (self.next_id, id))

    def send_leader(self, id):
        send_message("LEADER %d %d" % (self.next_id, id))


def on_message(client, userdata, msg):
    print (msg.payload)

    splits = msg.payload.split(' ')

    # TODO: implement node message handling


def main():
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

    root.mainloop()
    exit_program()


if __name__ == "__main__":
    main()
