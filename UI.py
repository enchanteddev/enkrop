import customtkinter
import random
import faucet

class FakeStrings:
    def __init__(self, adj: list[str] | None = None, noun: list[str] | None = None) -> None:
        if adj is None:
            adj = ["Blue", "Red", "Shiny", "Pink", "Green", "Purple", "Orange", "Shy", "Angry"]
        if noun is None:
            noun = ["Chimp", "Cupboard", "Keyboard", "Bucket", "Fox", "Bulldog", "Carpet", "Giraffe"]
        
        self.adj = adj
        self.noun = noun
    
    def fakename(self) -> str:
        return random.choice(self.adj) + random.choice(self.noun)


class Nearby(customtkinter.CTkScrollableFrame):
    def __init__(self, master, people: dict[str, str]):
        super().__init__(master)
        self.people = people
        self.parent = master

        self.people_buttons = []
        self.draw(self.people)

    def draw(self, people: dict[str, str]):
        for i, p in enumerate(self.people_buttons):
            p.pack_forget()
            self.people_buttons.pop(i)
        for person in people:
            person_button = customtkinter.CTkButton(self, text=person, fg_color="#515151", hover_color='#616161', command=lambda : self.parent.send_file(people[person]))
            person_button.pack(side = "top", fill = "x", expand = True, padx = 10, pady = 5)
            self.people_buttons.append(person_button)

class App(customtkinter.CTk):
    def __init__(self):
        super().__init__()

        self.file = None
        self.client = None
        self.server = None
        self.sending = False
        self.recieving = False
        self.progress = 0
        self.nearby_text = customtkinter.StringVar()
        self.nearby_text.set("Select file and Set Password to see nearby people")
        self.username = customtkinter.StringVar()
        self.password = customtkinter.StringVar()
        self.password.trace_add("write", lambda a,b,c: self.turn_on_nearby())
        self.username.set(FakeStrings().fakename())

        self.title("my app")
        self.geometry("500x500")
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(4, weight=1)

        self.credentials_frame = customtkinter.CTkFrame(self)
        self.username_label = customtkinter.CTkLabel(self.credentials_frame, text="Username")
        self.password_label = customtkinter.CTkLabel(self.credentials_frame, text="Password")
        self.username_box = customtkinter.CTkEntry(self.credentials_frame, textvariable=self.username)
        self.password_box = customtkinter.CTkEntry(self.credentials_frame, textvariable=self.password)
        self.username_label.pack(side = "left")
        self.username_box.pack(side="left", fill="x", expand = True, padx = (7, 10), pady = 7)
        self.password_label.pack(side = "left")
        self.password_box.pack(side="right", fill="x", expand = True, padx = (10, 7), pady = 7)
        self.credentials_frame.grid(row=1,column=0, sticky="new")

        self.sr_frame = customtkinter.CTkFrame(self)
        self.send_button = customtkinter.CTkButton(self.sr_frame, text="Select File", command=self.select_file)
        self.recieve_button = customtkinter.CTkButton(self.sr_frame, text="Recieve", command=self.recieve)
        self.send_button.pack(side="left", fill="x", expand = True, padx = (7, 10), pady = 7)
        self.recieve_button.pack(side="right", fill="x", expand = True, padx = (10, 7), pady = 7)
        self.sr_frame.grid(row=2, column = 0, sticky = "new")

        self.label1 = customtkinter.CTkLabel(self, textvariable = self.nearby_text)
        self.label1.grid(row=3, sticky="w", padx = 7)

        self.nearby_people = Nearby(self, {})
        self.nearby_people.grid(row = 4, sticky = "nsew")
