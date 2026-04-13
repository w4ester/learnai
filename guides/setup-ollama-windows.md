# Ollama Setup Guide for Windows (Coach Script)

This is a step by step teaching script for helping someone install Ollama on Windows. Follow the stages in order. Give ONE stage at a time. Wait for the user to confirm success before moving to the next stage. NEVER hardcode specific model names. Always point users to ollama.com/library to pick their own.

## Who this is for
A Windows user who wants to run AI models locally. Works on Windows 10 and 11. An NVIDIA GPU with CUDA makes models much faster but is not required.

## What they need before starting
- Windows 10 version 22H2 or Windows 11
- At least 8 GB of RAM (16 GB or more recommended)
- About 10 GB of free disk space for a typical model
- Administrator access (for the installer)
- Optional but great: an NVIDIA GPU with up to date drivers

---

## STAGE 1: Choose an install method

Ask the user: "How would you like to install Ollama? You have two options:

**Option A: Download the Windows installer from ollama.com** (easiest, recommended for most people)
- You go to ollama.com, click Download, run OllamaSetup.exe
- Ollama installs as a Windows service and adds a system tray icon
- This is what we recommend for nearly everyone

**Option B: Install inside WSL2 (Windows Subsystem for Linux)** (for advanced users who already use WSL)
- You install Ollama inside an Ubuntu or other Linux distribution running under Windows
- More flexible but requires you to know your way around WSL
- Only pick this if you already use WSL daily

Which would you like to try?"

Recommend Option A unless they explicitly know they want WSL.

---

## STAGE 2A: Install via ollama.com Windows installer

Walk them through this:

1. "Open your web browser and go to ollama.com"
2. "Click the Download button. The site will detect Windows and offer the Windows installer."
3. "Click Download for Windows. A file called OllamaSetup.exe will download to your Downloads folder."
4. "Open your Downloads folder. Double click OllamaSetup.exe to run the installer."
5. "Windows may show a SmartScreen warning because the file was downloaded from the internet. Click More info, then Run anyway. This is normal for apps not from the Microsoft Store."
6. "The installer is simple. Click Install. It finishes in under a minute."
7. "After install, Ollama runs automatically as a Windows service. You should see a llama icon in your system tray in the bottom right corner of your screen (you may need to click the ^ arrow to see hidden icons)."

Wait for them to confirm they see the llama icon in the system tray.

If they do not see it, ask them to check the hidden icons area (the little ^ arrow in the taskbar). If still missing, have them open Services (Windows key, type Services, press Enter) and find "Ollama" in the list. It should say Running. If not, right click and choose Start.

Once they confirm, move to Stage 3.

---

## STAGE 2B: Install inside WSL2

Only do this if they picked Option B. Otherwise skip to Stage 3.

Check if they have WSL2. Open PowerShell and run:
```
wsl --status
```

If it says WSL is not installed, they need to install it first:
```
wsl --install
```
This downloads Ubuntu by default and requires a restart.

Once WSL is ready and they are inside their Linux distribution (type `wsl` in PowerShell to enter it), install Ollama using the official Linux installer:
```
curl -fsSL https://ollama.com/install.sh | sh
```

This installs Ollama inside WSL. It will run as a systemd service if WSL has systemd enabled (Ubuntu 22.04+ does by default).

Start Ollama:
```
sudo systemctl start ollama
```

Verify:
```
curl http://localhost:11434
```

Note: When Ollama runs inside WSL, Windows apps and containers have different ways to reach it. This is more complicated than Option A. Only continue with Option B if you are comfortable with WSL networking.

Then move to Stage 3.

---

## STAGE 3: Verify Ollama is running and reachable

Open PowerShell (press Windows key, type "powershell", press Enter).

First check the Ollama CLI works:
```
ollama --version
```

They should see something like `ollama version 0.X.Y`. If they see "not recognized as a command", have them close PowerShell and open a new window. Windows sometimes needs a fresh shell to pick up newly installed commands. If still broken after a new window, they may need to restart their computer.

Then check the service is responding:
```
curl http://localhost:11434
```

They should see: `Ollama is running`

If they see a connection error:
- **Option A users:** Check the system tray for the llama icon. If missing, look in Services (Windows key, type Services) for Ollama and start it.
- **Option B users:** Start it inside WSL with `sudo systemctl start ollama`

Do not move on until they see "Ollama is running". Celebrate this moment: "Ollama is alive on your Windows machine."

---

## STAGE 4: Choose a model to download

Do NOT pick a model for them. Walk them through choosing one based on their hardware.

Ask: "How much RAM does your PC have? And do you have an NVIDIA GPU?"

They can check RAM by pressing Windows key, typing "about", and clicking About your PC. The Installed RAM line shows it.

For the GPU, have them open Device Manager (Windows key + X, then M) and expand Display adapters. If they see NVIDIA listed there, they have an NVIDIA GPU and Ollama will use it automatically for much faster inference.

Guide them based on their RAM:

- **8 GB RAM:** Stick with small models around 3B to 4B parameters. Fast and light.
- **16 GB RAM:** You can comfortably run 7B to 13B parameter models.
- **32 GB RAM:** You can run 20B to 30B parameter models.
- **64 GB RAM or more:** You can run the largest models.
- **With NVIDIA GPU:** Check your VRAM in Device Manager or Task Manager (Performance tab > GPU). 8 GB VRAM = 7B models fit. 12 GB VRAM = 13B models. 24 GB VRAM = 30B+ models.

Then tell them: "Open ollama.com/library in your browser. Browse the full catalog. Pick a model that looks interesting and fits your hardware. Click on it to see sizes and tags. Copy the exact model name including the tag (the part after the colon). It will look like `modelname:tag`."

Ask them to tell you the exact name before moving to Stage 5. Do not suggest a specific model by name.

---

## STAGE 5: Pull the model

In PowerShell, have them run (replacing THEIR_MODEL_NAME with the exact name from ollama.com/library):

```
ollama pull THEIR_MODEL_NAME
```

Explain: "This downloads the model from the Ollama registry to your PC. You only do this once per model. Future runs are fast."

Progress bar will appear. Wait for them to confirm it finished.

---

## STAGE 6: Test the model directly in PowerShell

```
ollama run THEIR_MODEL_NAME
```

They will see:
```
>>> Send a message (/? for help)
```

Tell them to type "hello" and press Enter. The model should respond.

To exit, type:
```
/bye
```

or press Ctrl+D.

**Celebrate.** "You just ran a real AI model entirely on your own Windows PC. No API key, no cloud, no data leaving your machine."

If the model is extremely slow, it is too big. Go back to Stage 4 and pick a smaller one.

---

## STAGE 7: Manage their models

```
ollama list
```

Shows all downloaded models with sizes.

Useful commands:
- Remove a model: `ollama rm THEIR_MODEL_NAME`
- Pull a different model: `ollama pull OTHER_MODEL_NAME`
- See models running in memory: `ollama ps`
- Stop a running model: `ollama stop THEIR_MODEL_NAME`

---

## STAGE 8: Connect Ollama to LearnAI (optional)

Only move to this stage if they asked to connect Ollama to LearnAI.

Prerequisites:

1. **WSL2:** Docker Desktop for Windows requires WSL2. Open PowerShell as Administrator and run `wsl --status`. If WSL is not installed, run `wsl --install` and restart the computer.

2. **Docker Desktop:** Download from docker.com. Run the installer. Make sure "Use WSL 2 based engine" is checked. Restart if prompted. Open Docker Desktop and wait for "Engine running" in the bottom status bar.

3. **Git:** Download from git-scm.com. Accept defaults. Verify with `git --version` in PowerShell.

Once they have all three, open PowerShell (not as admin) and run:

```
git clone https://github.com/w4ester/learnai.git
cd learnai
copy .env.example .env
docker compose up --build
```

The first build takes a few minutes. When it finishes, open http://localhost:9180 in a browser.

**Important Windows networking note:** If models do not show in the dropdown, edit the .env file with Notepad and change this line:

From:
```
OLLAMA_BASE_URL=http://host.docker.internal:11434
```

To:
```
OLLAMA_BASE_URL=http://localhost:11434
```

Explain why: Windows Docker sometimes cannot resolve `host.docker.internal` to the host machine the same way Mac can. Using `localhost` inside the container points back through Docker's network to the host.

Save the file. Then in PowerShell:
```
docker compose restart api
```

Reload http://localhost:9180 in your browser. The models should now appear.

---

## Troubleshooting cheat sheet

### "ollama is not recognized as a command" (Option A)
Close PowerShell completely. Open a new PowerShell window. Try again. If still broken, restart the computer. Windows sometimes needs a restart to pick up new PATH entries after an installer runs.

### System tray icon missing (Option A)
Check the hidden icons (^ arrow in the taskbar). If still missing, open Services (Windows key, type Services). Find Ollama in the list. Right click, Start. Set Startup type to Automatic if it is not already.

### "Could not connect to ollama server" or curl fails
The service is not running.
- Option A: Open Services, find Ollama, right click Start.
- Option B: `sudo systemctl start ollama` inside WSL.

### WSL2 install fails
Virtualization may not be enabled in BIOS/UEFI. Restart the computer, enter BIOS (usually F2 or Delete during boot), find "Virtualization Technology", "SVM Mode", or "Intel VT-x", and enable it. Save and restart.

### Docker Desktop will not start
Verify WSL2 is working: `wsl --status` in PowerShell. If not, run `wsl --install` as admin. After restart, try Docker Desktop again.

### Model runs very slowly on CPU
If they have an NVIDIA GPU, make sure the latest NVIDIA drivers are installed from nvidia.com. Ollama should pick up the GPU automatically. Without a GPU, stick to smaller models (under 8B parameters).

### Docker cannot reach Ollama
Try both values for OLLAMA_BASE_URL in .env: `http://host.docker.internal:11434` or `http://localhost:11434`. One will work depending on Docker network mode. Also verify Ollama is listening on all interfaces, not just localhost:
```
netstat -ano | findstr 11434
```
You want to see it listening on `0.0.0.0:11434`. If it is only on `127.0.0.1:11434`, set environment variable `OLLAMA_HOST=0.0.0.0` in Windows environment variables, then restart Ollama.

### Out of memory errors
Model is too big for available RAM or VRAM. Pick a smaller model.

### Mac commands in a Windows guide (user confusion)
If they copy a Mac command like `brew install ollama` into PowerShell, it will not work. Windows does not have brew. They should only follow the Windows steps in this guide.

---

## Managing the Ollama service

**Option A users:**
- Start: Services panel, find Ollama, Start
- Stop: Services panel, find Ollama, Stop
- Update: Download the latest installer from ollama.com and run it. It updates in place.

**Option B users (WSL):**
- Start: `sudo systemctl start ollama` inside WSL
- Stop: `sudo systemctl stop ollama`
- Update: `curl -fsSL https://ollama.com/install.sh | sh` inside WSL

---

## Coach rules (for the AI following this script)

1. **NEVER tell the user to run a specific named model.** Always guide them to ollama.com/library. Never say "try llama3" or "install gemma" by name.
2. **Give ONE stage at a time.** Wait for confirmation before moving on.
3. **Ask which install method first.** Stage 1 is a branch. Recommend Option A (the installer) for nearly everyone.
4. When a user reports an error, ask for the exact message and match to the troubleshooting cheat sheet.
5. **Explain the WHY** when it helps learning.
6. **Celebrate small wins.** First "Ollama is running" and first model response are real milestones.
7. If stuck or frustrated, slow down and break a stage into smaller pieces.
8. If asked something not in this guide, suggest the official Ollama docs at ollama.com or github.com/ollama/ollama/issues.

---


