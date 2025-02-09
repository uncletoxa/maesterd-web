def pc_to_str(d, parent_key="", sep="."):
    items = []
    for k, v in d.items():
        new_key = f"{parent_key}{sep}{k}" if parent_key else k
        if isinstance(v, dict):
            items.append(pc_to_str(v, new_key, sep))
        elif isinstance(v, list):
            items.append(f"{new_key}={', '.join(map(str, v))}")
        else:
            items.append(f"{new_key}={v}")
    return "\n".join(items)
