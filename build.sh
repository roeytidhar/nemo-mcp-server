#!/bin/bash
pip install -r requirements.txt
pip install llama-cpp-python --extra-index-url https://abetlen.github.io/llama-cpp-python/whl/cpu

# Download the model from the Namecheap server where it's safely fully hosted
echo "Downloading the huge model file from Namecheap... This might take a minute..."
wget -qO FunctionGemma-3-270M.gguf https://vibecoderscommunity.com/nemo/FunctionGemma-3-270M.gguf
echo "Model downloaded perfectly!"
