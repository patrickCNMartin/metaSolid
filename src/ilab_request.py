# -----------------------------------------------------------------------------#
# IMPORT LIBS
# -----------------------------------------------------------------------------#
import os
import argparse
import requests
from pathlib import Path
from dotenv import load_dotenv

# -----------------------------------------------------------------------------#
# IMPORT UTILS
# -----------------------------------------------------------------------------#
from src.utils import trim_response, set_default_cutoff_date

# -----------------------------------------------------------------------------#
# SET ENV VARS
# -----------------------------------------------------------------------------#
dotenv_path = Path.cwd() / "env" / ".env"
load_dotenv(dotenv_path=dotenv_path)


API_KEY = os.getenv("API_KEY")
BASE_URL = os.getenv("BASE_DOMAIN")
CORE_LOC = os.getenv("DEFAULT_CORE_LOCATION")
CUT_OFF_DATE = set_default_cutoff_date(os.getenv("CUT_OFF_DATE"))
# -----------------------------------------------------------------------------#
# DEFINE ILAB HEADERS
# -----------------------------------------------------------------------------#
headers = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json",
}


# -----------------------------------------------------------------------------#
# DEF FUNCTIONS
# -----------------------------------------------------------------------------#


def get_cores(return_info: str = "all"):
    response = requests.get(f"{BASE_URL}/{CORE_LOC}.json", headers=headers)
    response.raise_for_status()
    cores = trim_response(response.json(), "cores")
    match return_info:
        case "all":
            return cores
        # Potentially use a filter dict instead
        # Tha assumption is you don't know what the core info is
        case "id":
            return [i["id"] for i in cores]
        case "name":
            return [n["name"] for n in cores]
        case _:
            raise ValueError("Unknown information to return")


def select_service_request(
    core_id: int, from_date: str, per_page=100, filters: dict = {}
) -> list:
    all_requests = []
    page = 1
    while True:
        params = {"page": page, "per_page": per_page, "from_date": from_date, **filters}
        filtered_response = requests.get(
            f"{BASE_URL}/{CORE_LOC}/{core_id}/service_requests.json",
            headers=headers,
            params=params,
        )
        filtered_response.raise_for_status()
        local_requests = filtered_response.json()
        if not local_requests:
            break
        all_requests.extend(local_requests)
        page += 1
    return all_requests


def get_service_request(services):
    """Pull out specific request?"""
    service_request_action = services["actions"]["show_request"]["url"]
    response = requests.get(service_request_action, headers=headers)
    response.raise_for_status()
    request = trim_response(response.json(), "service_request")
    return request


def get_custom_forms(service):
    """Get custom form associated with a specific service ID"""
    custom_form_action = service["actions"]["list_custom_forms"]["url"]
    response = requests.get(custom_form_action, headers=headers)
    response.raise_for_status()
    forms = trim_response(response.json(), "custom_forms")
    return forms


def get_milestones(service):
    """Get custom form associated with a specific service ID"""
    milestone_action = service["actions"]["list_milestones"]["url"]
    response = requests.get(milestone_action, headers=headers)
    response.raise_for_status()
    milestones = trim_response(response.json(), "object")
    return milestones


def extract_active_requests(core_id: int, service_id: int):
    return 0


def non_empty_descriptions(services):
    id_list = [
        service["id"]
        for service in services
        if service["description"] is not None or service["description"] != ""
    ]
    return id_list


def person_info(service):
    service_type = service["service_name"]
    person = service["owner"]["name"]
    service_name = service["name"]
    return service_type, person, service_name


# for f in range(len(forms)):
#     with open(f'form_{f}.json','w') as fo:
#         json.dump(forms[f],fo)

# with open("core.json",'w') as r:
#     json.dump(req,r)


# -----------------------------------------------------------------------------#
# DEFINE ARGUMENTS
# -----------------------------------------------------------------------------#
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


# -----------------------------------------------------------------------------#
# ENTRY
# -----------------------------------------------------------------------------#
# if __name__ == "__main__":
#     args = parse_args()

#     if args.action == "get_cores":
#         result = get_cores()
#         print(result)
