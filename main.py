from fastapi import FastAPI, Request
from fastapi.responses import RedirectResponse, JSONResponse
import requests
import os
from dotenv import load_dotenv

load_dotenv()

app = FastAPI()

GITHUB_CLIENT_ID = os.getenv("GITHUB_CLIENT_ID")
GITHUB_CLIENT_SECRET = os.getenv("GITHUB_CLIENT_SECRET")

@app.get("/")
def read_root():
    return {"message": "Welcome to Unforker!"}

@app.get("/login")
def github_login():
    github_auth_url = f"https://github.com/login/oauth/authorize?client_id={GITHUB_CLIENT_ID}&scope=repo"
    return RedirectResponse(github_auth_url)

@app.get("/callback")
def github_callback(code: str):
    token_url = "https://github.com/login/oauth/access_token"
    headers = {"Accept": "application/json"}
    payload = {
        "client_id": GITHUB_CLIENT_ID,
        "client_secret": GITHUB_CLIENT_SECRET,
        "code": code
    }
    response = requests.post(token_url, headers=headers, data=payload)
    access_token = response.json().get("access_token")
    
    if not access_token:
        return JSONResponse({"error": "Failed to get token"}, status_code=400)
    
    # Test API call: get user's repos
    user_repos_url = "https://api.github.com/user/repos"
    headers.update({"Authorization": f"token {access_token}"})
    repos_response = requests.get(user_repos_url, headers=headers)

    return repos_response.json()

