from fastapi import FastAPI, Request, HTTPException, Form
from fastapi.responses import RedirectResponse, JSONResponse, HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware  # <-- CORS middleware import
import requests
import os
from dotenv import load_dotenv

app = FastAPI() 

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # allows all origins; replace with list of domains in prod
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

load_dotenv()

templates = Jinja2Templates(directory="templates")

GITHUB_CLIENT_ID = os.getenv("GITHUB_CLIENT_ID")
GITHUB_CLIENT_SECRET = os.getenv("GITHUB_CLIENT_SECRET")

@app.get("/")
def read_root(request: Request):
    return templates.TemplateResponse("Index.html", {"request": request})

@app.get("/login")
def github_login():
    github_auth_url = (
        f"https://github.com/login/oauth/authorize?"
        f"client_id={GITHUB_CLIENT_ID}&scope=repo"
    )
    return RedirectResponse(github_auth_url)

@app.get("/callback")
def github_callback(request: Request):
    code = request.query_params.get("code")
    if not code:
        raise HTTPException(status_code=400, detail="Missing 'code' query parameter")

    token_url = "https://github.com/login/oauth/access_token"
    headers = {"Accept": "application/json"}
    payload = {
        "client_id": GITHUB_CLIENT_ID,
        "client_secret": GITHUB_CLIENT_SECRET,
        "code": code
    }
    response = requests.post(token_url, headers=headers, data=payload)
    token_response = response.json()
    access_token = token_response.get("access_token")

    if not access_token:
        return JSONResponse({"error": "Failed to get token", "details": token_response}, status_code=400)

    user_repos_url = "https://api.github.com/user/repos"
    headers.update({"Authorization": f"token {access_token}"})
    repos_response = requests.get(user_repos_url, headers=headers)
    repos = repos_response.json()

    return templates.TemplateResponse("repos.html", {"request": request, "repos": repos, "token": access_token})

@app.post("/delete_repos")
async def delete_repos(
    request: Request,
    repo_names: list[str] = Form(None),
    access_token: str = Form(...)
):
    if not repo_names:
        return HTMLResponse(content="<h2>No repositories selected.</h2>", status_code=400)

    headers = {"Authorization": f"token {access_token}"}
    failed = []
    for repo_full_name in repo_names:
        delete_url = f"https://api.github.com/repos/{repo_full_name}"
        resp = requests.delete(delete_url, headers=headers)
        if resp.status_code not in (204, 202):
            failed.append(repo_full_name)
    if failed:
        return HTMLResponse(
            content=f"<h2>Failed to delete: {', '.join(failed)}</h2>",
            status_code=400
        )
    return HTMLResponse(content="<h2>Selected repositories deleted successfully.</h2>")
