import os
import argparse
import requests
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("API_KEY")
BASE_URL = os.getenv("BASE_DOMAIN")

headers = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json",
}


def get_cores():
    """GET /v1/cores.json — retrieve all cores."""
    response = requests.get(f"{BASE_URL}/v1/cores.json", headers=headers)
    response.raise_for_status()
    return response.json()


def parse_args():
    parser = argparse.ArgumentParser(
        description="iLab API client",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
examples:
  python ilab_api.py --action get_cores
        """,
    )
    parser.add_argument(
        "--action",
        choices=["get_cores"],
        required=True,
        help="Action to perform against the iLab API",
    )
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()

    if args.action == "get_cores":
        result = get_cores()
        print(result)
