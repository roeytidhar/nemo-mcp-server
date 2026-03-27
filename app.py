from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from mcp.server.fastmcp import FastMCP
from pydantic import BaseModel
import os

app = FastAPI(title="Nemo Console")

# -----------------------------------------------------
# MCP TOOLS FOR ANTIGRAVITY IDE
# -----------------------------------------------------
# Use 0.0.0.0 to accept any host since Render provides a dynamic URL
mcp = FastMCP("Nemo Server", host="0.0.0.0")

@mcp.tool()
def nemo_save_note(note: str) -> str:
    with open("nemo_notes.txt", "a") as f:
        f.write(note + "\n")
    return "Note saved successfully to the server!"

@mcp.tool()
def nemo_run_server_check() -> str:
    return "Nemo Server is ALIVE and connected via MCP!"

# Mount the MCP server
app.mount("/mcp", mcp.sse_app())

# -----------------------------------------------------
# WEB INTERFACE (HTML UI)
# -----------------------------------------------------
class ChatRequest(BaseModel):
    message: str

@app.post("/chat")
async def chat_endpoint(req: ChatRequest):
    user_msg = req.message
    reply = f"Nemo Server Received: '{user_msg}'.\n(System Note: Connect via Antigravity MCP for full agent logic!)"
    return {"reply": reply}

@app.get("/")
async def serve_ui():
    html_content = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Nemo AI Interface</title>
        <style>
            @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600&display=swap');
            body {
                background: linear-gradient(135deg, #0f172a, #1e293b);
                color: #f8fafc;
                font-family: 'Inter', sans-serif;
                height: 100vh;
                margin: 0;
                display: flex;
                flex-direction: column;
                align-items: center;
                justify-content: center;
            }
            .chat-container {
                width: 90%;
                max-width: 600px;
                background: rgba(255, 255, 255, 0.05);
                border: 1px solid rgba(255, 255, 255, 0.1);
                border-radius: 16px;
                backdrop-filter: blur(10px);
                box-shadow: 0 4px 30px rgba(0,0,0,0.5);
                overflow: hidden;
                display: flex;
                flex-direction: column;
                height: 70vh;
            }
            .header {
                padding: 20px;
                background: rgba(0,0,0,0.2);
                border-bottom: 1px solid rgba(255, 255, 255, 0.05);
                text-align: center;
                font-weight: 600;
                letter-spacing: 1px;
            }
            .messages {
                flex: 1;
                padding: 20px;
                overflow-y: auto;
                display: flex;
                flex-direction: column;
                gap: 15px;
            }
            .msg {
                padding: 12px 18px;
                border-radius: 12px;
                max-width: 75%;
                line-height: 1.5;
            }
            .msg.user {
                background: #3b82f6;
                align-self: flex-end;
            }
            .msg.nemo {
                background: rgba(255, 255, 255, 0.1);
                align-self: flex-start;
            }
            .input-area {
                padding: 20px;
                background: rgba(0,0,0,0.2);
                display: flex;
                gap: 10px;
            }
            input {
                flex: 1;
                padding: 15px;
                border-radius: 8px;
                border: 1px solid rgba(255, 255, 255, 0.2);
                background: rgba(0,0,0,0.3);
                color: white;
                font-size: 16px;
                outline: none;
            }
            button {
                padding: 0 25px;
                border-radius: 8px;
                border: none;
                background: #3b82f6;
                color: white;
                font-weight: 600;
                font-size: 16px;
                cursor: pointer;
                transition: 0.2s;
            }
            button:hover {
                background: #2563eb;
            }
        </style>
    </head>
    <body>
        <div class="chat-container">
            <div class="header">🟢 NEMO CONSOLE (RENDER)</div>
            <div class="messages" id="msgs">
                <div class="msg nemo">Hello! I am Nemo, your Render-hosted agent server. I am online and waiting for Antigravity's instructions! Send a test message below:</div>
            </div>
            <div class="input-area">
                <input type="text" id="chatbox" placeholder="Send a message to the API..." onkeypress="handleKey(event)">
                <button onclick="send()">Send</button>
            </div>
        </div>

        <script>
            async function send() {
                const box = document.getElementById('chatbox');
                const text = box.value.trim();
                if(!text) return;
                
                addMsg(text, 'user');
                box.value = '';

                try {
                    const res = await fetch('chat', {
                        method: 'POST',
                        headers: {'Content-Type': 'application/json'},
                        body: JSON.stringify({message: text})
                    });
                    const data = await res.json();
                    addMsg(data.reply, 'nemo');
                } catch(e) {
                    addMsg('Error reaching API.', 'nemo');
                }
            }

            function addMsg(text, sender) {
                const msgs = document.getElementById('msgs');
                const div = document.createElement('div');
                div.className = 'msg ' + sender;
                div.innerText = text;
                msgs.appendChild(div);
                msgs.scrollTop = msgs.scrollHeight;
            }

            function handleKey(e) {
                if(e.key === 'Enter') send();
            }
        </script>
    </body>
    </html>
    """
    return HTMLResponse(content=html_content)

if __name__ == "__main__":
    import uvicorn
    # When deployed on Render or running locally, uses uvicorn directly
    uvicorn.run("app:app", host="0.0.0.0", port=int(os.getenv("PORT", 8000)))
