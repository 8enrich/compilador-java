import os

PATH = os.getcwd()

def get_absolute_filename(filename: str) -> str:
    return PATH + "/" + filename

def test(filename: str):
    print(f"Testando arquivo {filename}")
    print()
    os.system(f"python3 {get_absolute_filename("javapy.py")} {get_absolute_filename("java-files/" + filename)}")
    print()

def tests(files: list[str]):
    for filename in files:
        test(filename)

files = sorted(os.listdir("./java-files/"))
tests(files)
