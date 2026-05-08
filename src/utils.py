# Utility functions
from datetime import datetime, timezone
from dateutil.relativedelta import relativedelta


def trim_response(response: dict, id: str, metadata: bool = False):
    """Extract actual info from response Dict or return iLab meta data"""
    # this is not super elegant and a bit hardcoded
    if metadata:
        return response["ilab_response"][1]
    else:
        return response["ilab_response"][id]


def set_default_cutoff_date(years: int = 2):
    today = datetime.now(timezone.utc)
    delta = relativedelta(years=years)
    cut_off = today - delta
    return cut_off.isoformat(timespec="milliseconds")
