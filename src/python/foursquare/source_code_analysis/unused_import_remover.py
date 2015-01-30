# coding=utf-8
# Copyright 2012 Foursquare Labs Inc. All Rights Reserved.

from __future__ import absolute_import

import logging

from foursquare.source_code_analysis.source_file_rewriter import SourceFileRewriter


VERSION = '0.1'

log = logging.getLogger()


class UnusedImportRemover(SourceFileRewriter):
  """
  Base class for import removers.

  Overwrites the original file. Use with caution.
  """
  def __init__(self, backup, import_parser):
    super(UnusedImportRemover, self).__init__(backup)
    self._source_text = ''
    self.import_parser = import_parser

  def apply_to_text(self, filename, source_text):
    # Grab the full source content, so we can check it for use of imports.
    self._source_text = self.process_source_text(source_text)
    return super(UnusedImportRemover, self).apply_to_text(filename, source_text)

  def apply_to_rewrite_cursor(self, rewrite_cursor):
    import_clause = self.import_parser.search(rewrite_cursor)
    while import_clause is not None:
      new_import, removed_import_names = self.check_for_usage(import_clause)
      reason = None
      if removed_import_names:
        reason = 'Unused imports: ' + ', '.join(removed_import_names)
      rewrite_cursor.emit(new_import, reason)
      import_clause = self.import_parser.search(rewrite_cursor)

  def check_for_usage(self, import_clause):
    """Returns the import_clause with unused imports removed, and a list of the names of the removed imports.

    Returns None if no unused imports were detected.
    """
    raise Exception('Implement usage checkin logic here')

  def process_source_text(self, source_text):
    """
    Subclasses can manipulate the source text here
    """
    return source_text

