from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from mcp.server.fastmcp import FastMCP
from pydantic import BaseModel
import os

app = FastAPI(title="Nemo Console")

# Enable CORS so your Namecheap website can talk to this Render API!
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all domains, or you can restrict to ["https://vibecoderscommunity.com"]
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# -----------------------------------------------------
# MCP TOOLS FOR ANTIGRAVITY IDE
# -----------------------------------------------------
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
    # This acts as a proxy until you attach AI logic
    reply = f"Nemo Server Received: '{user_msg}'.\n(System Note: Agent is alive on Render!)"
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
            body { background: linear-gradient(135deg, #0f172a, #1e293b); color: #f8fafc; font-family: 'Inter', sans-serif; align-items: center; justify-content: center; height: 100vh; margin: 0; display: flex; }
            h1 { text-align: center; font-weight: 600; letter-spacing: 1px; }
        </style>
    </head>
    <body>
        <h1>🟢 NEMO API OVER RENDER</h1>
        <p>Your API is ready to accept cross-origin requests from Namecheap!</p>
    </body>
    </html>
    """
    return HTMLResponse(content=html_content)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app:app", host="0.0.0.0", port=int(os.getenv("PORT", 8000)))
