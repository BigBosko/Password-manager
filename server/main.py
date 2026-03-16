from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
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
    if os.path.exists(DATABASE_FILE):
        with open(DATABASE_FILE, "r") as f:
            data = json.load(f)

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
            raise HTTPException(status=404, detaul="User vault not found")
        
        return {"user_id": user_id, "encrypted_vault": data[user_id]}
