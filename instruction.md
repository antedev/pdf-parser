# The One Ring - PDF Translation Pipeline

## Environment Setup
*   **Operating System**: Windows
*   **Shell**: PowerShell
*   **Core Tooling**: `marker-pdf` natively accessed through Python API. We rely on the `datalab-to/marker` pipeline to process rulebooks and compendiums. The processing heavily utilizes LLMs (Gemini, controlled via `.env`) to preserve complicated table structures, OCR, and complex layouts during the export.

## Automation Script
We use python scripts like `sync_lore.py` to trigger operations. These scripts completely sidestep the CLI wrapper of `marker_single`, instead initializing the `PdfConverter` directly so we can programmatically manage file workflows.

## Directory Structure Strategy
The pipeline relies on a strict directory structure relative to the project root:

1.  `Source_Material/Unprocessed/`
    *   **Purpose**: The drop-in folder for all new PDF content that needs OCR and conversion.
2.  `Source_Material/Processed/`
    *   **Purpose**: Files are moved here dynamically by the Python script after a successful translation to markdown. 
3.  `The_One_Ring/`
    *   **Purpose**: The main output directory.
    *   **Subdirectories**: Each PDF converted will generate its own directory here matching the basename of the PDF (e.g., `TOR_Starter_Set_The_Shire` directory for `TOR_Starter_Set_The_Shire.pdf`). The subdirectories will hold the final Markdown file alongside any extracted images or chunk data.

## Conflict Resolution
If the program detects that an output directory in `The_One_Ring/` already exists for a target PDF, or if the target PDF name already exists in `Source_Material/Processed/`, the script should throw a console warning and completely skip processing that file, continuing on to the next. Duplications are not allowed.
