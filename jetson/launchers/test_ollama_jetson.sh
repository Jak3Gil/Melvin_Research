#!/bin/bash
# Test Ollama LLM on Jetson

echo "=========================================="
echo "Testing Ollama LLM on Jetson"
echo "=========================================="
echo ""

# Check if Ollama is installed
if ! command -v ollama &> /dev/null; then
    echo "✗ Ollama is not installed"
    echo ""
    echo "To install Ollama:"
    echo "  curl -fsSL https://ollama.ai/install.sh | sh"
    exit 1
fi

echo "✓ Ollama is installed"
ollama --version
echo ""

# Check if Ollama service is running
if ! pgrep -x "ollama" > /dev/null; then
    echo "⚠ Ollama service is not running"
    echo "  Starting Ollama service..."
    ollama serve &
    sleep 3
fi

echo "✓ Ollama service is running"
echo ""

# List available models
echo "Available models:"
ollama list
echo ""

# Check if llama3.2:1b is available
if ollama list | grep -q "llama3.2:1b"; then
    echo "✓ Model 'llama3.2:1b' is available"
else
    echo "⚠ Model 'llama3.2:1b' not found"
    echo "  Downloading model (this may take several minutes)..."
    ollama pull llama3.2:1b
fi

echo ""
echo "=========================================="
echo "Testing LLM with a simple query"
echo "=========================================="
echo ""

echo "Query: 'What is 2+2?'"
echo ""
echo "Response:"
ollama run llama3.2:1b "What is 2+2? Answer in one sentence."

echo ""
echo "=========================================="
echo "Testing LLM with a conversation"
echo "=========================================="
echo ""

echo "Query: 'Tell me a short joke about robots'"
echo ""
echo "Response:"
ollama run llama3.2:1b "Tell me a short joke about robots"

echo ""
echo "=========================================="
echo "✓ Ollama test complete!"
echo "=========================================="
echo ""
echo "To use Ollama interactively:"
echo "  ollama run llama3.2:1b"
echo ""
echo "To use a different model:"
echo "  ollama pull llama3.2:3b    # Larger model, better quality"
echo "  ollama run llama3.2:3b"
echo ""

