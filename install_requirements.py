#!/usr/bin/env python3

from subprocess import run

cdsapi_chain = [
    ["six", "appdirs", "packaging", "wheel"],
    ["ordered_set"],
    ["cdsapi"],
]

normal_deps = ["requests", "pygrib"]

def pip_install(pkgs):
    cmd = ["pip", "install", *pkgs]
    print("$ " + " ".join(cmd))
    run(cmd)

pip_install(normal_deps)

for link in cdsapi_chain:
    pip_install(link)
