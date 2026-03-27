from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from mcp.server.fastmcp import FastMCP
from pydantic import BaseModel
import os
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
startup_log = "Waiting for first chat request to boot brain (to prevent CPU starvation)...\n"
is_booting = False

def lazy_load_model():
    global llama_model, startup_log, is_booting
    is_booting = True
    try:
        startup_log += "Attempting to import llama_cpp...\n"
        from llama_cpp import Llama
        
        startup_log += "Checking if model.gguf exists...\n"
        if os.path.exists("model.gguf"):
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
    is_booting = False

mcp = FastMCP("Nemo Server", host="0.0.0.0")

@mcp.tool()
def nemo_save_note(note: str) -> str:
    with open("nemo_notes.txt", "a") as f:
        f.write(note + "\n")
    return "Note saved successfully to the server!"

@mcp.tool()
def nemo_run_server_check() -> str:
    return "Nemo Server is ALIVE and connected via MCP!"

app.mount("/mcp", mcp.sse_app())

class ChatRequest(BaseModel):
    message: str

@app.post("/chat")
async def chat_endpoint(req: ChatRequest):
    global is_booting, llama_model
    user_msg = req.message
    
    # Lazy load on first request to bypass Render's strict health check 60-second limit
    if llama_model is None and not is_booting:
        import threading
        threading.Thread(target=lazy_load_model).start()
        return {"reply": f"Nemo Server Received: '{user_msg}'.\n(System Note: Nemo has received power. His brain is now waking up for the first time. Give me 10 seconds to load and send another message!)"}
    
    if is_booting:
        return {"reply": f"Nemo Server Received: '{user_msg}'.\n(System Note: Heavy AI Model is currently booting in background! Please wait a few seconds and try again!)"}
        
    if llama_model is not None:
        try:
            response = dict(llama_model(
                f"<|im_start|>user\\n{user_msg}<|im_end|>\\n<|im_start|>assistant\\n",
                max_tokens=64,
                stop=["<|im_end|>"],
            ))
            reply = response['choices'][0]['text'].strip()
        except Exception as e:
            reply = "The model is currently computing or temporarily out of memory."
    else:
        reply = "Brain initialization failed. Check /logs"
        
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
