import os
import time
from datetime import datetime, timezone

import requests

API_BASE_URL = os.getenv("API_BASE_URL", "http://api:8000")
BOT_PLATFORM = os.getenv("BOT_PLATFORM", "telegram")


def run() -> None:
    while True:
        try:
            response = requests.get(f"{API_BASE_URL}/healthz", timeout=5)
            print(
                f"[{datetime.now(timezone.utc).isoformat()}] "
                f"worker={BOT_PLATFORM} api_status={response.status_code}",
                flush=True,
            )
        except Exception as exc:  # noqa: BLE001
            print(f"worker ping failed: {exc}", flush=True)

        time.sleep(15)


if __name__ == "__main__":
    run()
