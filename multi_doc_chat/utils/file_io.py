from pathlib import Path
from typing import List
from fastapi import UploadFile
import uuid
import re
import logging

# Example: allowed file types
SUPPORTED_EXTENSIONS = {".pdf", ".png", ".jpg", ".jpeg", ".txt"}

log = logging.getLogger(__name__)

def save_uploaded_files(uploaded_files: List[UploadFile], target_dir: Path) -> List[Path]:
    """
    Save FastAPI UploadFile objects to the target directory.
    Returns list of saved file paths.
    """
    try:
        target_dir.mkdir(parents=True, exist_ok=True)
        saved_files: List[Path] = []

        for uf in uploaded_files:
            name = uf.filename
            ext = Path(name).suffix.lower()

            # Skip unsupported file types
            if ext not in SUPPORTED_EXTENSIONS:
                log.warning(f"Unsupported file skipped: {name}")
                continue

            # Sanitize and generate safe unique filename
            safe_name = re.sub(r'[^a-zA-Z0-9_\-]', '_', Path(name).stem).lower()
            unique_name = f"{safe_name}_{uuid.uuid4().hex[:8]}{ext}"
            out_path = target_dir / unique_name

            # Write file contents to disk
            with open(out_path, "wb") as out_file:
                contents = uf.file.read()
                out_file.write(contents)

            saved_files.append(out_path)
            log.info(f"Saved uploaded file: {name} -> {out_path}")

        return saved_files

    except Exception as e:
        log.error(f"Error saving uploaded files: {e}")
        raise RuntimeError("Failed to save uploaded files") from e