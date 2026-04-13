# Ollama Setup Guide for Linux (Coach Script)

This is a step by step teaching script for helping someone install Ollama on Linux. Follow the stages in order. Give ONE stage at a time. Wait for the user to confirm success before moving to the next stage. NEVER hardcode specific model names. Always point users to ollama.com/library to pick their own.

## Who this is for
A Linux user who wants to run AI models locally. Works on most distributions (Ubuntu, Debian, Fedora, Arch, openSUSE, and more). A dedicated GPU (NVIDIA or AMD) makes models much faster but is not required.

## What they need before starting
- A modern Linux distribution (Ubuntu 22.04+, Debian 12+, Fedora 38+, Arch, or similar)
- At least 8 GB of RAM (16 GB or more recommended)
- About 10 GB of free disk space for a typical model
- sudo access (admin permissions)
- curl and bash (both are standard on every distro)
- Optional: NVIDIA GPU with drivers, or AMD GPU with ROCm

---

## STAGE 1: Choose an install method

Ask the user: "How would you like to install Ollama? You have two options:

**Option A: Use the official install script from ollama.com** (easiest, recommended)
- You run one curl command that downloads and runs the official installer
- Works on most distributions automatically
- Detects your GPU and installs drivers if needed
- Sets up a systemd service so Ollama starts at boot
- This is what we recommend for nearly everyone

**Option B: Manual install from a downloaded binary** (for people who avoid running scripts from the internet)
- You download the Ollama binary directly from github.com/ollama/ollama/releases
- You manually put it in /usr/local/bin/
- You manually create a systemd service file
- More work but gives you full visibility into what gets installed

Which would you like to try?"

Recommend Option A unless they have a specific reason to avoid it.

---

## STAGE 2A: Install via ollama.com install script

Open a terminal and run:

```
curl -fsSL https://ollama.com/install.sh | sh
```

Explain what this does:
- `curl -fsSL` fetches the install script from ollama.com
- `| sh` pipes it to the shell to run
- The script detects your distribution, architecture, and GPU
- It installs the `ollama` binary to `/usr/local/bin/ollama`
- It creates a systemd service named `ollama.service`
- It installs GPU drivers if you have an NVIDIA card without CUDA already set up
- It starts the service automatically

This takes anywhere from 30 seconds to a few minutes depending on your connection and whether GPU drivers need to install.

When it finishes, verify the CLI works:
```
ollama --version
```

They should see a version number.

Check the service is running:
```
systemctl status ollama
```

They should see `active (running)` in green.

Then check it is reachable:
```
curl http://localhost:11434
```

They should see: `Ollama is running`

If any of these fail, jump to the troubleshooting cheat sheet. Do not move on until they see "Ollama is running".

**Celebrate:** "You just got Ollama running as a system service on Linux. It will start automatically every time you boot."

Skip to Stage 3.

---

## STAGE 2B: Manual install from binary

Only do this if they chose Option B. Otherwise skip to Stage 3.

1. Go to github.com/ollama/ollama/releases in a browser.
2. Find the latest release and download the binary matching your architecture:
   - `ollama-linux-amd64` for most x86_64 Linux machines
   - `ollama-linux-arm64` for ARM64 (like Raspberry Pi 64-bit or a Linux ARM server)
3. Move the binary to /usr/local/bin and make it executable:

```
sudo mv ~/Downloads/ollama-linux-amd64 /usr/local/bin/ollama
sudo chmod +x /usr/local/bin/ollama
```

4. Create an ollama user:
```
sudo useradd -r -s /bin/false -m -d /usr/share/ollama ollama
```

5. Create a systemd service file:
```
sudo tee /etc/systemd/system/ollama.service > /dev/null <<'EOF'
[Unit]
Description=Ollama Service
After=network-online.target

[Service]
ExecStart=/usr/local/bin/ollama serve
User=ollama
Group=ollama
Restart=always
RestartSec=3
Environment="PATH=$PATH"

[Install]
WantedBy=default.target
EOF
```

6. Reload systemd and start Ollama:
```
sudo systemctl daemon-reload
sudo systemctl enable ollama
sudo systemctl start ollama
```

7. Verify:
```
systemctl status ollama
curl http://localhost:11434
```

They should see "Ollama is running". Then move to Stage 3.

---

## STAGE 3: Verify Ollama is running and reachable

If they made it through Stage 2A or 2B successfully, verify one more time:

```
curl http://localhost:11434
```

They should see: `Ollama is running`

Also run:
```
ollama --version
```

To see the installed version.

If the curl command fails, have them check the service status:
```
systemctl status ollama
```

Look at the output. If it says "failed", have them run:
```
journalctl -u ollama -n 50
```

This shows the last 50 lines of the service logs. Ask them to paste any red error lines.

Do not move on until "Ollama is running" appears.

---

## STAGE 4: Choose a model to download

Do NOT pick a model for them. Walk them through choosing based on their hardware.

Ask: "How much RAM does your machine have? And do you have a dedicated GPU?"

They can check RAM with:
```
free -h
```
Look at the "Mem:" row, "total" column.

For GPU, run:
```
lspci | grep -i vga
```
or
```
nvidia-smi
```
If nvidia-smi prints a table with GPU info, they have an NVIDIA GPU and Ollama will use it automatically.

Guide them based on their RAM:

- **8 GB RAM:** Stick with small models around 3B to 4B parameters.
- **16 GB RAM:** You can comfortably run 7B to 13B parameter models.
- **32 GB RAM:** You can run 20B to 30B parameter models.
- **64 GB RAM or more:** You can run the largest models.
- **With NVIDIA GPU:** Use nvidia-smi to check VRAM. 8 GB VRAM fits 7B comfortably. 12 GB VRAM fits 13B. 24 GB VRAM fits 30B+.

Then tell them: "Open ollama.com/library in your browser. Browse the catalog. Pick a model, click on it to see sizes and tags, and copy the exact model name including the tag. It will look like `modelname:tag`."

Ask them to tell you the exact name before moving to Stage 5. Never suggest a specific model by name.

---

## STAGE 5: Pull the model

```
ollama pull THEIR_MODEL_NAME
```

Replace with the exact name they copied from ollama.com/library.

Explain: "This downloads the model from Ollama's registry to your machine. Only done once. Later runs are fast."

Wait for download to finish.

---

## STAGE 6: Test the model directly in the terminal

```
ollama run THEIR_MODEL_NAME
```

They see:
```
>>> Send a message (/? for help)
```

Have them type "hello" and press Enter. The model responds.

Exit with:
```
/bye
```

**Celebrate:** "You just ran a real AI model entirely on your own Linux machine. No cloud, no API key, your data stays on your box."

---

## STAGE 7: Manage their models

```
ollama list
```

Shows all downloaded models.

Commands:
- Remove: `ollama rm THEIR_MODEL_NAME`
- Pull another: `ollama pull OTHER_MODEL_NAME`
- See running models: `ollama ps`
- Stop a model: `ollama stop THEIR_MODEL_NAME`

---

## STAGE 8: Connect Ollama to LearnAI (optional)

Only continue if they asked to connect to LearnAI.

**Install Docker and git:**

On Debian/Ubuntu:
```
sudo apt update
sudo apt install docker.io docker-compose-plugin git
sudo systemctl enable --now docker
sudo usermod -aG docker $USER
```

On Fedora:
```
sudo dnf install docker docker-compose git
sudo systemctl enable --now docker
sudo usermod -aG docker $USER
```

On Arch:
```
sudo pacman -S docker docker-compose git
sudo systemctl enable --now docker
sudo usermod -aG docker $USER
```

After the usermod command, they need to log out and log back in (or run `newgrp docker` in the current shell) so the group change takes effect.

Verify:
```
docker --version
docker compose version
```

**Clone and start LearnAI:**
```
git clone https://github.com/w4ester/learnai.git
cd learnai
cp .env.example .env
```

**Critical Linux step:** Docker containers on Linux cannot use `host.docker.internal` by default. Edit the .env file and change the Ollama URL:

```
OLLAMA_BASE_URL=http://172.17.0.1:11434
```

Explain why: `172.17.0.1` is the default Docker bridge gateway on Linux. It points back to your host machine where Ollama is running. This is the equivalent of `host.docker.internal` on Mac.

Start it:
```
docker compose up --build
```

Open http://localhost:9180 in a browser.

If 172.17.0.1 does not work, they can try adding `network_mode: host` to the api service in docker-compose.yml which puts the container directly on the host network. Then `http://localhost:11434` works.

---

## Troubleshooting cheat sheet

### "ollama: command not found"
The install script may have put the binary in /usr/local/bin but that is not in your PATH. Fix by adding it:
```
export PATH=$PATH:/usr/local/bin
```
Add that line to `~/.bashrc` or `~/.zshrc` to make it permanent.

### systemctl says "ollama.service not found"
The service unit was not created. Try running it in the foreground to verify the binary works:
```
ollama serve
```
If that works, the install script did not create the systemd service. Manually create it using the steps in Stage 2B.

### GPU not detected
Run:
```
nvidia-smi
```
If nvidia-smi fails or is not found, the NVIDIA drivers are not installed properly. Install them via your distribution's package manager first, then reboot, then reinstall Ollama so its installer detects the GPU.

If nvidia-smi works but Ollama is not using the GPU, check Ollama logs:
```
journalctl -u ollama -f
```
You should see "found X NVIDIA GPU(s)" at startup. If not, Ollama could not find the CUDA libraries.

### Docker cannot connect to Ollama on host
Try these OLLAMA_BASE_URL values in order:
1. `http://172.17.0.1:11434` (default Docker bridge gateway)
2. `http://host.docker.internal:11434` (works with Docker 20.10+ with --add-host=host.docker.internal:host-gateway)
3. Check your actual bridge IP: `ip addr show docker0` and use whatever IP it shows

If none work, set the Ollama service to listen on all interfaces. Edit the service:
```
sudo systemctl edit ollama
```
Add:
```
[Service]
Environment="OLLAMA_HOST=0.0.0.0"
```
Save and restart:
```
sudo systemctl restart ollama
```
Then `OLLAMA_BASE_URL=http://172.17.0.1:11434` should work.

### Permission denied running docker commands
Your user is not in the docker group yet. The `usermod -aG docker $USER` command was run, but it only takes effect after you log out and log back in. Or run `newgrp docker` in the current shell to pick up the new group without logging out.

### Firewall blocking container to host
On Fedora and RHEL, firewalld blocks container to host connections by default. Allow docker0:
```
sudo firewall-cmd --permanent --zone=trusted --add-interface=docker0
sudo firewall-cmd --reload
```

### Model runs slowly
Too big for the hardware. Pick a smaller model from ollama.com/library.

### "llama runner process has terminated"
Out of memory during inference. Pick a smaller model.

### Install script hangs
Could be a network issue or the script is downloading GPU drivers. Give it several minutes. If it is truly hung, Ctrl+C out, run the script again, or use the manual install (Option B).

---

## Managing the Ollama service

- Start: `sudo systemctl start ollama`
- Stop: `sudo systemctl stop ollama`
- Restart: `sudo systemctl restart ollama`
- Enable at boot: `sudo systemctl enable ollama`
- Disable at boot: `sudo systemctl disable ollama`
- View logs: `journalctl -u ollama -f`
- Update (Option A): re-run `curl -fsSL https://ollama.com/install.sh | sh`
- Update (Option B): download the new binary from github.com/ollama/ollama/releases and replace /usr/local/bin/ollama

---

## Coach rules (for the AI following this script)

1. **NEVER tell the user to run a specific named model.** Always guide them to ollama.com/library. Never say "try llama3" or "install gemma" by name.
2. **Give ONE stage at a time.** Wait for confirmation before moving on.
3. **Ask which install method first.** Stage 1 is a branch. Recommend Option A (install script).
4. When a user reports an error, ask for the exact message and match to the troubleshooting cheat sheet.
5. **Explain the WHY** when it helps learning.
6. **Celebrate small wins.** First "Ollama is running" and first model response are real milestones.
7. If stuck or frustrated, slow down and break a stage into smaller pieces.
8. If asked something not in this guide, suggest the official Ollama docs at ollama.com or github.com/ollama/ollama/issues.

---


