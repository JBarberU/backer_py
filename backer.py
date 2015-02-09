#!/usr/bin/env python

import os
import sys
import json
import subprocess
import datetime

rsync_key = "rsync"
archive_key = "archive"
backup_file = ".backer.json"

def mkdir(host, dst):
    # mkdir
    mkdir_p = subprocess.Popen(["ssh", host, "mkdir -p {}".format(dst)])
    mkdir_p.wait()

def rsync(list):
  for l in list:
    src = l["src"]
    src_name = src.split("/")[-1]           # (filename)
    src_dir = "/".join(src.split("/")[:-1]) # equivalent to dirname(src)
    host = l["dst"].split(":")[0]
    dst = "{0}/{1}".format(l["dst"].split(":")[1], src_name)

    print("Backing up: {0} (rsync)".format(src_name))

    mkdir(host, dst)

    p = subprocess.Popen(["rsync", "-avh", l["src"], l["dst"]])
    p.wait()

def archive(list):
  for l in list:
    src = l["src"]
    src_name = src.split("/")[-1]           # (filename)
    src_dir = "/".join(src.split("/")[:-1]) # equivalent to dirname(src)

    print("Backing up: {0} (archive)".format(src_name))

    host = l["dst"].split(":")[0]
    dst = "{0}/{1}".format(l["dst"].split(":")[1], src_name)

    d = datetime.datetime.now()
    tar = "{0}.{1}{2}{3}_{4}{5}{6}.tar.gz".format(src_name, d.year, d.month, d.day, d.hour, d.minute, d.second)

    mkdir(host, dst)

    # tar to destination
    tar_p = subprocess.Popen(["tar", "czf", "-", src_name], cwd=src_dir, stdout=subprocess.PIPE)
    ssh_p = subprocess.Popen(["ssh", host, "cat >> {0}/{1}".format(dst, tar)], stdin=tar_p.stdout)

    tar_p.stdout.close()
    ssh_p.wait()

def main():
  path = "{0}/{1}".format(os.environ["HOME"], backup_file) 
  if not os.path.exists(path):
    json_obj = {"comment": "the rsync key should contain a list of ojects using the following format:"}
    json_obj["rsync_example"] = [{"src": "/Some/full/path", "dst": "user@somehost:target/dir"}] 
    json_obj[rsync_key] = []
    json_obj[archive_key] = []
    with open(path, "w") as f:
      json.dump(json_obj,indent=2, separators=[',',': '], fp=f)
    print("Created {}".format(path))
    return

  lines = ""
  with open(path, "r") as f:
    json_obj = json.load(f)

  rsync(json_obj[rsync_key])
  archive(json_obj[archive_key])
  print("Done!")

if __name__ == "__main__":
  main()

