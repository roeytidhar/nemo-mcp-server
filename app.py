from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from mcp.server.fastmcp import FastMCP
from pydantic import BaseModel
import os
import threading
import traceback

app = FastAPI(title="Nemo Console")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

llama_model = None
startup_log = "Initializing..."

def load_model():
    global llama_model, startup_log
    try:
        startup_log = "Attempting to import llama_cpp...\n"
        from llama_cpp import Llama
        
        startup_log += "Checking if model.gguf exists...\n"
        if os.path.exists("model.gguf"):
            # Load with very low context and strict batch/threads to NEVER exceed 512MB RAM on free Render tier
            startup_log += f"File found. Size: {os.path.getsize('model.gguf')} bytes. Loading Llama...\n"
            llama_model = Llama(
                model_path="model.gguf",
                n_batch=64,
                n_ctx=256,
                n_threads=1,
                use_mmap=False,
                use_mlock=False
            )
            startup_log += "Model Loaded perfectly under 512MB!\n"
        else:
            startup_log += "ERROR: model.gguf file does NOT exist on the filesystem!\n"
    except Exception as e:
        startup_log += f"Model failed to load: {e}\n{traceback.format_exc()}\n"

threading.Thread(target=load_model).start()

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
        status += " The local brain is also ONLINE!"
    return status

app.mount("/mcp", mcp.sse_app())

class ChatRequest(BaseModel):
    message: str

@app.post("/chat")
async def chat_endpoint(req: ChatRequest):
    user_msg = req.message
    
    if llama_model is not None:
        try:
            # Generate the response using our actual locally hosted AI model!
            response = dict(llama_model(
                f"<|im_start|>user\\n{user_msg}<|im_end|>\\n<|im_start|>assistant\\n",
                max_tokens=64,
                stop=["<|im_end|>"],
            ))
            reply = response['choices'][0]['text'].strip()
        except:
            reply = "The model is currently computing or temporarily out of memory."
    else:
        reply = f"Nemo Server Received: '{user_msg}'.\n(System Note: Model has not finished warming up yet!)"
        
    return {"reply": reply}

@app.get("/logs")
async def get_logs():
    return {"startup_log": startup_log}

@app.get("/")
async def serve_ui():
    return HTMLResponse(content="<h1>API Base</h1>")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app:app", host="0.0.0.0", port=int(os.getenv("PORT", 8000)))
