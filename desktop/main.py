import customtkinter as ctk
import requests
import json
import os

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("dark-blue")

class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        
        self.password_rows = []
        self.api_url = "http://localhost:8000"  # API endpoint
        self.DATABASE_FILE = "desktop/local_mock_database.json"
       

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

        self.add_pass_btn = ctk.CTkButton(top_toolbar, height=30, width=40, fg_color="#45136b", text="ADD PASSWORD") #command=self.open_pass_add
        self.add_pass_btn.pack(side="right", padx=(0,5))

        self.sync_btn = ctk.CTkButton(top_toolbar, height=30, width=20, fg_color="#ff0073", text="SYNC", command=self.sync)
        self.sync_btn.pack(side="right", padx=10)
        
        main_content = ctk.CTkFrame(master=self, fg_color="#212b38", corner_radius=0)
        main_content.grid(row=1, column=0, sticky="nsew")

        self.scrollable = ctk.CTkScrollableFrame(main_content, label_text="Passwords")
        self.scrollable.pack(fill="both", expand=True, padx=10, pady=10)

        self.load_passwords()
        self.search_bar.bind("<KeyRelease>", lambda e: self.on_search())

    def read_local_DB(self):
        if os.path.exists(self.DATABASE_FILE):
            try:
                with open(self.DATABASE_FILE, "r") as f:
                    data = json.load(f)
                    return data.get("passwords", [])
            except Exception as e:
                print(f"Error reading database: {e}")
                return []
        return []

    def load_passwords(self, passwords=None):
        for row in self.password_rows:
            row.destroy()
        self.password_rows.clear()

        data = self.read_local_DB()
        if passwords is not None:
            data = passwords #zaradi filtriranja

        for p in data:
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
            pass_entry.insert(0, "••••••••")  # hidden
                # col 3: buttons
            buttons_frame = ctk.CTkFrame(row_frame, fg_color="transparent")
            buttons_frame.grid(row=0, column=3, sticky="e", padx=5)

            show_hide_button = ctk.CTkButton(
                                buttons_frame, text="Show", width=50,
                                command=lambda s=p["site"], u=p["username"], e=pass_entry: self.temp_show_password(s, u, e)
            )
            show_hide_button.pack(side="left", padx=(0,2))

            copy_button = ctk.CTkButton(
                                buttons_frame, text="Copy", width=50, 
                                command=lambda s=p["site"], u=p["username"]: self.copy_password(s, u)
            )
            copy_button.pack(side="left")
                
            self.password_rows.append(row_frame)

    """def sync(self):
        try:
            r = requests.post("http://localhost:8000/api/passwords", json=json.load(self.DATABASE_FILE))
            self.passwords = r.json()["passwords"]
            #vault_data = r.json()["encrypted_vault"]
            self.load_passwords()
            print(f"Synced! Total: {len(json.load(self.DATABASE_FILE))}")
        except:
            print("Sync failed {e}")"""
    
    def get_password_by_site_user(self, site, username):
        data = self.read_local_DB()
        for p in data:
            if p["site"] == site and p["username"] == username:
                return p["password"]
        return None

    def temp_show_password(self, site, username, pass_entry):
        password = self.get_password_by_site_user(site, username)
        if not password:
            return
        
        pass_entry.configure(state="normal", show="")
        pass_entry.delete(0, "end")
        pass_entry.insert(0, password)
        pass_entry.configure(state="readonly")
        self.after(2000, lambda e=pass_entry: self.hide_password(e))

    def hide_password(self, pass_entry):
        pass_entry.configure(state="normal")
        pass_entry.delete(0, "end")
        pass_entry.insert(0, "••••••••")
        pass_entry.configure(show="•", state="readonly")

    def copy_password(self, site, username):
        password = self.get_password_by_site_user(site, username)
        if not password:
            return
        
        old_clipboard = self.clipboard_get() if self.clipboard_get() else ""

        self.clipboard_clear()
        self.clipboard_append(password)

        self.after(30000, lambda: self.clear_clipboard_if_unchanged(password, old_clipboard))

    def clear_clipboard_if_unchanged(self, expected_password, restore_content):
        current = self.clipboard_get()
        if current == expected_password:
            self.clipboard_clear()
            self.clipboard_append(restore_content)

    def filter_pass(self, query):
        query = query.strip().lower()
        if not query:
            return self.read_local_DB()
        data = self.read_local_DB()
        return [p for p in data if query in p["site"].lower() or query in p["username"].lower()]
    
    def on_search(self):
        query = self.search_bar.get()
        filtered_passwords = self.filter_pass(query)
        self.load_passwords(filtered_passwords)
                          

if __name__ == "__main__":
    tk_app = App()
    tk_app.mainloop()