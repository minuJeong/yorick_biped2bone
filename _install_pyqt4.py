
import sys
import os
import urllib
import subprocess


try:
    import pip

except Exception as e:
    print("PIP not found, installing..")

    # get path to .temp/get-pip.py
    dirpath = "{}/.temp".format(os.path.dirname(__file__))
    if not os.path.exists(dirpath):
        print("creating .temp directory for caching")
        os.makedirs(dirpath)
    get_pip_path = "{}/get-pip.py".format(dirpath)

    # download get-pip.py
    if not os.path.exists(get_pip_path):
        print("get-pip.py not found, downloading..")

        get_pip_url = "https://bootstrap.pypa.io/get-pip.py"
        res = urllib.urlopen(get_pip_url)
        with open(get_pip_path, 'w') as fp:
            fp.write(res.read())

    print("installing pip..")
    command = [
        "runas",
        "/env",
        "/user:admin",
        sys.executable,
        get_pip_path.replace('\\', '/')
    ]

    print("COMMAND: ", command)
    subprocess.call(' '.join(command))

    print("pip installed!")
    import pip

print("PIP: ", pip)
print("PIP.MAIN: ", pip.main)
pip.main(["install", "--user", "PySide"])
