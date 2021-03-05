#!/usr/bin/env python3

from subprocess import run
import sys

"""
This would've been a simple requirements.txt file, but we can't install cdsapi in one command
"""

cdsapi_chain = [
    ["six", "appdirs", "packaging", "wheel"],
    ["ordered_set"],
    ["cdsapi"],
]

normal_deps = [
        "requests",
]

def pip_install(pkgs):
    cmd = ["pip3", "install", "--disable-pip-version-check", *pkgs]
    print("$ " + " ".join(cmd))
    sys.stdout.flush()
    run(cmd)

pip_install(normal_deps)

for link in cdsapi_chain:
    pip_install(link)
