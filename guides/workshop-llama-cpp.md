# Workshop: Build llama.cpp and Run Your First Model

**Duration:** 60 minutes
**Audience:** Anyone comfortable opening a terminal who wants to understand what's under the hood of Ollama
**Outcome:** llama.cpp compiled from source, a GGUF model running locally via the CLI, the same model served over HTTP, and connected to LearnAI

> You will build the inference engine that powers Ollama, KoboldCpp, LM Studio, and dozens of other tools. After this workshop, you know what is happening underneath every "run AI locally" product, and you can tune it yourself.

---

## Before you start (5 minutes)

Check all of these are true before proceeding:

- [ ] A terminal you are comfortable opening (Terminal on Mac, PowerShell or WSL on Windows, any shell on Linux)
- [ ] `git --version` returns a version number
- [ ] **Mac:** `clang --version` works (Xcode Command Line Tools installed — `xcode-select --install` if not)
- [ ] **Linux:** `gcc --version` and `cmake --version` both work (install with `sudo apt install build-essential cmake` on Ubuntu/Debian)
- [ ] **Windows:** CMake installed AND you have either Visual Studio 2022 Community with "Desktop C++" workload OR you are in WSL2 (WSL2 is easier — treat it as Linux from here on)
- [ ] 10 GB free disk space (4 GB for the build, 4-6 GB for model downloads, rest for breathing room)

If any of these fails, stop and fix it before moving on. Building from source with a broken toolchain wastes 45 minutes.

### Hardware path

Pick the path that matches your machine:

| Path | Build flag | Notes |
|---|---|---|
| **Mac (Apple Silicon M1/M2/M3/M4)** | `-DGGML_METAL=ON` | Uses Apple's Metal GPU. Fastest path on Mac. |
| **Mac (Intel)** | `-DGGML_ACCELERATE=ON` | Uses Apple Accelerate framework. CPU only — expect slower inference. |
| **Linux (NVIDIA GPU)** | `-DGGML_CUDA=ON` | Requires CUDA Toolkit installed. Fastest path on Linux. |
| **Linux (CPU only)** | `-DGGML_OPENBLAS=ON` | CPU inference with BLAS acceleration. Slower but works everywhere. |
| **Windows WSL2 (treat as Linux)** | Match Linux above | NVIDIA GPU on Windows works if CUDA is set up in WSL. |

Remember your flag — you will use it in Phase 2.

---

## Phase 1: Clone the repo (2 minutes)

```bash
cd ~
git clone https://github.com/ggml-org/llama.cpp.git
cd llama.cpp
```

The repo is ~500 MB with all its git history. First clone takes a minute or two.

Checkpoint: `ls` shows files including `CMakeLists.txt`, `README.md`, `src/`, `tools/`, `examples/`.

---

## Phase 2: Build it (10-15 minutes)

This is the phase that can go wrong. Do not skip the hardware flag for your machine.

### The universal build pattern

```bash
# From inside the llama.cpp directory
cmake -B build <YOUR_HARDWARE_FLAG>
cmake --build build --config Release -j
```

Replace `<YOUR_HARDWARE_FLAG>` with the flag from the table above.

### Full examples

**Mac (Apple Silicon):**
```bash
cmake -B build -DGGML_METAL=ON
cmake --build build --config Release -j
```

**Linux (NVIDIA):**
```bash
cmake -B build -DGGML_CUDA=ON
cmake --build build --config Release -j
```

**Linux (CPU only):**
```bash
cmake -B build -DGGML_OPENBLAS=ON
cmake --build build --config Release -j
```

The `-j` flag at the end tells `make` to use all CPU cores. Build time depends on your machine: 5-15 minutes typically.

You will see a LOT of compiler output. Warnings are fine. **Errors halt the build.**

Checkpoint: `ls build/bin/` shows binaries including `llama-cli` and `llama-server`.

### If the build fails

Read the FIRST error, not the last one. Build systems cascade errors downstream. The root cause is near the top of the error output.

Common causes:
- **"cmake: command not found"** → install cmake first
- **"Metal framework not found"** (Mac) → confirm Xcode Command Line Tools are fully installed: `xcode-select --install`
- **"CUDA compiler not found"** (Linux) → CUDA Toolkit isn't installed or isn't in PATH. Run `nvcc --version` to check.
- **Out of memory during build** → reduce parallelism: `cmake --build build --config Release -j 2` instead of `-j`

Do not proceed until the build succeeds.

---

## Phase 3: Download a model (5 minutes)

llama.cpp runs GGUF files. You need one. The easiest source is Hugging Face.

### Option A: Use huggingface-cli (if you have it)

```bash
pip install huggingface_hub
huggingface-cli download unsloth/gemma-3-4b-it-GGUF gemma-3-4b-it-Q4_K_M.gguf --local-dir ./models
```

### Option B: Direct download with curl

```bash
mkdir -p models
curl -L -o models/gemma-3-4b-it-Q4_K_M.gguf \
  https://huggingface.co/unsloth/gemma-3-4b-it-GGUF/resolve/main/gemma-3-4b-it-Q4_K_M.gguf
```

This is a ~2.5 GB download. Time depends on your connection.

Checkpoint: `ls -lh models/` shows the `.gguf` file at ~2.5 GB.

### Why this model?

You picked a 4B (4 billion parameter) model quantized to Q4_K_M. Breakdown:
- **Gemma 3** — Google's open-weight model, strong quality for its size
- **4B parameters** — small enough to run fast on any modern CPU or GPU
- **Q4_K_M quantization** — weights are compressed to ~4.5 bits each. About 75% size reduction vs full precision with minimal quality loss.
- **instruction-tuned (`-it`)** — already trained to follow instructions (vs a base model that just continues text)

---

## Phase 4: Run your first inference (5 minutes)

```bash
./build/bin/llama-cli -m models/gemma-3-4b-it-Q4_K_M.gguf -p "Explain how photosynthesis works in 3 sentences."
```

What you will see:
1. Model loads (a few seconds — you'll see memory allocation messages)
2. Your prompt echoes back
3. The model generates a response token by token
4. Stats print at the end: tokens per second, memory used, total time

Checkpoint: you get a coherent 3-sentence response about photosynthesis.

### If it fails

- **"failed to load model"** → check the `.gguf` file path is correct
- **Gibberish output** → the model file might be corrupted. Re-download.
- **Out of memory** → pick a smaller quantization (Q3 or Q2) or a smaller model
- **Super slow (< 5 tokens/sec)** → you probably built without GPU acceleration. Re-check your build flag and rebuild.

---

## Phase 5: Play with sampling parameters (10 minutes)

Same model, different parameters, wildly different outputs. This phase is where most learners have their first "oh, that's what temperature actually does" moment.

### Try these variations

**Deterministic (same answer every time):**
```bash
./build/bin/llama-cli -m models/gemma-3-4b-it-Q4_K_M.gguf \
  -p "Write one sentence about the ocean." \
  --temp 0 \
  -n 50
```

Run it twice. Same output. That is what temperature 0 does — pick the single most probable next token every time.

**Creative (varied each time):**
```bash
./build/bin/llama-cli -m models/gemma-3-4b-it-Q4_K_M.gguf \
  -p "Write one sentence about the ocean." \
  --temp 1.2 \
  -n 50
```

Run it three times. Three different sentences. That's what high temperature does — sample more broadly from the probability distribution.

**Focused (only high-probability tokens):**
```bash
./build/bin/llama-cli -m models/gemma-3-4b-it-Q4_K_M.gguf \
  -p "List 3 flavors of ice cream." \
  --top-k 10 \
  -n 50
```

`--top-k 10` means only consider the top 10 most probable tokens at each step.

### Parameter cheat sheet

| Flag | What it does | Safe range |
|---|---|---|
| `--temp <N>` | Randomness. 0 = deterministic, 1 = baseline, 2 = chaos | 0.1 – 1.3 |
| `--top-k <N>` | Only consider top N tokens | 10 – 50 |
| `--top-p <N>` | Only consider tokens until cumulative probability reaches N | 0.7 – 0.95 |
| `--repeat-penalty <N>` | Penalize tokens that already appeared | 1.0 – 1.2 |
| `-n <N>` | Max tokens to generate | 50 – 2000 |
| `--ctx-size <N>` | Context window size | 2048 – 32768 |

Checkpoint: you have experimented with at least 3 different parameter combinations and seen how the output changes.

---

## Phase 6: Run as an HTTP server (5 minutes)

Now make it serve requests instead of running one-shot.

```bash
./build/bin/llama-server -m models/gemma-3-4b-it-Q4_K_M.gguf --port 8080 --host 127.0.0.1
```

The server starts and prints:
```
main: server is listening on http://127.0.0.1:8080 - starting the main loop
```

Leave this terminal running. Open a SECOND terminal for the next phase.

Checkpoint: the server shows "listening on http://127.0.0.1:8080" and doesn't crash.

---

## Phase 7: Call the API with curl (5 minutes)

llama.cpp's server implements the OpenAI-compatible API. Any tool that speaks OpenAI can talk to it.

In your second terminal:

```bash
curl http://127.0.0.1:8080/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "messages": [
      {"role": "user", "content": "What is 17 * 23?"}
    ],
    "temperature": 0.7,
    "max_tokens": 100
  }'
```

You get back a JSON response with the model's answer. The format exactly matches OpenAI's Chat Completions API.

Try a few more:

```bash
curl http://127.0.0.1:8080/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "messages": [
      {"role": "system", "content": "You are a pirate. Respond in pirate voice."},
      {"role": "user", "content": "Tell me about the weather today."}
    ]
  }'
```

Checkpoint: you can send requests and get responses back from your local llama.cpp server.

### Why this matters

Because the server speaks OpenAI's API, you can point ANY OpenAI-compatible client at `http://127.0.0.1:8080/v1` and it works. That includes: LearnAI, Continue.dev, Cursor, countless Python scripts, and hundreds of other tools. You just built a private, local OpenAI replacement.

---

## Phase 8: Connect to LearnAI (5 minutes)

Close the loop with your existing platform.

### Stop your current LearnAI containers if running:

```bash
cd ~/learnai
docker compose down
```

### Edit `.env`:

```bash
# Change these two lines:
MODEL_PROVIDER=openai
OLLAMA_BASE_URL=http://host.docker.internal:8080/v1

# Add a fake API key (llama.cpp ignores it, but the client library requires one):
OPENAI_API_KEY=not-needed
```

**Linux users:** `host.docker.internal` will not resolve from inside Docker. Use `http://172.17.0.1:8080/v1` instead.

### Restart LearnAI:

```bash
docker compose up -d
```

### Confirm llama-server is still running in its terminal

Scroll to that terminal. You should still see it waiting for requests.

### Open LearnAI:

Open `http://localhost:9180` in your browser. The model dropdown should now list models served by llama-server.

Start a chat. Send a message. Watch the llama-server terminal — you will see the request come in and be processed.

Checkpoint: you are chatting inside LearnAI, but the model is served by llama.cpp directly. Ollama is not involved.

---

## What just happened

You built an inference engine from source, downloaded a model, ran it three different ways (CLI, parameterized, server), and pointed your existing platform at the new backend.

Three things to sit with:

1. **You can see the whole stack now.** Before this workshop, "running AI locally" was a black box called Ollama. Now you know Ollama is llama.cpp with a wrapper. The layers are visible.
2. **GGUF is a universal format.** The file you just downloaded works in llama.cpp, Ollama, LM Studio, KoboldCpp, and every other GGUF-compatible runner. Swap the engine, keep the model.
3. **OpenAI compatibility is everywhere.** The server you just ran speaks the same protocol as OpenAI's cloud API. That means thousands of existing tools work against it without modification. This is the quiet standard that makes local AI practical.

---

## Homework (optional)

1. Build a second time with different flags and compare inference speed
2. Download a bigger model (7B or 13B) and compare quality vs speed vs memory usage
3. Try different quantizations (Q3, Q5, Q8) on the same model and compare
4. Put llama-server behind a reverse proxy (nginx or Caddy) with basic auth, making it reachable to other devices on your LAN
5. Script a comparison: same prompt, same model, five temperature values, record outputs side-by-side

---

## Troubleshooting

**"command not found: cmake"**
- Mac: `brew install cmake`
- Linux: `sudo apt install cmake` or equivalent
- Windows: download from cmake.org

**"Metal framework not found" (Mac)**
- Run `xcode-select --install` to install Command Line Tools
- If already installed, try `sudo xcode-select --reset` then reinstall

**"CUDA compiler nvcc not found" (Linux)**
- Install NVIDIA CUDA Toolkit from developer.nvidia.com
- After install: `export PATH=/usr/local/cuda/bin:$PATH`

**Inference is very slow (< 5 tokens/sec on modern hardware)**
- You probably built without GPU acceleration
- Check the build output near the top for lines mentioning Metal, CUDA, or OpenBLAS
- If absent, rebuild from a clean state: `rm -rf build && cmake -B build <YOUR_FLAG> && cmake --build build --config Release -j`

**"failed to load model"**
- Check the file path is correct
- Confirm the file is a `.gguf` (not `.gguf.json` or similar)
- Check file isn't zero bytes: `ls -lh models/`

**Server port already in use**
- Something else is on port 8080. Pick another: `--port 8181`
- Or find what's using 8080: `lsof -i :8080` (Mac/Linux)

**LearnAI can't see the server**
- From inside a Docker container, `localhost` means the container, not your host
- Mac/Windows: use `host.docker.internal`
- Linux: use `172.17.0.1` (the Docker bridge IP)
- Test from inside the API container: `docker compose exec api curl http://host.docker.internal:8080/v1/models`

---

## Resources

- [llama.cpp on GitHub](https://github.com/ggml-org/llama.cpp) — source, docs, issues
- [Hugging Face GGUF models](https://huggingface.co/models?library=gguf) — browse thousands of GGUF model files
- [llama-server API docs](https://github.com/ggml-org/llama.cpp/blob/master/tools/server/README.md) — full reference for the HTTP endpoints
- [GGUF format spec](https://github.com/ggerganov/ggml/blob/master/docs/gguf.md) — what's actually in the file
- LearnAI repo issues — ask questions: https://github.com/w4ester/learnai/issues

---

## Facilitator notes (if you are teaching this)

- **Build phase is where people get stuck.** Budget 15 minutes for it even though it should take 5-10. Have the tool installation commands ready for all three OSes as a handout.
- **Hardware flags matter more than the rest of the workshop combined.** Someone who builds without `-DGGML_METAL=ON` on a Mac will think llama.cpp is broken because inference is 20x slower than expected. Call this out at the top.
- **Phase 5 (sampling parameters) is the real learning moment.** Most attendees have used "temperature" without actually feeling what it does. Make them run the temp=0 example twice to see identical output. That's the "oh" moment.
- **Keep llama-server running for Phase 8.** Attendees who kill it between phases have to restart. Tell them twice to leave it running.
- **The LearnAI connection at the end is the payoff.** After an hour of terminal work, seeing their familiar chat UI now powered by the engine they just built closes a satisfying loop. Don't skip it.
- **If you have time, show `htop` or Activity Monitor during inference** so they can see CPU vs GPU usage and understand what the hardware flag actually bought them.
