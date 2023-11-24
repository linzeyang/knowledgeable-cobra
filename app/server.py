"""server.py"""

import os
from uuid import UUID

from dotenv import find_dotenv, load_dotenv
from fastapi import Body, FastAPI, Path
from fastapi.responses import PlainTextResponse, RedirectResponse

from app.authenticator import get_authenticator
from app.entity import UserAuth, UserPrompt
from app.prompt_processor import get_prompt_processor

# from langserve import add_routes


load_dotenv(find_dotenv())

app = FastAPI()


@app.get("/")
@app.post("/")
async def root():
    value = os.getenv("PROJECT_NAME")
    return PlainTextResponse(content=f"{value if value else 'NOT FOUND'}")


@app.post("/signup/")
async def signup(username: str):
    return PlainTextResponse("Signup is closed.")


@app.post("/auth/")
async def auth_user(userauth: UserAuth = Body(...)):
    authenticator = get_authenticator(purpose="signin")

    if not authenticator().authenticate(username=userauth.username):
        return PlainTextResponse(f"Auth failed for {userauth.username}")

    return RedirectResponse(url="/home/")


@app.post("/signout/")
async def signout():
    return RedirectResponse(url="/")


@app.post("/purge/")
async def purge_user():
    return RedirectResponse(url="/")


@app.get("/home/")
@app.post("/home/")
async def home():
    return PlainTextResponse("Welcome! This is home page.")


@app.get("/libraries/")
async def libraries():
    return []


@app.post("/libraries/")
async def create_library():
    ...
    return {}


@app.put("/libraries/{library_id}/")
@app.put("/library/{library_id}/")
async def update_library(library_id: UUID = Path(...)):
    return {"uuid": library_id}


@app.get("/libraries/{library_id}/")
@app.get("/library/{library_id}/")
async def library(library_id: UUID = Path(...)):
    return {"uuid": library_id}


@app.delete("/libraries/{library_id}/")
@app.delete("/library/{library_id}/")
async def remove_library(library_id: UUID = Path(...)):
    return {"uuid": library_id}


@app.get("/documents/")
async def documents():
    return []


@app.get("/documents/{document_id}/")
@app.get("/document/{document_id}/")
async def document(document_id: UUID = Path(...)):
    return {"uuid": document_id}


@app.post("/documents/")
async def upload_document():
    # start a background task
    return {}


@app.delete("/documents/{document_id}/")
@app.delete("/document/{document_id}/")
async def remove_document(document_id: UUID = Path(...)):
    return {"uuid": document_id}


@app.get("/dialogues/")
async def dialogues():
    return []


@app.post("/dialogues/")
async def create_dialogue():
    ...
    return {}


@app.get("/dialogues/{dialogue_id}/")
@app.get("/dialogue/{dialogue_id}/")
async def dialogue(dialogue_id: UUID = Path(...)):
    return {"uuid": dialogue_id}


@app.post("/dialogues/{dialogue_id}/prompt/")
@app.post("/dialogue/{dialogue_id}/prompt/")
async def prompt(
    dialogue_id: UUID = Path(...),
    user_prompt: UserPrompt = Body(...),
):
    response = get_prompt_processor(dialogue_id=dialogue_id)(
        prompt=user_prompt.content,
    )

    return {
        "dialogue_id": dialogue_id,
        "prompt": user_prompt.content,
        "response": response,
    }


@app.delete("/dialogues/{dialogue_id}/")
@app.delete("/dialogue/{dialogue_id}/")
async def remove_dialogue(dialogue_id: UUID = Path(...)):
    return {"uuid": dialogue_id}


# Edit this to add the chain you want to add
# add_routes(app, NotImplemented)

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
