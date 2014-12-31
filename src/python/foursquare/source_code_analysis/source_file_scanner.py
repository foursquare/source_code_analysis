# coding=utf-8
# Copyright 2013 Foursquare Labs Inc. All Rights Reserved.

from __future__ import (nested_scopes, generators, division, absolute_import, with_statement,
                        print_function, unicode_literals)

import logging
import os


log = logging.getLogger()

class SourceFileScanner(object):
  """Base class that rips over source files and applies scanning operations."""

  # The file extension of source files this class recognizes. E.g., '.scala'.
  # Subclasses must define.
  ext = None

  def apply_to_source_files(self, file_or_directory_paths):
    for file_or_directory_path in file_or_directory_paths:
      if os.path.isdir(file_or_directory_path):
        for root, dirs, files in os.walk(file_or_directory_path):
          for f in files:
            self.apply_to_source_file(os.path.join(root, f))
      else:
        self.apply_to_source_file(file_or_directory_path)
    self.all_files_scanned()

  def apply_to_source_file(self, file_path):
    if not file_path.endswith(self.ext):
      log.debug('Skipping non-{0} file {1}'.format(self.ext, file_path))
      return
    if not os.path.exists(file_path):
      log.debug('Skipping non existing file {0}'.format(file_path))
      return
    log.debug('Opening file {0}'.format(file_path))
    with open(file_path, 'r') as infile:
      text = infile.read()
      try:
        self.scan_text(file_path, text)
      except Exception:
        log.error('failed in {0}'.format(file_path))
        raise

  def scan_text(self, file_path, text):
    raise NotImplementedError('Implement scanning logic here.')

  def all_files_scanned(self):
    """Implement this to get a callback when all files have been scanned."""
    pass
