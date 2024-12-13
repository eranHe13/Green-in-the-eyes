import os
import tkinter as tk
from tkinter import messagebox
from tkinterdnd2 import TkinterDnD, DND_FILES

# Set the path to the tkdnd library
tkdnd_path = os.path.join(os.path.dirname(__file__), 'tkdnd2.8')
os.environ['TCLLIBPATH'] = tkdnd_path

class GreenEyesApp:
    def __init__(self, root):
        # Initialize the application
        self.root = root
        self.members = {}  # Dictionary to store member information (phone to name mapping)
        self.in_area = []  # List of phones in the area
        self.near_area = []  # List of phones near the area
        self.out_area = []  # List of phones out of the area
        self.active_area_phones = []  # Combined list of phones in or near the area
        self.files_loaded = {"members": False, "conenot": False}  # Track file load statuses

        # Set up the UI
        self.setup_ui()

    def setup_ui(self):
        # Configure the main window
        self.root.title("ירוק בעיניים")
        self.root.geometry("1200x600")

        # Input frames for file drop areas
        self.input_frame_1 = tk.Frame(self.root)
        self.input_frame_1.pack(pady=5, anchor="n", expand=True)

        # First file drop area
        self.label_file_1 = tk.Label(self.input_frame_1, text="Drop File Here", width=80, height=2, relief="sunken")
        self.label_file_1.pack(side=tk.LEFT)
        self.label_file_1.drop_target_register(DND_FILES)
        self.label_file_1.dnd_bind('<<Drop>>', lambda event: self.handle_drop(event, "conenot"))
        
        tk.Label(self.input_frame_1, text=":סקר כוננות ביישוב", width=20).pack(side=tk.LEFT, padx=5)

        # Second file drop area
        self.input_frame_2 = tk.Frame(self.root, bg="red")
        self.input_frame_2.pack(pady=5, anchor="n", expand=True)

        self.label_file_2 = tk.Label(self.input_frame_2, text="Drop File Here", width=80, height=2, relief="sunken")
        self.label_file_2.pack(side=tk.LEFT)
        self.label_file_2.drop_target_register(DND_FILES)
        self.label_file_2.dnd_bind('<<Drop>>', lambda event: self.handle_drop(event, "green"))
        
        tk.Label(self.input_frame_2, text=":סקר ירוק בעיניים", width=20).pack(side=tk.LEFT, padx=5)

        # Button frame
        button_frame = tk.Frame(self.root)
        button_frame.pack(pady=5)

        # Buttons for processing and loading members
        tk.Button(button_frame, text="בצע ירוק בעיניים", command=self.process_files, bg="red", fg="white").pack(side=tk.LEFT, padx=5)
        tk.Button(button_frame, text="חברי כיתת כוננות", command=self.load_internal_file).pack(side=tk.LEFT, padx=5)

        # Text widgets for display
        self.create_text_widget("בגזרה ולא ענו", "lightcoral", "missing")
        self.create_text_widget("בגזרה וענו", "lightgreen", "answered")
        self.create_text_widget("בגזרה", "lightblue", "all")

    def create_text_widget(self, label, bg_color, widget_key):
        # Helper to create labeled text widgets
        frame = tk.Frame(self.root)
        frame.pack(side=tk.LEFT, padx=5)

        label = tk.Label(frame, text=label, width=30, font=("Arial", 14))
        label.pack(pady=5)

        text_widget = tk.Text(frame, wrap=tk.WORD, height=20, width=30, bg=bg_color, fg="black")
        text_widget.pack()

        setattr(self, f"text_widget_{widget_key}", text_widget)

    def handle_drop(self, event, file_type):
        # Handle file drop events
        file_path = event.data.strip('{}')
        if file_type == "conenot":
            self.label_file_1.config(text=file_path)
            self.load_conenot_data(file_path)
        elif file_type == "green":
            self.label_file_2.config(text=file_path)
        print(f"File dropped for {file_type}: {file_path}")

    def clear_text_widgets(self):
        # Clear content of all text widgets
        for key in ["missing", "answered", "all"]:
            widget = getattr(self, f"text_widget_{key}")
            widget.delete(1.0, tk.END)

    def load_internal_file(self):
        # Load the members file and populate the "all" text widget
        self.clear_text_widgets()
        self.load_members('./names.csv')

        self.text_widget_all.delete(1.0, tk.END)
        for phone, name in self.members.items():
            self.text_widget_all.insert(tk.END, f"{phone} : {name}\n")

    def load_members(self, file_path):
        # Load members from a CSV file
        try:
            with open(file_path, 'r') as file:
                self.members = {line.strip().split(',')[1]: line.strip().split(',')[0] for line in file}
            self.files_loaded["members"] = True
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load members file: {e}")

    def load_conenot_data(self, file_path):
        # Load "conenot" data, categorizing phones into areas
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                lines = file.readlines()[2:]  # Skip header lines
                self.in_area, self.near_area, self.out_area = [], [], []

                for line in lines:
                    parts = line.strip().split(',')
                    phone = parts[1]
                    if parts[2] == 'X':
                        self.in_area.append(phone)
                    elif parts[3] == 'X':
                        self.near_area.append(phone)
                    else:
                        self.out_area.append(phone)
                
                self.active_area_phones = self.in_area + self.near_area
                self.files_loaded["conenot"] = True
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load conenot file: {e}")

    def load_green_data(self, file_path):
        # Load "green" data, extracting phones that responded
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                lines = file.readlines()[2:]  # Skip header lines
                ok = [line.split(',')[1] for line in lines if line.split(',')[2] == 'X']
                return ok
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load green file: {e}")
            return []

    def process_files(self):
        # Process data and populate text widgets
        self.clear_text_widgets()
        if not self.files_loaded["members"] or not self.files_loaded["conenot"]:
            messagebox.showwarning("Warning", "Please ensure both files are loaded.")
            return

        green_path = self.label_file_2.cget("text")
        if green_path == "Drop File Here":
            messagebox.showwarning("Warning", "Please drop the green survey file.")
            return

        ok_phones = self.load_green_data(green_path)

        missing = [phone for phone in self.active_area_phones if phone not in ok_phones]
        answered = [phone for phone in self.active_area_phones if phone in ok_phones]

        for phone in missing:
            self.text_widget_missing.insert(tk.END, f"{self.members.get(phone, 'Unknown')} : {phone}\n")

        for phone in answered:
            self.text_widget_answered.insert(tk.END, f"{self.members.get(phone, 'Unknown')} : {phone}\n")

        for phone in self.active_area_phones:
            self.text_widget_all.insert(tk.END, f"{self.members.get(phone, 'Unknown')} : {phone}\n")

if __name__ == "__main__":
    root = TkinterDnD.Tk()
    app = GreenEyesApp(root)
    root.mainloop()
