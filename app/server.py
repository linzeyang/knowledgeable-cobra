"""server.py"""

import os
from uuid import UUID

from dotenv import find_dotenv, load_dotenv
from fastapi import Body, FastAPI, Path, status
from fastapi.responses import PlainTextResponse, RedirectResponse

from app.authenticator import get_authenticator
from app.controller import (
    create_dialogue,
    create_document,
    create_library,
    emb_document,
    get_dialogue,
    get_dialogues,
    get_document,
    get_documents,
    get_libraries,
    get_library,
    update_dialogue,
)
from app.data_connection.mongo import get_client
from app.entity import (
    Dialogue,
    DialogueList,
    Document,
    DocumentList,
    Library,
    LibraryList,
    UserAuth,
    UserPrompt,
)

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


@app.get("/library/", response_model=LibraryList)
async def libraries():
    return await get_libraries(user_id=DUMMY_USER_ID)


@app.post("/library/", response_model=Library, status_code=status.HTTP_201_CREATED)
async def insert_library(instance: Library):
    return await create_library(instance=instance)


@app.get("/library/{library_id}/", response_model=Library)
async def library(library_id: UUID = Path(...)):
    return await get_library(user_id=DUMMY_USER_ID, library_id=library_id)


@app.put("/library/{library_id}/")
async def update_library(library_id: UUID = Path(...)):
    return {"uuid": library_id}


@app.delete("/library/{library_id}/")
async def remove_library(library_id: UUID = Path(...)):
    return {"uuid": library_id}


@app.get("/library/{library_id}/document/", response_model=DocumentList)
async def documents(library_id: UUID = Path(...)):
    return await get_documents(user_id=DUMMY_USER_ID, library_id=library_id)


@app.post("/document/", response_model=Document, status_code=status.HTTP_201_CREATED)
async def upload_document(instance: Document):
    # start a background task?

    return await create_document(user_id=DUMMY_USER_ID, instance=instance)


@app.get("/document/{document_id}/", response_model=Document)
async def document(document_id: UUID = Path(...)):
    return await get_document(user_id=DUMMY_USER_ID, document_id=document_id)


@app.post("/document/{document_id}/embed/")
async def embed_document(document_id: UUID = Path(...)):
    resp = await emb_document(user_id=DUMMY_USER_ID, document_id=document_id)

    return {"result": resp}


@app.delete("/document/{document_id}/")
async def remove_document(document_id: UUID = Path(...)):
    return {"uuid": document_id}


@app.get("/library/{library_id}/dialogue/", response_model=DialogueList)
async def dialogues(library_id: UUID = Path(...)):
    return await get_dialogues(user_id=DUMMY_USER_ID, library_id=library_id)


@app.post("/dialogue/", response_model=Dialogue, status_code=status.HTTP_201_CREATED)
async def insert_dialogue(instance: Dialogue):
    return await create_dialogue(user_id=DUMMY_USER_ID, instance=instance)


@app.get("/dialogue/{dialogue_id}/", response_model=Dialogue)
async def dialogue(dialogue_id: UUID = Path(...)):
    return await get_dialogue(user_id=DUMMY_USER_ID, dialogue_id=dialogue_id)


@app.post("/dialogue/{dialogue_id}/")
async def prompt(
    dialogue_id: UUID = Path(...),
    user_prompt: UserPrompt = Body(...),
):
    resp = await update_dialogue(
        user_id=DUMMY_USER_ID, dialogue_id=dialogue_id, user_prompt=user_prompt
    )

    return {
        "dialogue_id": dialogue_id,
        "prompt": user_prompt.content,
        "response": resp,
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
