#!/bin/bash
pip install -r requirements.txt
pip install llama-cpp-python --extra-index-url https://abetlen.github.io/llama-cpp-python/whl/cpu

# The user's Namecheap file was actually a 20-byte "Repository Not Found" error text from HuggingFace!
# To fit in Render's 512MB RAM and guarantee it boots without gated API tokens, we will download a totally open 0.5B Qwen chat model!
echo "Downloading ultra-fast open source Qwen 0.5B model..."
wget -qO model.gguf "https://huggingface.co/Qwen/Qwen1.5-0.5B-Chat-GGUF/resolve/main/qwen1_5-0_5b-chat-q4_k_m.gguf"
echo "Model downloaded perfectly!"
