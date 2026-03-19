import customtkinter as ctk
import requests

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("dark-blue")

class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        
        self.password_rows = []
       
        # fake data
        self.passwords = [
            {"id": 1, "site": "google.com", "username": "user@gmail.com", "password": "supersecret1"},
            {"id": 2, "site": "github.com", "username": "dev@git.com", "password": "ghp_token123"},
        ]

        self.title("Manger")
        self.geometry("600x400")
        self.resizable(width=True, height=True)

        self.grid_rowconfigure(0, weight=0)  # row 0 = fixed
        self.grid_rowconfigure(1, weight=1)  # row 1 = expand
        self.grid_columnconfigure(0, weight=1)  # single column expands
        
        top_toolbar = ctk.CTkFrame(self, height=50, fg_color="#0a192b", corner_radius=0)
        top_toolbar.grid(row=0, column=0, sticky="ew")
        top_toolbar.grid_propagate(False)

        self.search_bar = ctk.CTkEntry(top_toolbar, placeholder_text="Search for passwords...")
        self.search_bar.pack(side="left", fill="x", expand=True, padx=(0,5))
        
        main_content = ctk.CTkFrame(master=self, fg_color="#212b38", corner_radius=0)
        main_content.grid(row=1, column=0, sticky="nsew")

        self.scrollable = ctk.CTkScrollableFrame(main_content, label_text="Passwords")
        self.scrollable.pack(fill="both", expand=True, padx=10, pady=10)

        self.load_passwords()
        self.search_bar.bind("<KeyRelease>", lambda e: self.on_search())


    def load_passwords(self, passwords=None):
            if passwords == None:
                passwords=self.passwords

            for row in self.password_rows:
                row.pack_forget()

            self.password_rows.clear()

            for p in passwords:
                row_frame = ctk.CTkFrame(self.scrollable)
                row_frame.pack(fill="x", pady=2, padx=5)

                row_frame.grid_columnconfigure(0, weight=2)
                row_frame.grid_columnconfigure(1, weight=2)
                row_frame.grid_columnconfigure(2, weight=1)
                row_frame.grid_columnconfigure(3, weight=0)

                # col 0: site
                site = ctk.CTkEntry(row_frame)
                site.grid(row=0, column=0, sticky="ew", padx=5)
                site.insert(0, p["site"])
                site.configure(state="readonly")

                # col 1: username
                username=ctk.CTkEntry(row_frame)
                username.insert(0, p["username"])
                username.configure(state="readonly")
                username.grid(row=0, column=1, sticky="ew", padx=5)
                # col 2: masked password
                pass_entry = ctk.CTkEntry(row_frame, show="•", width=120)
                pass_entry.grid(row=0, column=2, sticky="ew", padx=5)
                pass_entry.insert(0, p["password"])  # hidden
                # col 3: buttons
                buttons_frame = ctk.CTkFrame(row_frame, fg_color="transparent")
                buttons_frame.grid(row=0, column=3, sticky="e", padx=5)

                show_hide_button = ctk.CTkButton(buttons_frame, text="Show", width=50,
                                command=lambda pe=pass_entry: self.toggle_password_visibility(pe))
                show_hide_button.pack(side="left", padx=(0,2))

                copy_button = ctk.CTkButton(buttons_frame, text="Copy", width=50, command=lambda p=p: self.copy_pass(p))
                copy_button.pack(side="left")
                
                self.password_rows.append(row_frame)


    def copy_pass(self, p):
         self.clipboard_clear()
         self.clipboard_append(p["password"])
         print("Coppied")

    def toggle_password_visibility(self, pass_entry):
        if pass_entry.cget("show") == "":
              pass_entry.configure(show="•")
        else:
            pass_entry.configure(show="")

    def filter_pass(self, query):
        query=query.strip().lower();
        if not query:
            return self.passwords
        filtered = [p for p in self.passwords 
                   if query in p["site"].lower() or 
                   query in p["username"].lower()]
        return filtered
    
    def on_search(self):
        query = self.search_bar.get()
        filtered_passwords = self.filter_pass(query)
        self.load_passwords(filtered_passwords)
                 
                 
         

if __name__ == "__main__":
    app = App()
    app.mainloop()