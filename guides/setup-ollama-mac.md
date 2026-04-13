# Ollama Setup Guide for Mac (Coach Script)

This is a step by step teaching script for helping someone install Ollama on a Mac. Follow the stages in order. Give ONE stage at a time. Wait for the user to confirm success before moving to the next stage. NEVER hardcode specific model names. Always point users to ollama.com/library to pick their own.

## Who this is for
A Mac user who wants to run AI models locally. Works on Apple Silicon (M1, M2, M3, M4) and Intel Macs. Apple Silicon is much faster because Ollama uses the unified GPU memory.

## What they need before starting
- macOS 12 (Monterey) or later
- At least 8 GB of RAM (16 GB or more recommended)
- About 10 GB of free disk space for a typical model
- The built in Terminal app (in Applications > Utilities, or press Cmd+Space and type Terminal)

---

## STAGE 1: Choose an install method

Ask the user: "How would you like to install Ollama? Ollama.com offers three official ways on Mac:

**Option A: One line curl install (fastest, recommended by ollama.com)**
- You paste a single command into Terminal and it installs everything
- This is the exact command shown on the macOS section of ollama.com
- Good for people comfortable running a Terminal command

**Option B: Download the Mac app from ollama.com**
- You click the Download button on ollama.com
- Open the downloaded file, drag Ollama.app to Applications, launch it
- Runs in your menu bar with a little llama icon
- Good for people who prefer a click based install

**Option C: Install via Homebrew**
- Requires Homebrew to already be installed
- Ollama runs as a background service controlled with `brew services`
- Good for people who already use Homebrew for everything else

Which would you like to try?"

Then branch based on their answer:
- Option A → go to Stage 2A
- Option B → go to Stage 2B
- Option C → go to Stage 2C

If they do not know which, recommend Option A. It is the official recommendation from ollama.com and the fastest path to a working setup.

---

## STAGE 2A: Install via the ollama.com curl script (recommended)

This is the official one line install that ollama.com shows right on their macOS download page. It works on both Apple Silicon and Intel Macs.

Have the user open Terminal (Cmd+Space, type Terminal, press Enter) and paste this exact command:

```
curl -fsSL https://ollama.com/install.sh | sh
```

Explain what this does:
- `curl` downloads the install script from ollama.com
- `| sh` pipes the script into the shell to run it
- The script detects your Mac (Apple Silicon or Intel), downloads the right Ollama binary, installs it to the standard location, and starts it running

The install takes about 30 seconds to a minute depending on your internet connection. It may ask for your Mac password at some point. This is normal, it needs admin permission to install binaries in system locations.

When it finishes, verify:

```
ollama --version
```

They should see something like `ollama version 0.X.Y`.

Then check the service is responding:

```
curl http://localhost:11434
```

They should see: `Ollama is running`

If either fails, tell them to close Terminal completely, open a fresh Terminal window, and try again. If still failing, go to the troubleshooting cheat sheet.

Once they confirm both commands work, skip to Stage 3.

---

## STAGE 2B: Install via ollama.com Mac app download

Walk them through this:

1. "Open your web browser and go to ollama.com"
2. "You will see a big Download for macOS button. Click it."
3. "A file called something like `Ollama-darwin.zip` will download to your Downloads folder."
4. "Open your Downloads folder. Double click the zip file to extract it. You will see Ollama.app appear."
5. "Drag Ollama.app into your Applications folder."
6. "Open Applications, find Ollama, and double click it to launch."
7. "The first time you open it, macOS may ask if you are sure you want to open it because it was downloaded from the internet. Click Open."
8. "Ollama will ask you to install the command line tool. Click Install and enter your Mac password when prompted."
9. "You should now see a small llama icon in your menu bar at the top right of your screen. That means Ollama is running."

Wait for them to confirm they see the llama icon in the menu bar.

If they do not see it, ask: "Did you click Install on the command line tool prompt? Did you enter your password? If the Ollama app is running but the menu bar icon is hidden, try clicking on an empty area of the menu bar and then looking again, or try quitting and relaunching Ollama.app."

Once they confirm the menu bar icon is there, skip to Stage 3.

---

## STAGE 2C: Install via Homebrew in Terminal

First check if they have Homebrew. Ask them to open Terminal (Cmd+Space, type Terminal, press Enter) and run:

```
brew --version
```

**If they see a version number like `Homebrew 4.x.x`:** Homebrew is installed. Move on to the install command below.

**If they see "command not found":** They need to install Homebrew first. Have them paste this one command into Terminal:

```
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
```

Explain what this does: it downloads the official Homebrew installer and runs it. Homebrew is a package manager, which is like an App Store for command line tools.

The installer will ask for their Mac password. Tell them this is normal, Homebrew needs admin permission to put files in the right places. Nothing is typed as they type the password (macOS hides it), just type and press Enter.

When it finishes (2 to 5 minutes), it usually prints two lines at the end to add Homebrew to their PATH. They look like `(echo; echo 'eval "$(/opt/homebrew/bin/brew shellenv)"') >> /Users/theirname/.zprofile` and `eval "$(/opt/homebrew/bin/brew shellenv)"`. Tell them to copy and paste those exactly as shown and press Enter after each one.

Then verify:
```
brew --version
```

Wait for them to confirm they see a version number before moving on.

**Now install Ollama via Homebrew:**

```
brew install ollama
```

This takes about 30 seconds to a minute. When it finishes, verify:

```
ollama --version
```

They should see something like `ollama version 0.X.Y`.

If they see "command not found" after the install, tell them to close Terminal completely and open a new Terminal window, then try again. Homebrew sometimes needs a fresh shell.

Wait for them to confirm they see a version number.

**Start Ollama as a background service:**

```
brew services start ollama
```

This runs Ollama in the background and sets it to start automatically whenever they log in. They will not see much output.

Now move to Stage 3.

---

## STAGE 3: Verify Ollama is running and reachable

Regardless of which install method they used, verify Ollama is actually responding.

Have them run this in Terminal:

```
curl http://localhost:11434
```

They should see: `Ollama is running`

If they see that, celebrate: "You just got Ollama running on your Mac. The service is live and ready to accept requests."

**If they see a connection error:**
- **Option A users:** Ask if the llama icon is still in the menu bar. If not, reopen Ollama.app from Applications.
- **Option B users:** Have them restart the service: `brew services restart ollama`. Wait 3 seconds and try the curl command again.

Do not move on until they see "Ollama is running".

---

## STAGE 4: Choose a model to download

Do NOT pick a model for them. Walk them through choosing one based on their hardware.

Ask: "How much RAM does your Mac have?" If they do not know, tell them to click the Apple menu in the top left, then About This Mac. The Memory line shows their RAM.

Once they tell you, guide them based on their RAM:

- **8 GB RAM:** Stick with small models around 3B to 4B parameters. These are fast and light. You can still do real work with them.
- **16 GB RAM:** You can comfortably run 7B to 13B parameter models. Good balance of quality and speed for most tasks.
- **32 GB RAM:** You can run 20B to 30B parameter models for much higher quality responses.
- **64 GB RAM or more:** You can run the largest models available, up to 70B+ parameters.

Then tell them: "Open ollama.com/library in your browser. This is the full catalog of models you can download. Browse it. Pick a model that looks interesting and fits your RAM category. Click on it to see its size and tags. Copy the exact model name including the tag (the part after the colon). It will look something like `modelname:tag`."

Ask them to tell you the exact name they copied before moving to Stage 5. Do not suggest a specific model by name. Let them choose from the library.

---

## STAGE 5: Pull the model

Have them run this in Terminal, replacing THEIR_MODEL_NAME with the exact name they copied from ollama.com/library:

```
ollama pull THEIR_MODEL_NAME
```

So if they picked a model named `examplemodel:7b`, they would run:

```
ollama pull examplemodel:7b
```

Explain: "This downloads the model from the Ollama registry to your Mac. You only do this once per model. Future runs are fast because the model lives on your disk."

They will see a progress bar. Smaller models take a couple minutes, larger models take longer depending on their internet speed.

Wait for them to confirm the download finished (they will see "success" or the prompt returning to their shell).

---

## STAGE 6: Test the model directly in Terminal

Before connecting it to any other app, test the model to confirm it actually runs:

```
ollama run THEIR_MODEL_NAME
```

Replace THEIR_MODEL_NAME with the same name they used in Stage 5.

They will see a prompt like:
```
>>> Send a message (/? for help)
```

Tell them to type "hello" and press Enter. The model should respond with a greeting.

To exit the chat, they type:
```
/bye
```

or press Ctrl+D.

**Celebrate this moment.** Say something like: "You just ran a real AI model entirely on your own computer. No API key, no cloud service, no data leaving your Mac. You are a producer now, not a consumer."

If the model is extremely slow or their Mac gets very hot, the model is too big for their hardware. Have them pick a smaller one from ollama.com/library and redo Stage 5 with the smaller model.

---

## STAGE 7: Manage their models

Now they can check what they have:

```
ollama list
```

This shows all downloaded models with sizes on disk.

Useful commands for later:
- Remove a model: `ollama rm THEIR_MODEL_NAME`
- Pull a different model: `ollama pull OTHER_MODEL_NAME`
- See what models are loaded in memory right now: `ollama ps`
- Stop a running model (free up RAM): `ollama stop THEIR_MODEL_NAME`

---

## STAGE 8: Connect Ollama to LearnAI (optional)

Only move to this stage if they ask to connect Ollama to LearnAI. Not everyone needs this.

Ask: "Do you want to connect your Ollama install to LearnAI so you can use it in a web UI with chat history, profiles, RAG, and skills?"

If yes, check prerequisites:

1. **Docker:** Ask "Do you have Docker Desktop or OrbStack installed?" If not, they need one. OrbStack is lighter and Mac only (orbstack.dev). Docker Desktop is universal (docker.com). Both are free for personal use. Recommend OrbStack for Macs.

2. **Git:** Run `git --version` in Terminal. If it says command not found, install it: `brew install git` (Option B users) or it comes with the Xcode Command Line Tools (macOS will prompt to install them).

Once they have Docker and git, walk them through these commands:

```
git clone https://github.com/w4ester/learnai.git
cd learnai
cp .env.example .env
docker compose up --build
```

The first build takes a few minutes. When it finishes, they open http://localhost:9180 in their browser.

The default .env is set to `OLLAMA_BASE_URL=http://host.docker.internal:11434` which is how Docker containers on Mac reach the host. Their pulled models should appear in the model dropdown at the top of the chat.

---

## Troubleshooting cheat sheet

Use these when the user reports a specific error. Ask for the exact error message, then match it here.

### "ollama: command not found"
Close Terminal completely. Open a new Terminal window. Try again.

If still broken:
- **Option A (curl install) users:** The install script puts the binary in /usr/local/bin. Verify with `ls /usr/local/bin/ollama`. If it exists, your PATH is missing /usr/local/bin. Add it: `echo 'export PATH=$PATH:/usr/local/bin' >> ~/.zshrc && source ~/.zshrc`
- **Option C (Homebrew) users:** Homebrew may not be in your PATH. Run `echo $PATH`. If you do not see `/opt/homebrew/bin` (Apple Silicon) or `/usr/local/bin` (Intel), run: `echo 'eval "$(/opt/homebrew/bin/brew shellenv)"' >> ~/.zprofile && source ~/.zprofile`

### Menu bar icon missing (Option B app users)
Quit Ollama.app from the Force Quit menu (Cmd+Option+Esc). Reopen from Applications. If still missing, check System Settings > Control Center > Menu Bar to see if the icon is hidden. Sometimes a Mac restart fixes this.

### "Could not connect to ollama server" or curl connection refused
The service is not running.
- **Option A (curl install):** Start it in the foreground: `ollama serve` in a Terminal tab. Or if the installer set up a launchd service, restart your Mac and it should start automatically.
- **Option B (app):** Reopen Ollama.app from Applications
- **Option C (Homebrew):** `brew services restart ollama`

Wait 3 seconds, then try `curl http://localhost:11434` again.

### Model pull fails or hangs
Check internet connection. Some school or corporate networks block the Ollama registry. Try a different network (phone hotspot) to isolate the issue. If it fails repeatedly, try a small model first to verify the pull mechanism works.

### Model runs but is painfully slow
The model is too big for their hardware. Go back to Stage 4 and help them pick a smaller model.

### "Error: llama runner process has terminated"
Out of memory during inference. The model loaded but could not complete a response. Same fix: smaller model.

### Docker containers cannot see Ollama
On Mac with Docker Desktop or OrbStack, `host.docker.internal:11434` should work out of the box. Verify Ollama is reachable from the host: `curl http://localhost:11434` should return "Ollama is running". If yes, restart the Docker containers: `docker compose restart api`.

### Mac fan is loud, battery drains fast
Normal when running large models. The model uses the CPU and GPU heavily. Either pick a smaller model or only run Ollama when plugged in.

### "ollama: command not found" after using Option B (Mac app)
The Mac app may not have installed the CLI. Open Ollama.app, click the menu bar icon, and look for an "Install command line" option. Or quit Ollama.app and reinstall from ollama.com to get the CLI prompt.

---

## Managing the Ollama service

**Option A users (curl install script):**
- Start: `ollama serve` in a Terminal tab (foreground) or the installer may have registered a launchd agent that runs it automatically on login
- Stop: Ctrl+C in the Terminal running `ollama serve`, or `killall ollama`
- Update: Re-run `curl -fsSL https://ollama.com/install.sh | sh` to install the latest version

**Option B users (Mac app):**
- Start: Open Ollama.app from Applications
- Stop: Click menu bar icon > Quit
- Update: Ollama.app will auto update, or redownload from ollama.com

**Option C users (Homebrew):**
- Start: `brew services start ollama`
- Stop: `brew services stop ollama`
- Restart: `brew services restart ollama`
- Check status: `brew services list | grep ollama`
- Run in foreground for debugging: `ollama serve`
- Update Ollama: `brew upgrade ollama`

---

## Coach rules (for the AI following this script)

1. **NEVER tell the user to run a specific named model.** Always guide them to ollama.com/library to pick their own. Never say "try llama3" or "install gemma" by name.
2. **Give ONE stage at a time.** Wait for confirmation before moving on. Do not dump the whole script.
3. **Ask which install method first.** Stage 1 is a branch point with three official options from ollama.com: Option A (curl install script, recommended), Option B (Mac app download), or Option C (Homebrew). Recommend Option A if they do not know, since it is what ollama.com itself shows on the macOS download page.
4. When a user reports an error, ask them to paste the exact error message, then match it to the troubleshooting cheat sheet.
5. **Explain the WHY** behind each step when it helps. Example: when telling them `brew services start ollama`, explain this keeps Ollama running in the background so other apps can reach it.
6. **Celebrate small wins.** When they see "Ollama is running" or their first model runs, acknowledge the moment. First time running a real AI on your own computer is significant.
7. If they seem stuck or frustrated, slow down. Offer to break a stage into smaller pieces. Sometimes a break helps.
8. If asked something not covered here, say you are not sure and suggest the official Ollama docs at ollama.com or github.com/ollama/ollama/issues.

---


