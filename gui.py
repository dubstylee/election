import Tkinter as tk
from shared import mqtt_client, mqtt_topic, exit_program

class Gui(tk.Frame):
    part_a_label = None
    part_a_text = None
    part_b_label = None
    part_b_text = None
    part_a_label_text = None
    property_state = "valid"
    assert_state = "valid"    

    def __init__(self, master, assert_frame, property_frame):
        tk.Frame.__init__(self, master)
        master.title("Something Cool")
        self.master = master
        self.assert_frame = assert_frame
        self.property_frame = property_frame

    def part_a(self):
        # part A Abhishek assert
        self.part_a_label = tk.Label(self.assert_frame, text="")
        self.part_a_label.pack()
        self.part_a_text = tk.Listbox(self.assert_frame, width=200)
        self.part_a_text.pack()
        self.assert_label = tk.Label(self.assert_frame)
        self.assert_label.config(text="Assert Successful",
                                 bg="green", width=200)
        self.assert_label.pack()

    def part_b(self):
        # part B Brian property
        self.part_b_label = tk.Label(self.property_frame,
                                     text="")
        self.part_b_label.pack()
        self.part_b_text = tk.Listbox(self.property_frame, width=200)
        self.part_b_text.pack()
        self.property_status = tk.Label(self.property_frame, width=200,
                                        text="Safety Property Valid",
                                        bg="green")
        self.property_status.pack()

    def update_label_a(self, text):
        self.part_a_label_text = self.part_a_label_text + "\n" + text
        self.part_a_label.config(text=self.part_a_label_text)

    def update_part_a(self, text):
        self.part_a_text.insert(tk.END, text)
        self.part_a_text.yview(tk.END)

        if "ASSERTFAILED" in text:
            self.assert_state = "invalid"
            self.assert_label.config(text="Assert Failed", bg="red", width=200)

    def update_label_b(self, text):
        self.part_b_label.config(text=text)

    def update_part_b(self, text):
        self.part_b_text.insert(tk.END, text)
        self.part_b_text.yview(tk.END)

        if "VIOLATION OF PROPERTY" in text:
            self.property_state = "invalid"
            self.property_status.config(text="Property Violation", bg="red")

gui = None

def on_message(client, userdata, msg):
    message = msg.payload
    splits = message.split(' ', 4)
    if splits[3] == "LABELA":
        gui.update_label_a(splits[4]) 
    elif splits[3] == "UPDATEA" and gui.assert_state == "valid":
        gui.update_part_a(splits[4])
    elif splits[3] == "LABELB":
        gui.update_label_b(splits[4])
    elif splits[3] == "UPDATEB" and gui.property_state == "valid":
        gui.update_part_b(splits[4])

# placeholder for GUI
def main():
    global gui
    root = tk.Tk()
    top_frame = tk.Frame()
    top_frame.pack()
    bottom_frame = tk.Frame(highlightthickness=2,
                            highlightbackground="black",
                            highlightcolor="black")
    bottom_frame.pack(side=tk.BOTTOM)
    gui = Gui(root, top_frame, bottom_frame)

    mqtt_client.will_set(mqtt_topic, '___Will of GUI___', 0, False)
    mqtt_client.on_message = on_message
    mqtt_client.loop_start()

    gui.part_a()
    gui.part_b()

    root.mainloop()
    exit_program()

if __name__ == "__main__":
    main()
