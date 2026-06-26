import json

with open("data/service_requests.json") as f:
    data = json.load(f)

data = data[0]


def flatten_dict(metadata, parent_key="", sep=".") -> dict:
    flat_dict = {}
    for k, v in metadata.items():
        new_key = f"{parent_key}{sep}{k}" if parent_key else k
        if isinstance(v, dict):
            flat_dict.update(flatten_dict(v, new_key, sep=sep))
        else:
            flat_dict[new_key] = v
    return flat_dict


data = flatten_dict(data)

for k, v in data.items():
    data[k] = " "

with open("data/ilab_metadata_fields.json", "w") as f:
    json.dump(data, f)
