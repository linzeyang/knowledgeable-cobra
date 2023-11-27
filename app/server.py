"""server.py"""

import os
from uuid import UUID

from dotenv import find_dotenv, load_dotenv
from fastapi import Body, FastAPI, Path
from fastapi.responses import PlainTextResponse, RedirectResponse

from app.authenticator import get_authenticator
from app.controller import (
    create_document,
    create_library,
    emb_document,
    get_document,
    get_documents,
    get_libraries,
)
from app.data_connection.mongo import get_client
from app.entity import Document, Library, UserAuth, UserPrompt
from app.prompt_processor import get_prompt_processor

# from langserve import add_routes


load_dotenv(find_dotenv())

app = FastAPI()


DUMMY_USER_ID = UUID("cfc0bd70-be32-4d62-85f8-cbdb65ce2ab7")


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


@app.get("/library/")
async def libraries():
    libraries = await get_libraries(user_id=DUMMY_USER_ID)

    return {"libraries": libraries}


@app.post("/library/")
async def insert_library(instance: Library):
    resp = await create_library(instance=instance)

    return {"library": resp}


@app.get("/library/{library_id}/")
async def library(library_id: UUID = Path(...)):
    return {"uuid": library_id}


@app.put("/library/{library_id}/")
async def update_library(library_id: UUID = Path(...)):
    return {"uuid": library_id}


@app.delete("/library/{library_id}/")
async def remove_library(library_id: UUID = Path(...)):
    return {"uuid": library_id}


@app.get("/library/{library_id}/document/")
async def documents(library_id: UUID = Path(...)):
    resp = await get_documents(user_id=DUMMY_USER_ID, library_id=library_id)

    return {"documents": resp}


@app.post("/document/")
async def upload_document(instance: Document):
    # start a background task?

    resp = await create_document(user_id=DUMMY_USER_ID, instance=instance)

    return {"document": resp}


@app.get("/document/{document_id}/")
async def document(document_id: UUID = Path(...)):
    resp = await get_document(user_id=DUMMY_USER_ID, document_id=document_id)

    return {"document": resp}


@app.post("/document/{document_id}/embed/")
async def embed_document(document_id: UUID = Path(...)):
    resp = await emb_document(user_id=DUMMY_USER_ID, document_id=document_id)

    return {"result": resp}


@app.delete("/document/{document_id}/")
async def remove_document(document_id: UUID = Path(...)):
    return {"uuid": document_id}


@app.get("/library/{library_id}/dialogue/")
async def dialogues(library_id: UUID = Path(...)):
    return []


@app.post("/library/{library_id}/dialogue/")
async def create_dialogue(library_id: UUID = Path(...)):
    ...
    return {}


@app.get("/dialogue/{dialogue_id}/")
async def dialogue(dialogue_id: UUID = Path(...)):
    return {"uuid": dialogue_id}


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


@app.delete("/dialogue/{dialogue_id}/")
async def remove_dialogue(dialogue_id: UUID = Path(...)):
    return {"uuid": dialogue_id}


@app.get("/mongo/db/")
async def list_mongo_dbs():
    client = get_client()

    lis = await client.list_database_names()

    return {"dbs": lis}


# @app.post("/mongo/db/{db_name}")
# async def create_mongo_db(db_name: str = Path(...)):
#     client = get_client()

#     resp = await client.


# Edit this to add the chain you want to add
# add_routes(app, NotImplemented)

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
