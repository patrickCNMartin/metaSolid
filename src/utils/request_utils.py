import requests

# -----------------------------------------------------------------------------#
# IMPORT GENERIC UTILS
# -----------------------------------------------------------------------------#
from utils.utils import trim_response


# -----------------------------------------------------------------------------#
# DEF FUNCTIONS
# -----------------------------------------------------------------------------#
def get_cores(base_url, core_loc, headers, return_info: str = "all"):
    response = requests.get(f"{base_url}/{core_loc}.json", headers=headers)
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
    base_url,
    core_loc,
    headers,
    core_id: int,
    from_date: None | str = None,
    per_page=30,
    filters: dict = {},
) -> list:
    all_requests = []
    page = 1
    while True:
        print(f"Checking and Filtering page {page}")
        params = {"page": page, "per_page": per_page, **filters}
        if from_date is not None:
            params["from_date"] = from_date
        filtered_response = requests.get(
            f"{base_url}/{core_loc}/{core_id}/service_requests.json",
            headers=headers,
            params=params,
        )
        filtered_response.raise_for_status()
        local_requests = trim_response(filtered_response.json(), "service_requests")
        if not local_requests:
            break
        all_requests.extend(local_requests)
        page += 1
    return all_requests


def get_custom_forms(service_request, headers, form="all"):
    """Get custom form associated with a specific service ID"""
    custom_form_action = service_request["actions"]["list_custom_forms"]["url"]
    response = requests.get(custom_form_action, headers=headers)
    response.raise_for_status()
    forms = trim_response(response.json(), "custom_forms")
    if form == "all":
        return forms
    else:
        form_list = [f for f in forms if f["name"] in form]
        if len(form_list) == 1:
            return form_list[0]
        else:
            return form_list


def get_request_info(
    service_request,
) -> str | list:
    state = service_request["state"]
    person = service_request["owner"]["name"]
    service_name = service_request["name"]
    return {"State": state, "Person": person, "Service name": service_name}


# Do we need to parse this if there is no requested info? I don't think so
# Why bother filtering
def get_request_description(
    service_request,
    headers,
    field_label: list,
    form_name: str = "Meeting protocol",
):
    form = get_custom_forms(service_request, headers, form_name)
    # This is stupid and needs to be updated
    if len(form) == 0:
        return "No Description \n"

    fields = form["fields"]
    # there is a cleaner way of doing this - but it will do for now.
    field_info = {
        fi["label"]: fi["value"] for fi in fields if fi["identifier"] in field_label
    }
    return field_info
