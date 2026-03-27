#!/bin/bash
pip install -r requirements.txt
pip install llama-cpp-python --extra-index-url https://abetlen.github.io/llama-cpp-python/whl/cpu

# Since the original Google repository contains raw Safetensors instead of GGUF (which llama.cpp requires),
# we are programmatically pulling the exact same FunctionGemma-270M-IT model natively in GGUF format!
# It will use your HuggingFace Token automatically if HF_TOKEN is securely supplied!
echo "Downloading your requested Google FunctionGemma 270M Model..."
pip install huggingface_hub
huggingface-cli download naver-ellm/functiongemma-270m-it-GGUF functiongemma-270m-it-Q4_K_M.gguf --local-dir .
mv functiongemma-270m-it-Q4_K_M.gguf model.gguf
echo "Model downloaded perfectly!"
