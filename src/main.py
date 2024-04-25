import os
from enum import Enum
import asyncio
from dotenv import load_dotenv, find_dotenv
import openai

from fastapi import FastAPI, WebSocket
from agents.group_chat import AutogenCodeGenGroupChat


_ = load_dotenv(find_dotenv()) # read local .env file
openai.api_key = os.environ['OPENAI_API_KEY']
openai.log='debug'


app = FastAPI()
app.autogen_chat = {}


class OpenAIModels(Enum):
    GPT4 = "gpt-4"
    GPT4_TURBO = "gpt-4-turbo-preview"
    GPT3_5_TURBO = "gpt-3.5-turbo"


class ConnectionManager:
    def __init__(self):
        self.active_connections: list[AutogenCodeGenGroupChat] = []

    async def connect(self, autogen_chat: AutogenCodeGenGroupChat):
        await autogen_chat.websocket.accept()
        self.active_connections.append(autogen_chat)

    async def disconnect(self, autogen_chat: AutogenCodeGenGroupChat):
        autogen_chat.client_receive_queue.put_nowait("DO_FINISH")
        print(f"autogen_chat {autogen_chat.chat_id} disconnected")
        self.active_connections.remove(autogen_chat)


manager = ConnectionManager()


@app.get("/")
async def root():
    return {"message": "AutoGen AI Agent PoC"}


async def send_to_client(autogen_chat: AutogenCodeGenGroupChat):
    while True:
        reply = await autogen_chat.client_receive_queue.get()
        if reply and reply == "DO_FINISH":
            autogen_chat.client_receive_queue.task_done()
            break
        await autogen_chat.websocket.send_text(reply)
        autogen_chat.client_receive_queue.task_done()
        await asyncio.sleep(0.05)


async def receive_from_client(autogen_chat: AutogenCodeGenGroupChat):
    while True:
        data = await autogen_chat.websocket.receive_text()
        if data and data == "DO_FINISH":
            await autogen_chat.client_receive_queue.put("DO_FINISH")
            await autogen_chat.client_sent_queue.put("DO_FINISH")
            break
        await autogen_chat.client_sent_queue.put(data)
        await asyncio.sleep(0.05)


@app.websocket("/ws/{chat_id}")
async def websocket_endpoint(websocket: WebSocket, chat_id: str):
    try:
        # setup chat and websocket connections
        autogen_chat = AutogenCodeGenGroupChat(chat_id=chat_id, websocket=websocket)
        await manager.connect(autogen_chat)

        # wait for client to send a message then send to chat
        data = await autogen_chat.websocket.receive_text()
        future_calls = asyncio.gather(
            send_to_client(autogen_chat), receive_from_client(autogen_chat)
        )
        await autogen_chat.start(data)
        print("DO_FINISHED")
    except Exception as e:
        print("ERROR", str(e))
    finally:
        try:
            await manager.disconnect(autogen_chat)
            print("DISCONNECTED")
        except:
            pass
