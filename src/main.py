import os
from enum import Enum
import asyncio
from dotenv import load_dotenv, find_dotenv
import openai

from fastapi import FastAPI, WebSocket
from agents.group_chat import CodeGenGroupChat


load_dotenv(find_dotenv())
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
        self.active_connections: list[CodeGenGroupChat] = []

    async def connect(self, autogen_chat: CodeGenGroupChat):
        await autogen_chat.websocket.accept()
        self.active_connections.append(autogen_chat)

    async def disconnect(self, autogen_chat: CodeGenGroupChat):
        autogen_chat.client_receive_queue.put_nowait("DO_FINISH")
        print(f"autogen_chat {autogen_chat.chat_id} disconnected")
        self.active_connections.remove(autogen_chat)


manager = ConnectionManager()


@app.get("/")
async def root():
    return {"message": "AutoGen AI Agent PoC"}


async def send_to_client(autogen_chat: CodeGenGroupChat):
    while True:
        reply = await autogen_chat.client_receive_queue.get()
        if reply and reply == "DO_FINISH":
            autogen_chat.client_receive_queue.task_done()
            break
        await autogen_chat.websocket.send_text(reply)
        autogen_chat.client_receive_queue.task_done()
        await asyncio.sleep(0.05)


async def receive_from_client(autogen_chat: CodeGenGroupChat):
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
        group_chat = CodeGenGroupChat(chat_id=chat_id, websocket=websocket)
        await manager.connect(group_chat)

        # wait for client to send a message then send to chat
        data = await group_chat.websocket.receive_text()
        future_calls = asyncio.gather(
            send_to_client(group_chat), receive_from_client(group_chat)
        )
        await group_chat.start(data)
        print(f"PROGRAMMER MESSAGES: \n{group_chat.get_chat_messages(group_chat.programmer, group_chat.manager)}")
        print("DO_FINISHED")
    except Exception as e:
        print("ERROR", str(e))
    finally:
        try:
            await manager.disconnect(group_chat)

            print("DISCONNECTED")
        except:
            pass
