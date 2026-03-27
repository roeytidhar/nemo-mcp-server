from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from mcp.server.fastmcp import FastMCP
from pydantic import BaseModel
import os
import threading

app = FastAPI(title="Nemo Console")

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# -----------------------------------------------------
# AI MODEL LOADING (LLAMA-CPP)
# -----------------------------------------------------
# We delay loading to not block the main thread
llama_model = None

def load_model():
    global llama_model
    try:
        from llama_cpp import Llama
        if os.path.exists("FunctionGemma-3-270M.gguf"):
            # Load with strict memory limits for free tier
            llama_model = Llama(
                model_path="FunctionGemma-3-270M.gguf",
                n_batch=128,
                n_threads=2,
                n_gqa=1
            )
            print("Llama Model Loaded successfully!")
    except Exception as e:
        print(f"Model failed to load: {e}")

threading.Thread(target=load_model).start()

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
    status = "Nemo Server is ALIVE and connected via MCP!"
    if llama_model is not None:
        status += " The FunctionGemma model is also ONLINE!"
    return status

app.mount("/mcp", mcp.sse_app())

# -----------------------------------------------------
# CHAT WEB INTERFACE
# -----------------------------------------------------
class ChatRequest(BaseModel):
    message: str

@app.post("/chat")
async def chat_endpoint(req: ChatRequest):
    user_msg = req.message
    
    if llama_model is not None:
        try:
            # Generate the response using our actual locally hosted AI model!
            response = dict(llama_model(
                f"User: {user_msg}\\nAgent: ",
                max_tokens=64,
                stop=["User:", "\\n"],
            ))
            reply = response['choices'][0]['text'].strip()
        except:
            reply = "The model is currently computing or OOM'd."
    else:
        reply = f"Nemo Server Received: '{user_msg}'.\n(System Note: Model is still warming up on Render!)"
        
    return {"reply": reply}

@app.get("/")
async def serve_ui():
    return HTMLResponse(content="<h1>API Base</h1>")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app:app", host="0.0.0.0", port=int(os.getenv("PORT", 8000)))
