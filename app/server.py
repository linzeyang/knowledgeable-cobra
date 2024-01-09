"""server.py"""

from typing import Annotated
from uuid import UUID

from fastapi import Body, FastAPI, Form, Path, Request, UploadFile, status
from fastapi.responses import PlainTextResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from jinja2_fragments.fastapi import Jinja2Blocks

from app.authenticator import DUMMY_USER_DB, get_authenticator
from app.config import Settings
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

DUMMY_USER_ID = DUMMY_USER_DB["joe.bloggs"]

settings = Settings()
templates = Jinja2Blocks(directory=settings.TEMPLATE_DIR)


app = FastAPI(**settings.fastapi_kwargs)
app.mount("/static", StaticFiles(directory=settings.STATIC_DIR), name="static")


@app.get("/")
async def root(request: Request):
    libraries = await get_libraries(user_id=DUMMY_USER_ID)

    return templates.TemplateResponse(
        "main.html",
        {
            "request": request,
            "libraries": libraries,
        },
    )


@app.get("/about/")
async def about(request: Request):
    """About page - some background information about this app."""

    return templates.TemplateResponse("about.html", {"request": request})


@app.get("/library/{library_id}/")
async def library_page(request: Request, library_id: UUID = Path(...)):
    library = await get_library(user_id=DUMMY_USER_ID, library_id=library_id)

    documents = await get_documents(user_id=DUMMY_USER_ID, library_id=library_id)

    dialogues = await get_dialogues(user_id=DUMMY_USER_ID, library_id=library_id)

    return templates.TemplateResponse(
        "library.html",
        {
            "request": request,
            "library": library,
            "documents": documents,
            "dialogues": dialogues,
        },
    )


@app.get("/dialogue/{dialogue_id}/")
@app.post("/dialogue/{dialogue_id}/")
async def dialogue_page(request: Request, dialogue_id: UUID = Path(...)):
    dialogue = await get_dialogue(user_id=DUMMY_USER_ID, dialogue_id=dialogue_id)

    return templates.TemplateResponse(
        "dialogue.html",
        {
            "request": request,
            "dialogue": dialogue,
        },
    )


@app.post("/dialogue/")
async def dialogue_create(request: Request, library_id: Annotated[UUID, Form()]):
    instance = Dialogue(
        user_id=DUMMY_USER_ID,
        library_id=library_id,
        llm="dashscope",
    )

    dialogue = await create_dialogue(user_id=DUMMY_USER_ID, instance=instance)

    return RedirectResponse(url=f"/dialogue/{dialogue.uuid}/")


@app.put("/dialogue/{dialogue_id}/")
async def dialogue_update(
    request: Request,
    user_prompt: Annotated[str, Form()],
    dialogue_id: UUID = Path(...),
):
    prompt = UserPrompt(content=user_prompt)

    message = await update_dialogue(
        user_id=DUMMY_USER_ID, dialogue_id=dialogue_id, user_prompt=prompt
    )

    return templates.TemplateResponse(
        "message.html",
        {
            "request": request,
            "message": message,
        },
    )


@app.post("/api/signup/")
async def signup(username: str):
    return PlainTextResponse("Signup is closed.")


@app.post("/api/auth/")
async def auth_user(userauth: UserAuth = Body(...)):
    authenticator = get_authenticator(purpose="signin")

    if not authenticator().authenticate(username=userauth.username):
        return PlainTextResponse(f"Auth failed for {userauth.username}")

    return RedirectResponse(url="/home/")


@app.post("/api/signout/")
async def signout():
    return RedirectResponse(url="/")


@app.post("/api/purge/")
async def purge_user():
    return RedirectResponse(url="/")


@app.get("/home/")
@app.post("/home/")
async def home():
    return PlainTextResponse("Welcome! This is home page.")


@app.get("/api/library/", response_model=LibraryList)
async def libraries():
    return await get_libraries(user_id=DUMMY_USER_ID)


@app.post("/api/library/", response_model=Library, status_code=status.HTTP_201_CREATED)
async def insert_library(instance: Library):
    return await create_library(instance=instance)


@app.get("/api/library/{library_id}/", response_model=Library)
async def library(library_id: UUID = Path(...)):
    return await get_library(user_id=DUMMY_USER_ID, library_id=library_id)


@app.put("/api/library/{library_id}/")
async def update_library(library_id: UUID = Path(...)):
    return {"uuid": library_id}


@app.delete("/api/library/{library_id}/")
async def remove_library(library_id: UUID = Path(...)):
    return {"uuid": library_id}


@app.get("/api/library/{library_id}/document/", response_model=DocumentList)
async def documents(library_id: UUID = Path(...)):
    return await get_documents(user_id=DUMMY_USER_ID, library_id=library_id)


@app.post(
    "/api/document/", response_model=Document, status_code=status.HTTP_201_CREATED
)
async def accept_document(instance: Document):
    return await create_document(user_id=DUMMY_USER_ID, instance=instance)


@app.post(
    "/api/document/upload/",
    response_model=Document,
    status_code=status.HTTP_201_CREATED,
)
async def upload_document(file: UploadFile):
    return await create_document(user_id=DUMMY_USER_ID, instance=file)


@app.get("/api/document/{document_id}/", response_model=Document)
async def document(document_id: UUID = Path(...)):
    return await get_document(user_id=DUMMY_USER_ID, document_id=document_id)


@app.post("/api/document/{document_id}/embed/")
async def embed_document(document_id: UUID = Path(...)):
    resp = await emb_document(user_id=DUMMY_USER_ID, document_id=document_id)

    return {"result": resp}


@app.delete("/api/document/{document_id}/")
async def remove_document(document_id: UUID = Path(...)):
    return {"uuid": document_id}


@app.get("/api/library/{library_id}/dialogue/", response_model=DialogueList)
async def dialogues(library_id: UUID = Path(...)):
    return await get_dialogues(user_id=DUMMY_USER_ID, library_id=library_id)


@app.post(
    "/api/dialogue/", response_model=Dialogue, status_code=status.HTTP_201_CREATED
)
async def insert_dialogue(instance: Dialogue):
    return await create_dialogue(user_id=DUMMY_USER_ID, instance=instance)


@app.get("/api/dialogue/{dialogue_id}/", response_model=Dialogue)
async def dialogue_get(dialogue_id: UUID = Path(...)):
    return await get_dialogue(user_id=DUMMY_USER_ID, dialogue_id=dialogue_id)


@app.post("/api/dialogue/{dialogue_id}/")
async def prompt_send(
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


@app.delete("/api/dialogue/{dialogue_id}/")
async def remove_dialogue(dialogue_id: UUID = Path(...)):
    return {"uuid": dialogue_id}


# @app.post("/mongo/db/{db_name}")
# async def create_mongo_db(db_name: str = Path(...)):
#     client = get_client()

#     resp = await client.


# Edit this to add the chain you want to add
# add_routes(app, NotImplemented)

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8080)
