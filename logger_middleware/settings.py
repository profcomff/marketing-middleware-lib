import os
from functools import lru_cache


class Settings:
    """Module settings"""

    LOGGING_MARKETING_URLS = {
        "dev": f"http://localhost:{os.getenv('MARKETING_PORT', 8000)}/v1/action",
        "test": "https://api.test.profcomff.com/marketing/v1/action",
        "prod": "https://api.profcomff.com/marketing/v1/action",
    }
    RETRY_DELAYS = [2, 4, 8]  # Задержки перед повторными попытками


@lru_cache
def get_settings() -> Settings:
    settings = Settings()
    return settings
