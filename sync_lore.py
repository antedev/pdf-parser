import os
import argparse
import shutil
import logging
from pathlib import Path
from dotenv import load_dotenv

# Suppress annoying C++ GRPC logs from underlying LLM calls
os.environ["GRPC_VERBOSITY"] = "ERROR"
os.environ["GLOG_minloglevel"] = "2"

# 1. Import Marker modules natively
from marker.converters.pdf import PdfConverter
from marker.models import create_model_dict
from marker.output import save_output
from marker.config.parser import ConfigParser

# Load Credentials
load_dotenv()

# Setup Basic Logging
logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)

def get_args():
    parser = argparse.ArgumentParser(description="Convert RPG PDFs to Markdown using local models and Gemini.")
    
    parser.add_argument(
        "--pages", "-p",
        type=str,
        default=None,
        help="Page range to process (e.g., '1-10', '5-', or empty for all). Default is all pages."
    )
    
    parser.add_argument(
        "--ocr",
        action="store_true",
        default=False,
        help="Force OCR on all pages (even digital ones)."
    )
    
    parser.add_argument(
        "--no-llm",
        action="store_false",
        dest="use_llm",
        default=True,
        help="Disable LLM refinement (Gemini)."
    )
    
    parser.add_argument(
        "--model", "-m",
        type=str,
        default=os.getenv("GEMINI_MODEL", "gemini-3.1-pro-preview"),
        help="Gemini model to use for refinement."
    )

    return parser.parse_args()

def main():
    args = get_args()
    
    # 2. Define our Directory Pipeline
    BASE_DIR = Path(__file__).parent.resolve()
    UNPROCESSED_DIR = BASE_DIR / "Source_Material" / "Unprocessed"
    PROCESSED_DIR = BASE_DIR / "Source_Material" / "Processed"
    OUTPUT_BASE_DIR = BASE_DIR / "The_One_Ring"

    # Make sure folders exist
    UNPROCESSED_DIR.mkdir(parents=True, exist_ok=True)
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
    OUTPUT_BASE_DIR.mkdir(parents=True, exist_ok=True)

    # 3. Find PDFs in the Unprocessed directory
    pdf_files = list(UNPROCESSED_DIR.glob("*.pdf"))
    if not pdf_files:
        logger.info(f"No PDFs found in {UNPROCESSED_DIR}. Exiting.")
        return

    logger.info(f"Found {len(pdf_files)} PDF(s) to process. Initializing Converter...")

    # 4. Initialize Global Models (loaded once)
    model_dict = create_model_dict()

    # 5. Process Each PDF
    for pdf_path in pdf_files:
        base_name = pdf_path.stem
        target_output_dir = OUTPUT_BASE_DIR / base_name
        target_processed_file = PROCESSED_DIR / pdf_path.name

        # Duplicate Safety Check
        if target_output_dir.exists():
            logger.warning(f"[SKIP] Output directory already exists: {target_output_dir}")
            continue
        
        if target_processed_file.exists():
            logger.warning(f"[SKIP] File already exists in Processed folder: {target_processed_file}")
            continue

        logger.info(f"--- Processing Full Document: {pdf_path.name} ---")
        
        try:
            # 6. Configure Converter
            custom_config = {
                "use_llm": args.use_llm,
                "force_ocr": args.ocr,
                "output_format": "markdown",
                "page_range": args.pages if args.pages else None,
                "gemini_api_key": os.getenv("GOOGLE_API_KEY"),
                "gemini_model_name": args.model,
                "llm_timeout": 300 # 5-minute timeout for the full document refinement
            }

            config_parser = ConfigParser(custom_config)
            
            # Initialize for this specific PDF
            converter = PdfConverter(
                config=config_parser.generate_config_dict(),
                artifact_dict=model_dict,
                processor_list=config_parser.get_processors(),
                renderer=config_parser.get_renderer(),
                llm_service=config_parser.get_llm_service()
            )

            # 7. Execute Conversion
            target_output_dir.mkdir(parents=True, exist_ok=True)
            rendered_document = converter(str(pdf_path))

            # 8. Save results
            save_output(rendered_document, str(target_output_dir), base_name)
            
            # 9. Move the original
            shutil.move(str(pdf_path), str(target_processed_file))
            logger.info(f"✅ Successfully converted and moved to Processed!")

        except Exception as e:
            logger.error(f"❌ Failed to process {pdf_path.name}. Error: {e}")

if __name__ == "__main__":
    main()
