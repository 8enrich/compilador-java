
def error(filename, errors):
    with open(filename, "r") as file:
        lines = file.readlines()
    for error in errors:
        _, error_token, error_str, line = error
        error_line = lines[line - 1]
        i, j = 0, len(error_token)
        while j < len(error_line):
            if error_token == error_line[i:j]: break
            i += 1
            j += 1
        print(f"{filename}:{line}: error: {error_str}")
        print(error_line, end="")
        print(" " * i + "^")
    print(f"{len(errors)} error")
    print("error: compilation failed")
