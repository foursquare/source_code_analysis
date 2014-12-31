# coding=utf-8
# Copyright 2011 Foursquare Labs Inc. All Rights Reserved.

from __future__ import (nested_scopes, generators, division, absolute_import, with_statement,
                        print_function, unicode_literals)


class SourceEdit(object):
  """Represents an edit to a source file."""
  def __init__(self, filename, line_num, reason):
    self.filename = filename
    self.line_num = line_num
    self.reason = reason

  def __repr__(self):
    return '{0}:{1}: {2}'.format(self.filename, self.line_num, self.reason)


class RewriteCursor(object):
  """Represents the source text, the rewritten text so far, and the current position in the source text."""
  def __init__(self, filename, src_text):
    self.filename = filename
    self.src_text = src_text
    self.src_pos = 0
    self.src_line_num = 1
    self.new_text = ''
    self.edits = []

  def set_src_pos(self, src_pos):
    self.src_pos = src_pos

  def emit(self, new_text, reason=None):
    self.new_text += new_text
    if reason is not None:
      self.edits.append(SourceEdit(self.filename, self.src_line_num, reason))

  def copy_from_src_until(self, endpos):
    self.emit(self.src_text[self.src_pos:endpos])
    self.set_src_pos(endpos)
    self.src_line_num = 1 + self.src_text.count('\n', 0, endpos)

  def finish(self):
    self.new_text += self.src_text[self.src_pos:]
    self.src_pos = len(self.src_text)

