import re
from pathlib import Path

DECORATOR_PROPS = {
    "image": [
        "image-src",
    ]
}

def normalize(val):
    return re.sub(r"\s+", " ", val.strip())

def transform_decorator_block(lines, i):
    line = lines[i]
    line = line.strip()
    print(line)

    if "background-decorator: image" not in line:
        return None
    
    next_line = lines[i + 1].strip() if i + 1 < len(lines) else ""
    match = re.match(r"\s*background-image:\s*([a-zA-Z0-9_-]+\.png)\s*(.*);", next_line)
    if match:
        new_decorator = f"\t\tdecorator: image(\"{match.group(1).strip()}\" {match.group(2).strip()});"
        lines.pop(i + 1)
    else:
        new_decorator = None
    return {
        "start": i,
        "end": i + 1,
        "replacement": [new_decorator]
    }

def migrate(path: Path, full_migrate: bool):
    lines = path.read_text(encoding="utf-8").splitlines()
    i = 0
    edits = []
    inside_comment = False

    while i < len(lines):
        line = lines[i].strip()

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
            new_filename = path.stem + "_migrated.rml"
            new_path = path.with_name(new_filename)
            new_path.write_text("\n".join(new_lines), encoding="utf-8")
            print(f"transformed: {new_path}")
    else:
        print(f"no changes: {path}")

def migrate_recursively(directory: Path, full_migrate: bool):
    for file in directory.rglob("*.rml"):
        migrate(file, full_migrate)

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("directory", help="Directory to apply migration recursively to .rml files")
    parser.add_argument("--full-migrate", action="store_true", help="Perform full migration (overwrite original files)")

    args = parser.parse_args()

    migrate_recursively(Path(args.directory), args.full_migrate)
