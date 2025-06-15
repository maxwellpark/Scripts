import re
import sys

def uncomment(lines):
    output = []
    inside_layer_block = False

    for line in lines:
        stripped = line.strip()

        if not inside_layer_block:
            if re.match(r"/\*\s*background-decorator:\s*layer-decorator;", stripped):
                inside_layer_block = True
                output.append(line.replace("/*", "", 1))
            else:
                output.append(line)
        else:
            if "*/" in line:
                inside_layer_block = False
                output.append(line.replace("*/", "", 1))
            else:
                output.append(re.sub(r"^\s*\*?\s*", lambda m: m.group(0).replace("/*", "").replace("*", ""), line))

    return output

def image_replace(lines): 
    output = []
    inside_block = False
    block_lines = []

    for line in lines:
        stripped = line.strip()

        if not inside_block:
            if stripped.endswith('{'):
                inside_block = True
                block_lines = [line]
            else:
                output.append(line)
            continue

        block_lines.append(line)

        if '}' in stripped:
            new_block = []
            image_filename = extract_image_src(block_lines)
            replaced = False

            for block_line in block_lines:
                if 'decorator:' in block_line and 'layer-decorator' in block_line:
                    if image_filename:
                        indent = re.match(r'^(\s*)', block_line).group(1)
                        new_block.append(f'{indent}decorator: image("{image_filename}");\n')
                        replaced = True
                    else:
                        new_block.append(block_line)
                        replaced = True
                else:
                    new_block.append(block_line)

            if not replaced and image_filename:
                for j, block_line in enumerate(new_block):
                    if '{' in block_line:
                        indent = re.match(r'^(\s*)', new_block[j + 1]).group(1) if j + 1 < len(new_block) else '    '
                        new_block.insert(j + 1, f'{indent}decorator: image("{image_filename}");\n')
                        break

            output.extend(new_block)
            inside_block = False
            block_lines = []
    return output

def extract_image_src(block_lines):
    pattern = re.compile(r'layer-\d+-texture-0\s*:\s*("?)([^";]+)\1\s*;')
    for line in block_lines:
        match = pattern.search(line.strip())
        if match:
            return match.group(2)
    return None

def add_definitions(lines):
    output = []
    inside_block = False
    block_lines = []
    block_needs_decorator = False
    block_has_decorator = False

    for line in lines:
        stripped = line.strip()

        if not inside_block and re.match(r'^.+\s*\{', stripped):
            inside_block = True
            block_lines = [line]
            block_needs_decorator = False
            block_has_decorator = False
            continue

        if inside_block:
            block_lines.append(line)

            if 'layer-' in stripped or 'layer_' in stripped:
                block_needs_decorator = True
            if 'decorator:' in stripped:
                block_has_decorator = True

            if '}' in stripped:
                if block_needs_decorator and not block_has_decorator:
                    for j, block_line in enumerate(block_lines):
                        if '{' in block_line:
                            indent = re.match(r'^(\s*)', block_lines[j + 1]).group(1) if j + 1 < len(block_lines) else '    '
                            block_lines.insert(j + 1, f'{indent}decorator: layer-decorator;\n')
                            break
                output.extend(block_lines)
                inside_block = False
                block_lines = []
                continue
            continue
        
        output.append(line)
    return output

def process(path):
    with open(path, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    # updated_lines = uncomment(lines)
    # updated_lines = add_definitions(lines)
    updated_lines = image_replace(lines)

    with open(path, 'w', encoding='utf-8') as f:
        f.writelines(updated_lines)

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("python layer_decorators.py <file.rcss>")
    else:
        process(sys.argv[1])
        print(f"written to: {sys.argv[1]}")
