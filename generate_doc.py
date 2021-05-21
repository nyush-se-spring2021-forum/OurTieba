import os
import shutil
import subprocess
from glob import glob


def extract_name(path_, depth=1):
    separator = "\\" if os.name == 'nt' else "/"  # different path separators for different OS
    path_split_list = path_.split(separator)
    real_name = path_split_list[-1][:-3]
    relative_name = ".".join(path_split_list[-depth:-1] + [real_name])
    name = "ourtieba." + relative_name
    return name


if not os.path.exists("docs"):
    os.mkdir("docs")

file_list = []
for path in glob("ourtieba/*.py", recursive=True):
    file_list.append(extract_name(path))
for path in glob("ourtieba/*/*.py", recursive=True):
    file_list.append(extract_name(path, depth=2))

for file in file_list:
    python_name = "python" if os.name == "nt" else "python3"
    proc = subprocess.Popen(python_name + " -m pydoc -w " + file, shell=True)
    proc.communicate()  # synchronize
    shutil.move(file + ".html", "docs")
