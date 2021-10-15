#!/usr/bin/env python3

import sys
import os
import argparse
import re

from common import *

def _log(s):
  print(s)

class IncompatibleHEDFile(Exception):
  """ Raised when input HED file can't be processed """
  pass

def main(args):

  hed = args.hed
  wad = args.wad
  export_path = args.export
  list_only = args.list_only

  _log("Checking for %s" % export_path)
  if not os.path.exists(export_path):
    raise PathNotFound("Export path not found: %s" % export_path)
    pass

  _log("Checking for CD.HED")
  if not os.path.exists(hed):
    raise PathNotFound("CD.HED not found: %s" % hed)
    pass

  if not wad:
    # imply cd.wad from cd.hd
    _log("--wad was not passed, using --hed location")
    wad = "%s.WAD" % os.path.splitext(hed)[0]
    _log("wad file is now: %s" % wad)

  _log("Checking for CD.WAD")
  if not os.path.exists(wad):
    raise PathNotFound("CD.WAD not found: %s" % wad)
    pass

  # Open the HED file
  with open(hed, "rb") as f:

    # Get file size to know where it ends
    f.seek(0, os.SEEK_END)
    file_size = f.tell()
    f.seek(0)

    # Also open the WAD file
    with open(wad, "rb") as fw:

      # Loop over HED entries
      while f.tell() < file_size - 7:
        name = read_string(f)
        try:
          # hacky filename check
          if not re.match('^[A-Za-z0-9-.].+', name):
            raise IncompatibleHEDFile ("Failed to decode a reasonable filename, this hed isn't compatible")
        except IncompatibleHEDFile as e:
          _log(e)
          exit(1)

        #FIXME: Check for terminator?
        align(f, 4)
        offset = read32(f)
        size = read32(f)

        fw.seek(offset)


        if not list_only:
          # Construct path
          file_export_path = os.path.join(export_path, name)


          # Extract file
          _log("Extracting %s" % file_export_path)
          with open(file_export_path, "wb") as fo:
            data = fw.read(size)
            fo.write(data)

        _log("HED Found: file=%s offset=%s" % (name, f.tell()) )

    terminator = read8(f)
    assert(terminator == 0xFF)


if __name__ == "__main__":
  parser = argparse.ArgumentParser(description='Options')
  parser.add_argument('--hed', required=True, default=False, type=str,
                      help='cd.hed file to process')
  parser.add_argument('--wad', required=False, default=False, type=str,
                      help='cd.wad file to pocess, implied from --hed if not passed')
  parser.add_argument('--export', required=True, default=False, type=str,
                      help='output path for extracted files')
  parser.add_argument('--list-only', const=True, required=False, default=False, type=bool, nargs="?",
                      help='do not extract, just list findings')
  main(parser.parse_args())
