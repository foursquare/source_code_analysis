# coding=utf-8
# Copyright 2011 Foursquare Labs Inc. All Rights Reserved.

from __future__ import (nested_scopes, generators, division, absolute_import, with_statement,
                        print_function, unicode_literals)

import logging
import optparse

from foursquare.source_code_analysis.exception import SourceCodeAnalysisException
from foursquare.source_code_analysis.scala.scala_import_parser import PathValidator, ScalaImportParser
from foursquare.source_code_analysis.scala.scala_imports import ScalaImportClause, ScalaSymbolPath
from foursquare.source_code_analysis.scala.scala_source_file_rewriter import ScalaSourceFileRewriter


VERSION = '0.1'


log = logging.getLogger()


class ScalaImportRewriteRule(object):
  """How to rewrite an import."""
  def __init__(self, from_string, to_string):
    self.from_path = ScalaSymbolPath(from_string)  # Rewrite imports of this symbol...
    self.to_path = ScalaSymbolPath(to_string)  # ... to this symbol.


class ScalaImportRewriter(ScalaSourceFileRewriter):
  """Rewrites imports in scala source files.

  Handles all import forms, e.g.,:

  import foo.bar.Baz
  import foo.bar.{Baz, Qux}
  import foo.bar.{Baz, Qux => Quux}

  Notes:

  - Only rewrites imports that are on a line on their own. This should be virtually all imports we encounter in
    practice, but technically Scala allows inline imports, e.g., if (x > 0) { import java.util.Vector; }.

  - Overwrites the original file. Use with caution.

  - Does not handle imports with embedded or trailing comments.

  - Does not regroup/reorder imports. scala_import_sorter does that.

  - Does not removed unused imports. scala_unused_import_remover does that.

  - We use semi-naive regexps, so this may not do what you expect in very extreme corner cases. For example,
    it will rewrite some malformed, syntactically incorrect import statements, but not others.
    You definitely want to eyeball all changes made by this script before committing them.


  USAGE: python src/python/foursquare/source_code_analysis/scala/scala_import_rewriter.py --nobackup --rewrite_from=foo.bar.Baz --rewrite_to=foo.qux.Baz <files_or_directories>

  (don't forget to put the code on your PYTHONPATH).
  """
  def __init__(self, rewrite_rule, backup):
    super(ScalaImportRewriter, self).__init__(backup)
    self._rewrite_rule = rewrite_rule

  def apply_to_rewrite_cursor(self, rewrite_cursor):
    import_clause = ScalaImportParser.search(rewrite_cursor)
    while import_clause is not None:
      rewritten_clauses = self.apply_rewrite(import_clause)
      if rewritten_clauses is None:
        # Spit out the original text, with any wrapping, whitespace or other idiosyncracies it may have. This makes
        # sure that We only modify files where needed, and not just because of such non-germane differences.
        rewrite_cursor.emit(import_clause.src_text)
      else:
        new_text = '\n'.join([repr(x) for x in rewritten_clauses]) + '\n'
        rewrite_cursor.emit(new_text)
      import_clause = ScalaImportParser.search(rewrite_cursor)

  def apply_rewrite(self, import_clause):
    """Returns a list of ScalaImportClause objects containing the rewritten imports from the input clause.

    Note that a rewrite may turn one clause into more than one, e.g., applying foo.bar.Qux -> foo.qux.Qux:
    import foo.bar.{Baz, Qux}  -> import foo.bar.Baz
                                  import foo.qux.Qux
    """
    clauses = []

    def _find_clause(path_string):
      for clause in clauses:
        if clause.path.path_string == path_string:
          return clause
      return None

    def _find_or_create_clause(path_string):
      ret = _find_clause(path_string)
      if ret is None:
        ret = ScalaImportClause(import_clause.indent, path_string)
        clauses.append(ret)
      return ret

    rewritten = False
    for scala_import in import_clause.imports:
      maybe_rewritten_import = scala_import.get_maybe_rewritten_import(self._rewrite_rule)
      if maybe_rewritten_import != scala_import:
        rewritten = True
      clause = _find_or_create_clause('.'.join(maybe_rewritten_import.path.get_all_but_name()))
      clause.add_import(maybe_rewritten_import.path.get_name(), maybe_rewritten_import.as_name)

    if not rewritten:
      return None  # So we don't change the wrapping etc. of imports that weren't otherwise rewritten.
    else:
      return clauses

def get_command_line_args():
  opt_parser = optparse.OptionParser(usage='%prog [options] scala_source_file_or_dir(s)', version='%prog ' + VERSION)
  opt_parser.add_option('--log_level', type='choice', dest='log_level', choices=['DEBUG', 'INFO', 'WARNING', 'ERROR'],
    default='INFO', help='Log level to display on the console.')
  opt_parser.add_option('--rewrite_from', type='string', dest='rewrite_from', metavar='foo.bar.Baz',
    help='import to rewrite')
  opt_parser.add_option('--rewrite_to', type='string', dest='rewrite_to', metavar='foo.qux.Baz',
    help='rewrite the import to this')
  opt_parser.add_option('--nobackup', action='store_true', dest='nobackup', default=False,
    help='If unspecified, we back up modified files with a .bak suffix before rewriting them.')

  (options, args) = opt_parser.parse_args()

  if not options.rewrite_from:
    opt_parser.error('Must specify --rewrite_from')
  if not options.rewrite_to:
    opt_parser.error('Must specify --rewrite_to')

  if not PathValidator.validate(options.rewrite_from):
    opt_parser.error('--rewrite_from must be of the form foo.bar.Baz')
  if not PathValidator.validate(options.rewrite_to):
    opt_parser.error('--rewrite_to must be of the form foo.bar.Baz')

  if len(args) == 0:
    opt_parser.error('Must specify at least one scala source file or directory to rewrite')

  return options, args


def main(options, scala_source_files):
  numeric_log_level = getattr(logging, options.log_level, None)
  if not isinstance(numeric_log_level, int):
    raise SourceCodeAnalysisException('Invalid log level: {0}'.format(options.log_level))
  logging.basicConfig(level=numeric_log_level)
  import_rewriter = ScalaImportRewriter(ScalaImportRewriteRule(options.rewrite_from, options.rewrite_to),
                                        not options.nobackup)
  import_rewriter.apply_to_source_files(scala_source_files)
  log.info('Done!')


if __name__ == '__main__':
  (options, args) = get_command_line_args()
  main(options, args)
