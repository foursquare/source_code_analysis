# coding=utf-8
# Copyright 2013 Foursquare Labs Inc. All Rights Reserved.

from __future__ import (nested_scopes, generators, division, absolute_import, with_statement,
                        print_function, unicode_literals)

import logging
import os
import re

from foursquare.source_code_analysis.rewrite_cursor import RewriteCursor
from foursquare.source_code_analysis.source_file_scanner import SourceFileScanner


log = logging.getLogger()

_BLANK_LINE_PATTERN = '[ \t]*\n'

_BLANK_LINE_RE = re.compile(_BLANK_LINE_PATTERN)


class SourceFileRewriter(SourceFileScanner):
  """Base class that applies rewrites to source files."""
  def __init__(self, backup):
    super(SourceFileRewriter, self).__init__()
    self._backup = backup

  def scan_text(self, file_path, old_text):
    new_text = self.apply_to_text(file_path, old_text).new_text
    if new_text != old_text:
      if self._backup:
        os.rename(file_path, file_path + '.bak')
      with open(file_path, 'w') as outfile:
        outfile.write(new_text)
      log.info('Rewrote file {0}'.format(file_path))
    else:
      log.debug('Nothing to rewrite in file {0}'.format(file_path))

  def apply_to_text(self, filename, src_text):
    rewrite_cursor = RewriteCursor(filename, src_text)
    self.apply_to_rewrite_cursor(rewrite_cursor)
    return rewrite_cursor

  def apply_to_rewrite_cursor(self, rewrite_cursor):
    raise NotImplementedError('Implement rewriting logic here')

  def skip_blank_lines(self, rewrite_cursor):
    """Skips the cursor over any blank lines. Does not emit anything.

    Returns the number of blank lines skipped.
    """
    n = 0
    m = _BLANK_LINE_RE.match(rewrite_cursor.src_text, rewrite_cursor.src_pos)
    while m is not None:
      rewrite_cursor.set_src_pos(m.end())
      n += 1
      m = _BLANK_LINE_RE.match(rewrite_cursor.src_text, rewrite_cursor.src_pos)
    return n
