"""Download SOHO/MDI full-disk continuum images (2002-2011) from JSOC.

Uses the drms package to query JSOC directly (more reliable than VSO for
this product) and lets the server handle daily sampling via DRMS record-set
cadence syntax (@1d), instead of filtering results in Python.

Downloads file by file (not as one big batch) so that:
- a single network timeout doesn't lose the whole run
- re-running the script skips files already downloaded (resumable)
- a failed file is retried a few times before being logged and skipped

Requires a JSOC-registered email: http://jsoc.stanford.edu/ajax/register_email.html
"""


#This code was highly assisted by Claude AI
import os
import time

import drms
import requests

EMAIL = "andrei2legal@gmail.com"
SERIES = "mdi.fd_Ic_interp"
START = "2002.01.01_TAI"
END = "2011.12.31_TAI"
CADENCE = "1d"
OUTPUT_DIR = r"D:\IC-DeepLearning\data_mdi"

MAX_RETRIES = 3
TIMEOUT_SECONDS = 60


def download_with_retry(url, dest_path):
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            with requests.get(url, stream=True, timeout=TIMEOUT_SECONDS) as response:
                response.raise_for_status()
                with open(dest_path, "wb") as f:
                    for chunk in response.iter_content(chunk_size=8192):
                        f.write(chunk)
            return True
        except Exception as e:
            print(f"    tentativa {attempt}/{MAX_RETRIES} falhou: {e}")
            time.sleep(5)
    return False


def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    client = drms.Client(email=EMAIL)
    query = f"{SERIES}[{START}-{END}@{CADENCE}]{{continuum}}"

    print(f"Query: {query}")
    export_request = client.export(query, method="url", protocol="fits")

    print("Aguardando o JSOC preparar os arquivos...")
    export_request.wait()

    urls_df = export_request.urls
    total = len(urls_df)
    print(f"{total} arquivos disponíveis para download")

    downloaded = skipped = failed = 0

    for i, row in urls_df.iterrows():
        filename = row["filename"]
        url = row["url"]
        dest_path = os.path.join(OUTPUT_DIR, filename)

        if os.path.exists(dest_path) and os.path.getsize(dest_path) > 0:
            skipped += 1
            continue

        print(f"[{i + 1}/{total}] baixando {filename}...")
        if download_with_retry(url, dest_path):
            downloaded += 1
        else:
            failed += 1
            print(f"    [FALHOU] {filename} — pulando para o próximo")

    print(f"\nConcluído: {downloaded} baixados, {skipped} já existiam, {failed} falharam.")


if __name__ == "__main__":
    main()