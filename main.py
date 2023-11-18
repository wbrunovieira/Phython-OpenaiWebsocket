from fastapi import FastAPI, WebSocket
from typing import AsyncGenerator
import asyncio
import openai
import os
from dotenv import load_dotenv

app = FastAPI()


assistant_id = None

load_dotenv()
openai_api_key = os.getenv("OPENAI_API_KEY")
client = openai.OpenAI(api_key=openai_api_key)

async def async_openai_thread_create(client):
    return await asyncio.to_thread(client.beta.threads.create)

async def async_openai_thread_run_create(client, thread_id, assistant_id, instructions):
    return await asyncio.to_thread(client.beta.threads.runs.create, thread_id=thread_id, assistant_id=assistant_id, instructions=instructions)

async def async_openai_run_retrieve(client, thread_id, run_id):
    return await asyncio.to_thread(client.beta.threads.runs.retrieve, thread_id=thread_id, run_id=run_id)

async def async_openai_messages_list(client, thread_id):
    return await asyncio.to_thread(client.beta.threads.messages.list, thread_id=thread_id)

async def wait_on_run(run_id, thread_id, client):
    run = await async_openai_run_retrieve(client, thread_id, run_id)
    while run.status == "queued" or run.status == "in_progress":
        await asyncio.sleep(0.5)
        run = await async_openai_run_retrieve(client, thread_id, run_id)
    return run




# Funções auxiliares adaptadas para execução assíncrona
async def async_openai_thread_create(client):
    return await asyncio.to_thread(client.beta.threads.create)

async def async_openai_thread_run_create(client, thread_id, assistant_id, instructions):
    return await asyncio.to_thread(client.beta.threads.runs.create, thread_id=thread_id, assistant_id=assistant_id, instructions=instructions)

async def async_openai_run_retrieve(client, thread_id, run_id):
    return await asyncio.to_thread(client.beta.threads.runs.retrieve, thread_id=thread_id, run_id=run_id)

async def get_ai_response(message: str) -> AsyncGenerator[str, None]:
    await add_message_to_thread(thread_id, message, client)
    
    run = await client.beta.threads.runs.create(
        thread_id=thread_id,
        assistant_id=assistant_id
    )
    
    responses = await get_run_responses(run.id, thread_id, client)
    yield responses

async def add_message_to_thread(thread_id: str, message: str, client):
    await client.beta.threads.messages.create(
        thread_id=thread_id,
        role="user",
        content=message
    )
    
async def get_run_responses(run_id: str, thread_id: str, client) -> str:
    # Aguarda a conclusão do run
    run = await wait_on_run(run_id, thread_id, client)

    # Verifica se o run foi concluído com sucesso
    if run.status == 'completed':
        messages = await async_openai_messages_list(client, thread_id)
        return "\n".join([f"{message.role.title()}: {message.content[0].text.value}" for message in messages.data])
    else:
        return "Run não foi concluído com sucesso."

    
async def async_openai_messages_list(client, thread_id):
    return await asyncio.to_thread(client.beta.threads.messages.list, thread_id=thread_id)

async def wait_on_run(run_id, thread_id, client):
    run = await async_openai_run_retrieve(client, thread_id, run_id)
    while run.status == "queued" or run.status == "in_progress":
        await asyncio.sleep(0.5)
        run = await async_openai_run_retrieve(client, thread_id, run_id)
    return run

async def process_run_response(run_id, thread_id, client):
    run = await wait_on_run(run_id, thread_id, client)
    if run.status == 'completed':
        messages = await async_openai_messages_list(client, thread_id)
        return "\n".join([f"{message.role.title()}: {message.content[0].text.value}" for message in messages.data])
    else:
        return "Run não foi concluído com sucesso."
    
@app.on_event("startup")
async def create_assistant():
    global assistant_id
    response = await asyncio.to_thread(
        lambda: client.beta.assistants.create(
            model="gpt-3.5-turbo-1106",
            name="Your Assistant Name",
            tools=[{"type": "code_interpreter"}],
            instructions="You are a helpful assistant, skilled in explaining complex concepts in simple terms."
        )
    )
    assistant_id = response.id  # Acesso como propriedade



@app.get("/")
def read_root():
    return {"Hello": "World"}

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    while True:
        message = await websocket.receive_text()
        async for text in get_ai_response(message):
            await websocket.send_text(text)
