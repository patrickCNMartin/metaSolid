# -----------------------------------------------------------------------------#
# IMPORT LIBS
# -----------------------------------------------------------------------------#
import os

import argparse
import json
from pathlib import Path
from dotenv import load_dotenv

# -----------------------------------------------------------------------------#
# IMPORT GENERIC UTILS
# -----------------------------------------------------------------------------#
from utils.utils import set_default_cutoff_date
from utils.request_utils import (
    get_cores,
    get_request_description,
    get_request_info,
    select_service_request,
)
from reporting.format_convert import convert_sr_to_md
from reporting.build_ppt import convert_md_to_ppt

# -----------------------------------------------------------------------------#
# SET ENV VARS
# -----------------------------------------------------------------------------#
dotenv_path = Path.cwd() / "env" / ".env"
load_dotenv(dotenv_path=dotenv_path)


API_KEY = os.getenv("API_KEY")
BASE_URL = os.getenv("BASE_DOMAIN")
CORE_LOC = os.getenv("DEFAULT_CORE_LOCATION")

CORE_ID = os.getenv("CORE_ID")
CORE_NAME = os.getenv("CORE_NAME")

FROM_DATE = set_default_cutoff_date(int(os.getenv("YEARS_FROM_TODAY")))

FILTER_CRITERIA = json.loads(os.getenv("FILTER_CRITERIA"))
# Hardcoding this for now - but will move this to a more flaxeible approach later
REQUEST_INFO = [
    "What_is_the_background_of_your_project_and_the_aim_with_the_analysis_",
    "What_type_of_samples_do_you_have__species__blood_or_tissue__pellet_or_gel__etc__",
    "how_many_samples_would_you_analyze_",
]
PROTOCOL_INFO = ["BACKGROUND_OF_PROJECT_", "TYPE_OF_SAMPLES", "Number_of_samples_"]

REQ_DELIM = "===================================================================="
# -----------------------------------------------------------------------------#
# DEFINE ILAB HEADERS
# -----------------------------------------------------------------------------#
headers = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json",
}


# -----------------------------------------------------------------------------#
# DEFINE ARGUMENTS
# -----------------------------------------------------------------------------#
def parse_args():
    parser = argparse.ArgumentParser(
        description="iLab API client",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
examples:
  python ilab_api.py --outfile file_out.md
        """,
    )
    parser.add_argument(
        "--outfile",
        required=False,
        type=str,
        help="Output file location - if none provide default names will be used in current directory.",
    )

    return parser.parse_args()


# -----------------------------------------------------------------------------#
# ENTRY
# -----------------------------------------------------------------------------#
if __name__ == "__main__":
    args = parse_args()
    # need to update this function
    if CORE_ID is None or CORE_ID == "":
        CORE_ID = get_cores(BASE_URL, CORE_LOC, headers, "id")

    service_requests = select_service_request(
        BASE_URL, CORE_LOC, headers, CORE_ID, FROM_DATE, filters=FILTER_CRITERIA
    )
    request_info = [get_request_info(i) for i in service_requests]
    request_description = [
        get_request_description(
            i,
            headers,
            field_label=REQUEST_INFO,
            form_name="Start-up Meeting Request form",
        )
        for i in service_requests
    ]
    if args.outfile is None:
        outfile = "file_out"
    else:
        outfile = args.outfile
    convert_sr_to_md(request_info, request_description, outfile)
    convert_md_to_ppt(f"{outfile}.md", f"{outfile}.ppt")
