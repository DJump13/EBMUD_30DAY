# What is this?

This project is a Python app. You can either:

1. **Just run it** (no coding needed), or
2. **Set it up to edit and build on it**

---

## Running the App (No Python Needed)

If you want to download the ready-to-use version:

1. Go to Releases
2. Download the file from the most recent version for your OS

### Important

* Don’t move files out of the folder (if there is one)
* If nothing happens, try running it from Terminal/Command Prompt to see errors

---

## Want to Edit the Code? (Forking the Project)

If you want to make changes, start by making your own copy.

### Step 1 — Fork the repo

* Go to the project on GitHub
* Click **Fork** (top right)

This creates your own version of the project.

---

### Step 2 — Download your copy

```bash
git clone https://github.com/YOUR_USERNAME/REPO_NAME.git
cd REPO_NAME
```

---

### Step 3 — (Optional) Link original project

This lets you get updates later:

```bash
git remote add upstream https://github.com/ORIGINAL_OWNER/REPO_NAME.git
```

---

## Setting Up Python

You need a **virtual environment**. Think of it as a clean workspace just for this project.

---

### Step 1 — Create a virtual environment

Most systems use `python3`:

```bash
python3 -m venv .venv
```

---

### Step 2 — Turn it on (activate it)

#### macOS/Linux

```bash
source .venv/bin/activate
```

#### Windows

```bash
.venv\Scripts\activate
```

You should now see something like:

```bash
(.venv)
```

---

### Step 3 — Install required packages

```bash
pip3 install -r requirements.txt
```

---

### Step 4 — Run the app

```bash
python3 main.py
```

---

## Using PyCharm (Optional)

If you use PyCharm:

1. Open the project
2. Go to **Settings → Python Interpreter**
3. Select:

   ```bash
   .venv/bin/python
   ```

---

## Packaging the App (Making the Executable)

This turns your Python app into something people can double-click.

We use PyInstaller for this.

---

### Important

You must build on each system:

* Build on Mac → works on Mac
* Build on Windows → works on Windows

---

### Step 1 — Install PyInstaller

```bash
pip3 install pyinstaller
```

---

### Step 2 — Build the app

#### Fast startup (recommended)

```bash
pyinstaller --windowed main.py
```

#### Single file (slower startup)

```bash
pyinstaller --onefile --windowed main.py
```

---

### Step 3 — Find your app

Look in the `dist` folder:

* Mac → `.app` or folder
* Windows → `.exe` or folder

---

## Fixing Common Errors

### Missing module error

Example:

```bash
ModuleNotFoundError: No module named 'xyz'
```

Fix:

```bash
pyinstaller --windowed --hidden-import=xyz main.py
```

---

### 🔄 Clean rebuild (if things break)

#### macOS/Linux

```bash
rm -rf build dist *.spec
```

#### Windows

```bat
rmdir /s /q build
rmdir /s /q dist
del *.spec
```

Then run the build again.

---

## Key Ideas (Simple Version)

* A **virtual environment** keeps your project’s packages separate
* You only need Python if you’re editing the project
* The packaged app runs without Python
* PyInstaller turns your code into an app

---

## Quick Summary

| What you want to do | What to do                            |
| ------------------- | ------------------------------------- |
| Just run the app    | Open file in `dist/`                  |
| Edit code           | Create `.venv` + install requirements |
| Build app (Mac)     | Run PyInstaller on Mac                |
| Build app (Win)     | Run PyInstaller on Windows            |

---

## Need Help?

If something isn’t working:

* Make sure your environment is activated (`(.venv)` shows)
* Make sure you installed requirements
* Try running from terminal to see errors

---
