from datetime import datetime
import json
import logging
import traceback

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from websockets.exceptions import ConnectionClosedOK

from langchain.chains import ConversationChain

from story import get_chain
from webapp.server.schemas import ChatResponse

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

app = FastAPI()

app.mount("/static", StaticFiles(directory="webapp/static"), name="static")
templates = Jinja2Templates(directory="webapp/templates")


class ConnectionManager:
    def __init__(self):
        self.active_connections: list[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def send_personal_message(self, message: str, websocket: WebSocket):
        await websocket.send_text(message)

    async def broadcast(self, message: str):
        for connection in self.active_connections:
            await connection.send_text(message)


manager = ConnectionManager()


@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    return templates.TemplateResponse(
        context={'request': request}, name="index.html"
    )


@app.websocket("/ws/{client_id}")
async def websocket_endpoint(websocket: WebSocket, client_id: int):
    await manager.connect(websocket)

    # Initialize conversation chain
    conversation = get_chain()

    while True:
        # Mostly lifted out of https://github.com/pors/langchain-chat-websockets
        try:
            message = await websocket.receive_text()
            data = json.loads(message)
            message_type = data.get("type")
            
            if message_type == 'end_conversation':
                #end_conversation(conversation)
                return

            # Handle unknown message types
            if message_type != 'message':
                raise ValueError(f'Unknown type received: {message_type}')

            # Receive and send back the client message
            user_msg = data.get('value')

            resp = ChatResponse(
                sender="human", message=user_msg, type="stream")
            
            write_log_entry(client_id, "user", user_msg)

            await websocket.send_json(resp.dict())

            # Construct a response
            start_resp = ChatResponse(sender="bot", message="", type="start")
            await websocket.send_json(start_resp.dict())

            ai_message = ''
            # Send the message to the chain and feed the response back to the client
            # the stream handler will send chunks as they come
            async for chunk in conversation.astream(user_msg):
                msg = chunk['response']
                ai_message += msg
                fragment = ChatResponse(sender="bot", message=msg, type="stream")

                await websocket.send_json(fragment.dict())

            # Send the end-response back to the client
            end_resp = ChatResponse(sender="bot", message="", type="end")
            write_log_entry(client_id, "bot", ai_message)
            await websocket.send_json(end_resp.dict())

        except WebSocketDisconnect:
            logging.info("WebSocketDisconnect")
            # TODO try to reconnect with back-off
            manager.disconnect(websocket)
            break

        except ConnectionClosedOK:
            logging.info("ConnectionClosedOK")
            # TODO handle this?
            break

        except Exception as e:
            logging.error(e)
            resp = ChatResponse(
                sender="bot",
                message="Sorry, something went wrong. Try again.",
                type="error",
            )
            await websocket.send_json(resp.dict())


@app.get("/health")
async def health():
    """Check the api is running"""
    return {"status": "🤙"}


def write_log_entry(session_id, sender, entry):
        timestamp = datetime.today().strftime('%Y-%m-%d_%H:%M:%S')

        with open(f"logs/{session_id}.log", "w+") as f:
            f.write(f'[{timestamp}] {sender}: {entry}')