import re
from pathlib import Path

DECORATOR_PROPS = {
    "tiled-box": [
        "background-top-left-image",
        "background-top-image",
        "background-top-right-image",
        "background-left-image",
        "background-center-image",
        "background-right-image",
        "background-bottom-left-image",
        "background-bottom-image",
        "background-bottom-right-image",
    ],
    "tiled-horizontal": [
        "background-left-image",
        "background-center-image",
        "background-right-image",
    ],
    "tiled-vertical": [
        "background-top-image",
        "background-center-image",
        "background-bottom-image",
    ],
    "image": [
        "image-src",
    ]
}

def normalize(val):
    return re.sub(r"\s+", " ", val.strip())

def transform_decorator_block(lines, i):
    line = lines[i]
    # print("line = " + line)
    match = re.match(r"\s*(\S+)-decorator:\s*([a-zA-Z0-9_-]+)\s*;?\s*", line)
    if not match:
        return None
    
    # print("match = " + str(match))
    decorator = match.group(2)
    print("decorator = " + decorator)
    props = DECORATOR_PROPS.get(decorator)
    if not props:
        print("no decorator matched " + decorator)
        return None

    end = i + 1
    collected = {}
    
    if decorator == "image":
        next_line = lines[i + 1].strip()
        match = re.match(r"background-image:\s*([a-zA-Z0-9_-]+\.png);", next_line)
        if not match:
            print("no match for image-src " + next_line)
            return None
        
        new_decorator = f"\tdecorator: {decorator}({match.group(1)});"
        lines.pop(i + 1)
    else:
        for j in range(i + 1, min(i + 20, len(lines))):
            for prop in props:
                prop_match = re.match(rf"\s*{re.escape(prop)}\s*:\s*(.+);", lines[j])
                if prop_match:
                    collected[prop] = normalize(prop_match.group(1))
                    end = j + 1
            if lines[j].strip() == "}" or len(collected) == len(props):
                break
        
        if not collected:
            return None
        
        # print(collected)
        values = [collected.get(prop, "none") for prop in props]
        new_decorator = f"\tdecorator: {decorator}({', '.join(values)});"
    
    return {
        "start": i,
        "end": end,
        "replacement": [new_decorator]
    }

def migrate_rcss_file(path: Path):
    lines = path.read_text(encoding="utf-8").splitlines()
    i = 0
    edits = []
    block_started = False
    inside_comment = False

    while i < len(lines):
        line = lines[i].strip()

        # skip commented out sections
        if inside_comment:
            if "*/" in line:
                inside_comment = False
            i += 1
            continue

        if line.startswith("/*"):
            inside_comment = True
            i += 1
            continue

        if line.startswith("//"):
            i += 1
            continue

        result = transform_decorator_block(lines, i)
        if result:
            edits.append(result)
            i = result["end"]
        else:
            next_line = lines[i + 1].strip() if i + 1 < len(lines) else ""
            match = re.match(r"background-image:\s*([a-zA-Z0-9_-]+\.png);", next_line)
            if match:
                new_decorator = f"\tdecorator: image({match.group(1)});"
                lines.pop(i + 1)
                edits.append({
                    "start": i + 1,
                    "end": i + 1,
                    "replacement": [new_decorator]
                })
            i += 1

    if edits:
        new_lines = []
        idx = 0
        for edit in edits:
            new_lines.extend(lines[idx:edit["start"]])
            new_lines.extend(edit["replacement"])
            idx = edit["end"]
        new_lines.extend(lines[idx:])
        
        for idx in range(len(new_lines)):
            if new_lines[idx].strip() == "decorator:" and (idx == 0 or new_lines[idx-1].strip() != "{"):
                new_lines.insert(idx, "{")
                block_started = True
                break
        
        if new_lines[-1].strip() != "}":
            new_lines.append("}")

        if not block_started:
            new_lines.insert(0, "{")
            new_lines.append("}")

        new_filename = path.stem + "_migrated.rcss"
        new_path = path.with_name(new_filename)
        
        new_path.write_text("\n".join(new_lines), encoding="utf-8")
        print(f"transformed: {new_path}")
    else:
        print(f"no changes: {path}")

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("files", nargs="+", help="RCSS file(s) to migrate")
    args = parser.parse_args()
    
    if len(args.files) < 1:
        print("python rcss_migrate_decorators.py <path/to/file1.rcss> <path/to/file2.rcss>")

    for f in args.files:
        migrate_rcss_file(Path(f))
