# 📖 Lore Sync — RPG PDF to Markdown Pipeline

A tool for automatically converting RPG rulebook PDFs into clean, structured Markdown. Uses local AI models for layout detection and Google Gemini for intelligent text refinement and table formatting.

---

## ✅ Prerequisites

Before you begin, make sure you have the following installed:

- **Python 3.13+** — [python.org](https://www.python.org/downloads/)
- **An NVIDIA GPU** *(recommended)* — Required for fast local processing. A GTX 1070 or better is recommended. The script will fall back to CPU if no GPU is available, but will be significantly slower.
- **A Google Gemini API Key** — Get one for free at [aistudio.google.com](https://aistudio.google.com/apikey)

---

## ⚙️ Installation

### 1. Clone or download the project

Place the project files in a folder of your choice.

### 2. Install PyTorch with CUDA support

> **Important:** You must install the CUDA-enabled version of PyTorch, **not** the default CPU version. The default `pip install torch` will download the CPU version.

Run the following in your terminal from the project folder:

```powershell
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu126
```

> 💡 This is a large download (~2.5 GB). It only needs to be done once.

### 3. Install Python dependencies

```powershell
pip install marker-pdf python-dotenv
```

### 4. Patch the marker-pdf library for better API stability

The `marker-pdf` library does not retry on `504 Gateway Timeout` errors by default. Apply this fix manually to prevent incomplete conversions on large PDFs.

Open the following file:
```
<your Python installation>\Lib\site-packages\marker\services\gemini.py
```

Find this line (around line 95):
```python
if e.code in [429, 443, 503]:
```

Change it to:
```python
if e.code in [429, 443, 503, 504]:
```

Save the file. This allows the converter to gracefully retry when Gemini is slow to respond.

---

## 🔑 Configuration

Create a `.env` file in the project root with the following content:

```env
GOOGLE_API_KEY=your_api_key_here
LLM_SERVICE=google
GEMINI_MODEL=gemini-3.1-pro-preview
```

Replace `your_api_key_here` with your actual Gemini API key.

---

## 📁 Directory Structure

The script manages files through a strict folder pipeline. These folders are created automatically on first run.

```
project/
├── Source_Material/
│   ├── Unprocessed/    ← DROP YOUR PDFs HERE
│   └── Processed/      ← Script moves files here after successful conversion
├── The_One_Ring/       ← Output Markdown files appear here
│   └── <BookName>/
│       ├── <BookName>.md
│       └── <images>.jpeg
├── sync_lore.py
└── .env
```

---

## 🚀 Running the Script

### Basic usage (convert all PDFs in the Unprocessed folder):

```powershell
python sync_lore.py
```

### Test with only a few pages first:

```powershell
python sync_lore.py --pages 1-5
```

### Convert without LLM refinement (faster, raw layout only):

```powershell
python sync_lore.py --no-llm
```

### Use a specific Gemini model:

```powershell
python sync_lore.py --model gemini-3.1-pro-preview
```

### See all available options:

```powershell
python sync_lore.py --help
```

---

## ⏱️ What to Expect

| Phase | What Happens | Time Estimate |
|---|---|---|
| **Layout Detection** | Local GPU models scan every page for columns, headers, tables | ~2-3s per page |
| **OCR Error Detection** | Local model checks for garbled characters | ~30s total |
| **Table Refinement** | Gemini API reformats tables into clean Markdown | ~15-45s per table |
| **Section Headers** | Gemini corrects heading hierarchy | ~30-90s total |

For a typical 56-page RPG rulebook, expect the full run to take **8–15 minutes**.

> ⚠️ You may see `504 DEADLINE_EXCEEDED` warnings in the console. These are harmless — the script will automatically retry up to 3 times. If a section still fails after retrying, it will use the local model's best effort and continue.

---

## 🔁 Re-running on Existing Files

The script includes **duplicate protection**. If a PDF has already been converted, it will be skipped automatically:

- If `The_One_Ring/<BookName>/` already exists → **SKIP**
- If `Source_Material/Processed/<BookName>.pdf` already exists → **SKIP**

To re-process a file, delete its output folder from `The_One_Ring/` and move the PDF back to `Source_Material/Unprocessed/`.

---

## 🐛 Troubleshooting

| Problem | Solution |
|---|---|
| `CUDA available: False` after PyTorch install | Make sure you used the `--index-url https://download.pytorch.org/whl/cu126` flag when installing torch |
| `No PDFs found in ... Exiting.` | Make sure your PDF is in `Source_Material/Unprocessed/`, not the project root |
| `504 DEADLINE_EXCEEDED` (no retry) | Make sure you applied the `gemini.py` patch in Step 4 of Installation |
| Very slow processing (many hours) | You are running on CPU. Install the CUDA version of torch (Step 2) |
| `APIError: 401` | Your `GOOGLE_API_KEY` in `.env` is invalid or missing |
