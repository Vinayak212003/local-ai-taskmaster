#!/usr/bin/env bash
# scripts/pull_models.sh — Pull recommended Ollama models
# Usage: bash scripts/pull_models.sh

echo "🤖 Pulling Ollama models for LocalAI TaskMaster..."
echo ""
echo "Recommended model for 8GB RAM:"
echo "  mistral (4.1GB) — best balance of quality + speed"
echo ""

read -p "Pull mistral? [Y/n] " yn
case $yn in
  [Nn]*) echo "Skipped mistral";;
  *) ollama pull mistral && echo "✅ mistral ready";;
esac

echo ""
echo "Optional lightweight models:"
read -p "Pull phi3 (2.3GB — fast on CPU)? [y/N] " yn
case $yn in
  [Yy]*) ollama pull phi3 && echo "✅ phi3 ready";;
  *) echo "Skipped phi3";;
esac

read -p "Pull gemma2:2b (1.6GB — smallest)? [y/N] " yn
case $yn in
  [Yy]*) ollama pull gemma2:2b && echo "✅ gemma2:2b ready";;
  *) echo "Skipped gemma2:2b";;
esac

echo ""
echo "Currently available models:"
ollama list
