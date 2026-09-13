"""Download NOAA SWPC Solar Region Summary (SRS) daily reports.

Files are small text files, one per day, served from NCEI's long-term
archive. Downloads day by day (resumable — skips files already present)
with retry on transient failures, similar to the MDI image downloader.
This code was highly assisted by Claude AI"""

import os
import time
from datetime import date, timedelta

import requests

START_DATE = date(2002, 1, 1)
END_DATE = date(2011, 12, 31)  # same period as the downloaded MDI images
OUTPUT_DIR = r"D:\IC-DeepLearning\data_srs"
BASE_URL = "https://www.ngdc.noaa.gov/stp/space-weather/swpc-products/daily_reports/solar_region_summaries"

MAX_RETRIES = 3
TIMEOUT_SECONDS = 30

os.makedirs(OUTPUT_DIR, exist_ok=True)


def download_with_retry(url, dest_path):
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            response = requests.get(url, timeout=TIMEOUT_SECONDS)
            if response.status_code == 404:
                return "not_found"
            response.raise_for_status()
            with open(dest_path, "wb") as f:
                f.write(response.content)
            return "ok"
        except Exception as e:
            print(f"    tentativa {attempt}/{MAX_RETRIES} falhou: {e}")
            time.sleep(3)
    return "failed"


def main():
    current = START_DATE
    downloaded = skipped = missing = failed = 0

    while current <= END_DATE:
        filename = f"{current.strftime('%Y%m%d')}SRS.txt"
        url = f"{BASE_URL}/{current.strftime('%Y')}/{current.strftime('%m')}/{filename}"
        dest_path = os.path.join(OUTPUT_DIR, filename)

        if os.path.exists(dest_path) and os.path.getsize(dest_path) > 0:
            skipped += 1
        else:
            print(f"Baixando {filename}...")
            result = download_with_retry(url, dest_path)
            if result == "ok":
                downloaded += 1
            elif result == "not_found":
                missing += 1
                print(f"  [--] {filename} não encontrado (404)")
            else:
                failed += 1
                print(f"  [FALHOU] {filename}")

        current += timedelta(days=1)

    print(
        f"\nConcluído: {downloaded} baixados, {skipped} já existiam, "
        f"{missing} não encontrados, {failed} falharam."
    )


if __name__ == "__main__":
    main()