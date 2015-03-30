# coding=utf-8
# Copyright 2012 Foursquare Labs Inc. All Rights Reserved.

from __future__ import absolute_import

import logging
import re

from foursquare.source_code_analysis.scala.scala_source_file_rewriter import ScalaSourceFileRewriter
from foursquare.source_code_analysis.scala.scala_import_parser import ScalaImportParser
from foursquare.source_code_analysis.scala.scala_imports import ScalaSymbolPath
from foursquare.source_code_analysis.scala.scala_import_parser import IMPORT_RE


VERSION = '0.1'

log = logging.getLogger()

class BaseUnusedImportRemover(ScalaSourceFileRewriter):
  """
  Base class for import removers.

  Overwrites the original file. Use with caution.
  """
  def __init__(self, backup, import_parser):
    super(BaseUnusedImportRemover, self).__init__(backup)
    self._source_text = ''
    self.import_parser = import_parser

  def apply_to_text(self, filename, source_text):
    # Grab the full source content, so we can check it for use of imports.
    self._source_text = self.process_source_text(source_text)
    return super(BaseUnusedImportRemover, self).apply_to_text(filename, source_text)

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

class ScalaUnusedImportRemover(BaseUnusedImportRemover):
  """Removes unused imports.

  An import is heuristically considered unused if:

  1) It is not a wildcard import.
  2) It is not an import of a method.

  The reason is that these imports may bring implicits into scope, and we can't detect usage of implicits without
  full compiler analysis. However a regular import foo.Bar in a file with no reference to Bar should be safe to remove.

  We detect that an import is not of a method by checking if the first character is upper case, indicating,
  by convention, a type or an object. Note that this heuristic fails if a method does not use this convention, or
  in case of an implicit object. However these are rare in our codebase, and the known instances are special-cased
  below. In any case, the compiler should yell if this heuristic fails.

  Overwrites the original file. Use with caution.
  """
  def __init__(self, backup):
    super(ScalaUnusedImportRemover, self).__init__(backup, ScalaImportParser)

  excluded_paths = [ ScalaSymbolPath('scalaj.collection.Implicits') ]

  def check_for_usage(self, import_clause):
    removed_import_names = []
    for scala_import in import_clause.imports:
      if len(filter(lambda x: x.is_prefix_of(scala_import.path) is not None,
                    ScalaUnusedImportRemover.excluded_paths)) == 0:
        name = scala_import.get_name()
        if name[0].isupper():  # Only rewrite imports that appear to be of types, not functions or wildcards.
          # Search for any appearance not immediately preceeded or followed by alphanumeric or underscore
          # characters (so we don't match Bar in FooBar and so on).
          if re.search('\W%s\W' % name, self._source_text) is None:
            removed_import = import_clause.remove_import(name)
            removed_import_names.append(repr(removed_import))

    if len(removed_import_names) > 0:
      rewritten_clause = import_clause
    else:
      rewritten_clause = None
      removed_import_names = []

    if rewritten_clause is None:
      # Spit out the original text, with any wrapping, whitespace or other idiosyncracies it may have. This makes
      # sure that We only modify files where needed, and not just because of such non-germane differences.
      new_import = import_clause.src_text
    else:
      if len(rewritten_clause.imports) > 0:
        new_import = repr(rewritten_clause) + '\n'
      else:
        new_import = ''
    return new_import, removed_import_names

  def process_source_text(self, source_text):
    # Strip out all the imports, so we don't false-positive on them.
    return IMPORT_RE.sub('', source_text)
