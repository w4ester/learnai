# Unsloth Studio: Fine-Tune Your Own AI Model

A one-pager for going from a base model to your own custom AI, then running it locally with Ollama and LearnAI.

## What Is Unsloth?

Unsloth is a Python library that makes fine-tuning large language models **2-5x faster** with **80% less memory** than standard methods. Unsloth Studio adds a GUI on top so you can fine-tune without writing training scripts from scratch.

**The learning loop:**
```
Hugging Face model → Unsloth fine-tune → GGUF export → Ollama → LearnAI
```

You start with a public base model, teach it your data, convert it to a format Ollama understands, and then chat with your custom model in LearnAI. Full circle.

## Prerequisites

- **Python 3.10+** — check with `python3 --version`
- **GPU recommended** — NVIDIA with CUDA (fine-tuning is GPU-heavy). No GPU? Use Google Colab's free T4.
- **Hugging Face account** — free at [huggingface.co](https://huggingface.co)
- **Ollama** — already installed if you followed the LearnAI setup

## Option A: Google Colab (No Local GPU Needed)

The fastest path. Colab gives you a free GPU.

1. Go to [unsloth.ai](https://unsloth.ai) and pick a starter notebook
2. Click "Open in Colab"
3. Select **Runtime → Change runtime type → T4 GPU**
4. Run each cell top to bottom
5. The notebook walks you through: load model → prepare dataset → train → export

**Recommended starter notebooks:**
- Fine-tune Llama 3.1 8B
- Fine-tune Gemma 2B
- Fine-tune Mistral 7B

Each takes ~15 minutes on a free Colab T4.

## Option B: Local Setup (NVIDIA GPU Required)

```bash
# Create a virtual environment
python3 -m venv unsloth-env
source unsloth-env/bin/activate

# Install unsloth (picks the right torch+cuda version)
pip install unsloth

# Verify GPU is detected
python3 -c "import torch; print(torch.cuda.is_available())"
# Should print: True
```

Then follow the same notebook workflow locally, or use Unsloth Studio's GUI.

## Fine-Tuning Basics (What's Actually Happening)

| Concept | Plain English |
|---------|--------------|
| **Base model** | A pre-trained model from Hugging Face (e.g., `unsloth/llama-3.1-8b-bnb-4bit`) |
| **Dataset** | Your training data — pairs of (instruction, response) in JSON or CSV |
| **LoRA / QLoRA** | A technique that trains only a small adapter instead of the full model. Uses ~80% less memory. |
| **Epochs** | How many times the model sees your entire dataset. 1-3 is usually enough. |
| **Loss** | A number that goes down during training. Lower = model is learning. |
| **Merged model** | Your base model + trained adapter combined into one model file. |

## Preparing Your Dataset

Your data should look like this (JSON format):

```json
[
  {
    "instruction": "Summarize this meeting transcript.",
    "input": "The team discussed the Q3 roadmap...",
    "output": "Key decisions: 1) Launch feature X by August..."
  },
  {
    "instruction": "Write a follow-up email.",
    "input": "Client asked about pricing tiers.",
    "output": "Subject: Pricing Information..."
  }
]
```

**Tips:**
- Start with 50-200 examples (quality over quantity)
- Make your examples look like real conversations you want the model to handle
- Diverse examples teach better than repetitive ones
- Clean your data — typos and inconsistencies get learned too

## Exporting to GGUF (For Ollama)

After training, export to GGUF format so Ollama can run it:

```python
# In your notebook or script, after training:
model.save_pretrained_gguf(
    "my-custom-model",
    tokenizer,
    quantization_method="q4_k_m"  # good balance of quality vs size
)
```

This creates a `.gguf` file you can load into Ollama.

## Loading Into Ollama

```bash
# Create a Modelfile
cat > Modelfile << 'EOF'
FROM ./my-custom-model-unsloth.Q4_K_M.gguf

PARAMETER temperature 0.7
PARAMETER top_p 0.9

SYSTEM "You are a helpful assistant fine-tuned for [your use case]."
EOF

# Build the Ollama model
ollama create my-custom-model -f Modelfile

# Test it
ollama run my-custom-model "Hello, are you working?"

# Verify it shows up
ollama list
```

## Using Your Model in LearnAI

Once the model is in Ollama, it automatically appears in LearnAI's model dropdown. No config changes needed.

1. Open LearnAI (`http://localhost:9180`)
2. Click the model dropdown in the header
3. Select `my-custom-model`
4. Start chatting with your fine-tuned model

You can also create a **Profile** in LearnAI that locks to your custom model with a specific system prompt and sampling parameters. That way you have a one-click preset for your fine-tuned model.

## Quantization Options

When exporting to GGUF, you choose a quantization level. Tradeoff: smaller = faster + less RAM, but slightly less accurate.

| Method | Size (7B model) | RAM needed | Quality | When to use |
|--------|-----------------|-----------|---------|-------------|
| `q4_k_m` | ~4 GB | ~6 GB | Good | Default choice, runs on most hardware |
| `q5_k_m` | ~5 GB | ~7 GB | Better | You have the RAM and want higher quality |
| `q8_0` | ~7 GB | ~9 GB | Near-original | Maximum quality, needs more RAM |
| `f16` | ~14 GB | ~16 GB | Original | Only if you have 16+ GB RAM |

## Troubleshooting

**"CUDA out of memory"**
- Use a smaller model (2B or 4B instead of 7B)
- Reduce `max_seq_length` in your training config
- Use Colab if your local GPU is too small

**"Model not showing in Ollama"**
- Verify with `ollama list`
- Check the Modelfile path points to the actual .gguf file
- Try `ollama create` again with the full absolute path

**"Fine-tuned model gives weird outputs"**
- Check your dataset format matches what the base model expects
- Try fewer epochs (overfitting = memorizing instead of learning)
- Add more diverse training examples

## Resources

- [unsloth.ai](https://unsloth.ai) — official site, starter notebooks, docs
- [Hugging Face Hub](https://huggingface.co/unsloth) — Unsloth's pre-quantized base models
- [Ollama model creation docs](https://ollama.com/blog/import) — importing custom GGUF models
- [GGUF format spec](https://github.com/ggerganov/ggml/blob/master/docs/gguf.md) — technical details on the file format
