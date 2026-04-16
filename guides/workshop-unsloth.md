# Workshop: Fine-Tune Your First Model with Unsloth

**Duration:** 60 minutes
**Audience:** Anyone who has LearnAI running and a Hugging Face account
**Outcome:** A custom fine-tuned model running in Ollama, callable from LearnAI

> You will not write training code from scratch. You will use an Unsloth notebook that already works, modify the dataset for your own use case, and watch the model learn. Then you will export it to GGUF and run it locally.

---

## Before you start (5 minutes)

Check all three are true before proceeding:

- [ ] LearnAI is running at `http://localhost:9180` and responds
- [ ] Ollama is installed and `ollama list` shows at least one model
- [ ] You have a free [Hugging Face](https://huggingface.co) account (for downloading base models)

If any of these fails, stop and fix them first. Do not try to fine-tune without a working base setup.

### Hardware path

Pick your path:

| Path | Hardware | Model size | Time |
|---|---|---|---|
| **A: Google Colab free** | T4 GPU in browser | 2B - 8B | 15-20 min training |
| **B: Google Colab Pro ($10/mo)** | A100 GPU | up to 26B | 20-30 min training |
| **C: Local NVIDIA GPU** | RTX 3090 / 4090 | up to 13B | 15-25 min training |
| **D: Cloud GPU rental (~$1/hr)** | RunPod / Lambda A100 | up to 70B | varies |

Most attendees should start with **Path A** (Colab free tier). You can always go bigger later.

---

## Phase 1: Pick a use case (5 minutes)

Before touching any code, decide what you are fine-tuning FOR. Good beginner use cases:

1. **Your writing style** — train on 50 of your own emails so the model writes like you
2. **Domain-specific Q&A** — train on your field's jargon and typical questions
3. **Role-specific assistant** — train on examples of how a customer support agent / teacher / nurse / coach would respond
4. **Family AI** — train on family recipes, routines, traditions (local-only data, never touches cloud)

Pick one. Write it down in one sentence: "I want a model that _____________."

---

## Phase 2: Prepare a dataset (15 minutes)

The dataset is what teaches the model. Quality beats quantity.

### Format

Every example is a pair:

```json
{
  "instruction": "What the user asks",
  "input": "Optional context (can be empty)",
  "output": "The response you want the model to give"
}
```

### Starter volume

- **Minimum to see behavior change:** 30 examples
- **Sweet spot for beginners:** 50-100 examples
- **Solid production dataset:** 500+ examples

**Quality rules:**
- Make each output look like the BEST response you would write yourself
- Vary the input wording — same intent, different phrasing
- Avoid duplicate phrasings (the model will memorize instead of generalizing)
- Clean your data — typos and inconsistencies get learned too

### Example: "Writes in my voice" dataset

```json
[
  {
    "instruction": "Reply to this email acknowledging the meeting time.",
    "input": "Hi, can we meet Thursday at 2pm?",
    "output": "Howdy! Thursday at 2pm works great. I'll send a calendar invite shortly. Talk soon."
  },
  {
    "instruction": "Write a short message canceling plans.",
    "input": "Dinner Friday night with the Johnsons",
    "output": "Hey folks, something came up and I need to push Friday. Can we grab a bite next week instead? Sorry for the shuffle."
  }
]
```

Save your dataset as `my_data.json`. Checkpoint: you have at least 30 examples.

---

## Phase 3: Open an Unsloth notebook (5 minutes)

Go to [unsloth.ai](https://unsloth.ai) and pick a starter notebook. For most attendees:

**Recommended:** "Gemma 3 4B SFT" (small, fast, runs on free Colab T4)

Click "Open in Colab." A Google Colab notebook opens.

In Colab:
1. **Runtime → Change runtime type → T4 GPU → Save**
2. Run the first cell (imports) — confirm no errors
3. Run the second cell (load model) — this downloads ~2.5 GB. Wait for it.

Checkpoint: you see "Model loaded" or similar success output.

---

## Phase 4: Load your dataset (10 minutes)

In the Colab notebook, find the cell that loads the dataset. It usually looks like this:

```python
from datasets import load_dataset
dataset = load_dataset("some-default-dataset")
```

Replace that with your own data:

```python
# Upload your my_data.json to Colab (Files panel on the left)
from datasets import load_dataset
dataset = load_dataset("json", data_files="my_data.json", split="train")
```

To upload `my_data.json` in Colab: click the folder icon on the left sidebar, then the upload icon at the top of that panel.

Run the cell. Verify by running:

```python
print(dataset)
print(dataset[0])
```

Checkpoint: you see your first example printed back. Counts and fields look correct.

---

## Phase 5: Train the model (15-20 minutes)

Scroll down in the notebook to the training cell. It looks something like:

```python
trainer.train()
```

**Before running:** look for settings you can tune. The defaults usually work but these matter:

| Setting | What it does | Safe value for beginners |
|---|---|---|
| `num_train_epochs` | How many times the model sees your data | 1-3 |
| `learning_rate` | How big each learning step is | Keep the default |
| `per_device_train_batch_size` | Examples per GPU pass | Keep the default |
| `max_seq_length` | Max tokens per example | 2048 |

Start with whatever defaults the notebook came with. Don't tune until you've done this once.

Run the training cell. Training output appears:

```
Step 10/75 | loss: 2.14
Step 20/75 | loss: 1.87
Step 30/75 | loss: 1.52
...
```

**What to watch:**
- **Loss going down** = model is learning. Good.
- **Loss flat or bouncing** = dataset might be inconsistent, learning rate might be too low/high
- **Loss went to zero** = overfitting (memorizing). Cut epochs or add more data.

Checkpoint: training finishes without errors. Loss is lower at the end than at the start.

---

## Phase 6: Test the model in the notebook (5 minutes)

Before exporting, test it while it is still in memory:

```python
FastLanguageModel.for_inference(model)
inputs = tokenizer(["What is your favorite color?"], return_tensors="pt").to("cuda")
outputs = model.generate(**inputs, max_new_tokens=100)
print(tokenizer.decode(outputs[0]))
```

Try a few prompts related to what you trained it on. Does it sound like what you wanted?

**If the output is weird:**
- Too repetitive → reduce epochs, add more diverse examples
- Ignores your training → increase epochs or check your dataset format
- Gibberish → stop, re-check the training loss pattern

Checkpoint: you get coherent responses that reflect your training.

---

## Phase 7: Export to GGUF (5 minutes)

GGUF is the file format Ollama reads. Find or add this cell in the notebook:

```python
model.save_pretrained_gguf(
    "my-custom-model",
    tokenizer,
    quantization_method="q4_k_m"
)
```

Quantization options:
- `q4_k_m` — default, good quality, runs on most hardware
- `q5_k_m` — higher quality, needs more RAM
- `q8_0` — near-original, needs ~8GB RAM for a 7B model

Run the cell. Wait 2-5 minutes.

A file appears in your Colab files panel named something like `my-custom-model-unsloth.Q4_K_M.gguf`.

**Download it:** right-click the file → "Download." This pulls the model to your local machine. The download is 2-5 GB.

Checkpoint: the GGUF file is on your local machine (usually `~/Downloads/`).

---

## Phase 8: Load into Ollama (5 minutes)

Open a terminal. Move the GGUF somewhere permanent:

```bash
mkdir -p ~/ollama-models
mv ~/Downloads/my-custom-model-unsloth.Q4_K_M.gguf ~/ollama-models/
```

Create a Modelfile:

```bash
cat > ~/ollama-models/Modelfile << 'EOF'
FROM ~/ollama-models/my-custom-model-unsloth.Q4_K_M.gguf

PARAMETER temperature 0.7
PARAMETER top_p 0.9

SYSTEM "You are a helpful assistant fine-tuned for my specific use case."
EOF
```

Build the Ollama model:

```bash
ollama create my-custom-model -f ~/ollama-models/Modelfile
```

Test:

```bash
ollama run my-custom-model "Hello, are you working?"
```

Checkpoint: you see a response from your custom model.

---

## Phase 9: Use it in LearnAI (5 minutes)

Open LearnAI at `http://localhost:9180`.

1. Click the model dropdown in the chat header
2. Find `my-custom-model` in the list (it appears automatically — no config change needed)
3. Start a new chat with your model

**Bonus — create a Profile:**

1. Go to `#/profiles`
2. New Profile:
   - Name: "My Fine-Tuned Assistant"
   - Base model: `my-custom-model`
   - System prompt: describe what you trained it for
   - Temperature: 0.7
3. Save

Now when you start a chat, you can pick that profile and get your fine-tuned model with the right defaults locked in.

Checkpoint: you are chatting with a model YOU trained, running on YOUR machine, inside a platform YOU can modify.

---

## What just happened

You took a public base model, taught it something specific to you, converted it to run locally, and plugged it into an interface where you can keep building with it. That's the full fine-tuning loop.

Three things to sit with:
1. **No one else saw your data.** The training ran in your Colab notebook. The model runs on your laptop. Nothing was sent to any service you do not control.
2. **The skill transfers.** Every future fine-tune uses the same 9 phases with different datasets and different base models.
3. **This is the next wave.** Running other people's models is table stakes. Fine-tuning your own unlocks the value only you can provide.

---

## Homework (optional, takes a week)

1. Build a real dataset for a real use case (200+ examples, high quality)
2. Fine-tune a slightly bigger base model (8B or 13B if your hardware allows)
3. Compare outputs: your fine-tuned model vs the base model on the same prompts
4. Share your learnings: what worked, what didn't, what you'd try next

---

## Troubleshooting

**"CUDA out of memory" during training**
- Pick a smaller base model (2B or 4B)
- Reduce `max_seq_length` to 1024
- Use Colab Pro for an A100

**"Model not showing in Ollama"**
- Run `ollama list` — is it there?
- Check the Modelfile `FROM` path is absolute and points to the actual `.gguf` file
- Try `ollama create` again

**"Fine-tuned model gives worse answers than base"**
- Your dataset might be too small, too inconsistent, or too narrow
- Try fewer epochs (overfitting)
- Add more diverse examples
- Check your output examples are actually high quality — the model copies what you give it

**"Training loss is flat, not going down"**
- Your dataset might be too small (under 30 examples)
- Your examples might be inconsistent
- Check the format is correct

---

## Resources

- [unsloth.ai](https://unsloth.ai) — starter notebooks, official docs
- [Hugging Face model hub](https://huggingface.co/unsloth) — pre-quantized Unsloth models
- [Ollama import docs](https://ollama.com/blog/import) — more on Modelfiles and GGUF
- LearnAI repo issues — ask questions: https://github.com/w4ester/learnai/issues

---

## Facilitator notes (if you are teaching this)

- **Before the workshop:** have every attendee confirm LearnAI is running locally. Debugging Ollama/Docker during a fine-tuning workshop is a disaster.
- **Have a fallback dataset ready.** If someone shows up without data, hand them a prepared `my_data.json` so they don't block the whole session.
- **Run training on YOUR machine too.** When someone's training stalls, you want to compare your output to theirs to debug.
- **The "test in notebook before export" step is critical.** Do not let anyone skip Phase 6. Catching a bad model before a 5-minute export is much better than after.
- **End on the Phase 9 demo.** The moment when "my custom model shows up in LearnAI" is the payoff. Land it well.
