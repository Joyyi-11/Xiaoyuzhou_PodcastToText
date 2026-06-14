import os

from dotenv import load_dotenv

load_dotenv()


def get_xunfei_config() -> dict:
    return {
        "app_id": os.getenv("XUNFEI_APP_ID", ""),
        "api_key": os.getenv("XUNFEI_API_KEY", ""),
        "api_secret": os.getenv("XUNFEI_API_SECRET", ""),
    }


def get_deepseek_api_key() -> str:
    return os.getenv("DEEPSEEK_API_KEY", "")


def check_config() -> list[str]:
    missing = []
    if not get_xunfei_config()["app_id"]:
        missing.append("XUNFEI_APP_ID")
    if not get_xunfei_config()["api_key"]:
        missing.append("XUNFEI_API_KEY")
    if not get_xunfei_config()["api_secret"]:
        missing.append("XUNFEI_API_SECRET")
    if not get_deepseek_api_key():
        missing.append("DEEPSEEK_API_KEY")
    return missing
