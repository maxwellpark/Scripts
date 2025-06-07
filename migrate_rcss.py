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
        next_line = lines[i + 1].strip() if i + 1 < len(lines) else ""
        match = re.match(r"\s*([a-zA-Z0-9_-]+-image):\s*([a-zA-Z0-9_-]+\.png);", next_line)
        if not match:
            print("no match for image-src " + next_line)
            return None
        
        new_decorator = f"\tdecorator: {decorator}({match.group(2)});"
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

def migrate(path: Path, full_migrate: bool):
    lines = path.read_text(encoding="utf-8").splitlines()
    i = 0
    edits = []
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

        # mouse-capture property removed in rml 
        if re.match(r"\s*mouse-capture:\s*\d;\s*", line):
            lines.pop(i)
            continue

        result = transform_decorator_block(lines, i)
        if result:
            edits.append(result)
            i = result["end"]
        else:
            next_line = lines[i + 1].strip() if i + 1 < len(lines) else ""
            match = re.match(r"\s*([a-zA-Z0-9_-]+-image):\s*([a-zA-Z0-9_-]+\.png);", next_line)
            if match:
                new_decorator = f"\tdecorator: image({match.group(2)});"
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

        if full_migrate:
            path.write_text("\n".join(new_lines), encoding="utf-8")
            print(f"transformed: {path}")
        else:
            new_filename = path.stem + "_migrated.rcss"
            new_path = path.with_name(new_filename)
            new_path.write_text("\n".join(new_lines), encoding="utf-8")
            print(f"transformed: {new_path}")
    else:
        print(f"no changes: {path}")

def migrate_recursively(directory: Path, full_migrate: bool):
    for file in directory.rglob("*.rcss"):
        migrate(file, full_migrate)

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("directory", help="Directory to migrate rcss files in recursively")
    parser.add_argument("--full-migrate", action="store_true", help="Wet run vs. dry run (wihout flag)")

    args = parser.parse_args()
    print(args)
    migrate_recursively(Path(args.directory), args.full_migrate)
