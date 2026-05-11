# -----------------------------------------------------------------------------#
# IMPORT LIBS
# -----------------------------------------------------------------------------#


# -----------------------------------------------------------------------------#
# SET GLOBAL VARS
# NOTE: this will need to be changed to have more fexibility. I don't like this
# The probelem is that it assume that the list are in the same order with
# the same elements. Which might not always be the case.
# -----------------------------------------------------------------------------#
REQUEST_INFO = [
    "What_is_the_background_of_your_project_and_the_aim_with_the_analysis_",
    "What_type_of_samples_do_you_have__species__blood_or_tissue__pellet_or_gel__etc__",
    "how_many_samples_would_you_analyze_",
]
PROTOCOL_INFO = ["BACKGROUND_OF_PROJECT_", "TYPE_OF_SAMPLES", "Number_of_samples_"]

SHORTHAND_DESC = ["Background", "Type of sample", "Number of Samples"]

# -----------------------------------------------------------------------------#
# DEF FUNCTIONS
# -----------------------------------------------------------------------------#


def convert_to_md(sr: dict, sd: dict):
    # This is also stupid since we will add other types later
    title = "# Service Requests \n"
    # import pdb; pdb.set_trace()
    subtitle = (
        "## " + " - ".join([f"**{key}**: {val}" for key, val in sr.items()]) + "\n"
    )
    # This happens if there is nothing in the description
    # I just add a simple "No Description" str
    if type(sd) is dict:
        body = "*" + "*".join(
            [f" **{k1}**: {v2} \n" for k1, v2 in zip(SHORTHAND_DESC, list(sd.values()))]
        )
    else:
        body = sd
    md_format = [title, subtitle, body]
    return md_format


def convert_sr_to_md(
    service_request: list, service_description: list, outfile: str = "file_out.md"
):
    print(f"Convert to md: {outfile}.md")
    with open(f"{outfile}.md", "w") as f:
        for sr, sd in zip(service_request, service_description):
            md_local = convert_to_md(sr, sd)
            f.writelines(md_local)
    return 0
