import sys

def char_positions(input_str, indexes):
    # 0-based 
    adjusted_indexes = [index - 1 for index in indexes]

    for index in adjusted_indexes:
        if 0 <= index < len(input_str):
            print(input_str[index])
        else:
            print(f"index {index + 1} out of bounds")

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("python script.py <input_str> <index1> <index2> ...")
        sys.exit(1)

    input_str = sys.argv[1]
    indexes = list(map(int, sys.argv[2:]))
    char_positions(input_str, indexes)
