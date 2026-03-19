from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Dict
import json
import os

app = FastAPI(title="Zero-Knowledge Sync API")

class VaultPayload(BaseModel):
    user_id: str
    encrypted_vault: str

DATABASE_FILE = "mock_database.json"

@app.get("/")
def root():
    return {"status": "online", "message": "Zero-Knowledge Sync Server is running"}

#POST endpoint for saving the vault
@app.post("/sync")
def upload_vault(payload: VaultPayload):
    data = {}
    #1. Reaading an existing file if it exists
    try:
        with open(DATABASE_FILE, "r") as f:
            data = json.load(f)
    except json.JSONDecodeError:
            data = {}

    #2. Updating or adding a new user
    data[payload.user_id] = payload.encrypted_vault

    #3. Writing refreshed data back into the file
    with open(DATABASE_FILE, "w") as f:
        json.dump(data, f)

    return {"status": "success", "message": "Vault synced successfully"}

#GET endpoint for downloading the vault
@app.get("/sync/{user_id}")
def download_vault(user_id: str):
    if not os.path.exists(DATABASE_FILE):
        raise HTTPException(status_code=404, detail="Database file doesnt exists")

    with open(DATABASE_FILE, "r") as f:
        data = json.load(f)

        if user_id not in data:
            raise HTTPException(status=404, detail="User vault not found")
        
        return {"user_id": user_id, "encrypted_vault": data[user_id]}
    
"""@app.get("/api/passwords")
def get_passwords():
    if os.path.exists(DATABASE_FILE):
        try:
            with open(DATABASE_FILE, "r") as f:
                data = json.load(f)
                return data.get("passwords", [])
        except json.JSONDecodeError:
            pass
    return []"""

@app.post("/api/passwords")
def merge_passwords(client_passwords: List[dict]):
    server_passwords=[]
    if os.path.exists(DATABASE_FILE):
        try:
            with open(DATABASE_FILE, "r") as f:
                data = json.load(f)
                server_passwords = data.get("passwords", [])
        except Exception as e:
            print(f"Error reading database: {e}")
            server_passwords=[]
    
    existing_sites = set()
    for p in server_passwords:
        if "site" in p:
            existing_sites.add(p["site"])
    
    #unija gesel
    all_passwords = server_passwords.copy()
    for client_p in client_passwords:
        if client_p.get("site") not in existing_sites:
            if "id" in client_p:
                del client_p["id"]
            all_passwords.append(client_p)
            existing_sites.add(client_p.get("site"))
    
    data = {"passwords": all_passwords}
    with open(DATABASE_FILE, "w") as f:
        json.dump(data, f)

    return {"status": "merged", "total": len(all_passwords), "passwords": all_passwords}
