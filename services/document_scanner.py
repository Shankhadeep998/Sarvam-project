import os
import time
import io
import zipfile
import httpx
from typing import Union, BinaryIO, Dict, Any
from services.sarvam_client import get_sarvam_client

def digitise_handwritten_document(
    doc_file: Union[str, BinaryIO, bytes],
    filename: str = "notes.png",
    language: str = "en-IN",
    content_type: str = "handwritten",
    output_format: str = "md",
    poll_interval: float = 2.0,
    max_timeout: float = 120.0,
) -> Dict[str, Any]:
    """
    Submits a handwritten notes image or PDF to Sarvam Vision (Doc AI Digitise),
    polls the job until completed, and extracts the recognized Markdown text.

    :param doc_file: File path, file-like object, or raw bytes.
    :param filename: Filename (e.g. notes.png, notes.pdf, notes.jpg).
    :param language: Language code, e.g. 'en-IN', 'hi-IN'.
    :param content_type: 'handwritten' (default), 'printed', or 'mixed'.
    :param output_format: 'md' (Markdown), 'html', or 'json'.
    :param poll_interval: Seconds between status polling requests.
    :param max_timeout: Maximum seconds to wait for job completion.
    :return: dict with 'markdown_text', 'job_id', 'status', 'pages_processed'.
    """
    client = get_sarvam_client()

    # Determine MIME type
    lower_name = filename.lower()
    if lower_name.endswith(".pdf"):
        mime_type = "application/pdf"
    elif lower_name.endswith(".png"):
        mime_type = "image/png"
    elif lower_name.endswith(".jpg") or lower_name.endswith(".jpeg"):
        mime_type = "image/jpeg"
    else:
        mime_type = "application/octet-stream"

    # Read binary content
    if isinstance(doc_file, str):
        with open(doc_file, "rb") as f:
            file_bytes = f.read()
    elif isinstance(doc_file, bytes):
        file_bytes = doc_file
    else:
        file_bytes = doc_file.read()

    # Submit Digitise job
    job = client.doc_ai.digitise(
        file=[(filename, file_bytes, mime_type)],
        language=language,
        output_format=output_format,
        content_type=content_type,
    )

    job_id = job.job_id
    start_time = time.time()
    terminal_states = {"completed", "partially_completed", "failed", "rejected"}
    last_status = job.status

    # Poll status
    while time.time() - start_time < max_timeout:
        st = client.doc_ai.get_status(job_id=job_id)
        last_status = st.status.lower()
        if last_status in terminal_states:
            break
        time.sleep(poll_interval)

    if last_status not in ("completed", "partially_completed"):
        raise RuntimeError(
            f"Document digitisation ended with status '{last_status}' (Job ID: {job_id})"
        )

    # Retrieve output
    extracted_text = ""
    pages_processed = 0

    # 1. Try fetching via get_results
    try:
        results = client.doc_ai.get_results(job_id=job_id)
        if hasattr(results, "documents") and results.documents:
            doc_texts = []
            for doc in results.documents:
                if hasattr(doc, "pages") and doc.pages:
                    for page in doc.pages:
                        pages_processed += 1
                        if hasattr(page, "content") and page.content:
                            doc_texts.append(str(page.content))
                        elif hasattr(page, "text") and page.text:
                            doc_texts.append(str(page.text))
            if doc_texts:
                extracted_text = "\n\n".join(doc_texts)
    except Exception:
        pass

    # 2. If not obtained, download result zip archive
    if not extracted_text:
        try:
            dl = client.doc_ai.get_download_url(job_id=job_id)
            if hasattr(dl, "url") and dl.url:
                resp = httpx.get(dl.url, timeout=30.0)
                if resp.status_code == 200:
                    with zipfile.ZipFile(io.BytesIO(resp.content)) as z:
                        md_files = [n for n in z.namelist() if n.endswith(".md") or n.endswith(".txt") or n.endswith(".html")]
                        if md_files:
                            # Primary file is usually the document markdown
                            main_file = md_files[0]
                            with z.open(main_file) as f:
                                extracted_text = f.read().decode("utf-8", errors="replace")
        except Exception as e:
            if not extracted_text:
                extracted_text = f"[Recognized text could not be downloaded: {e}]"

    return {
        "job_id": job_id,
        "status": last_status,
        "markdown_text": extracted_text,
        "pages_processed": pages_processed,
    }
