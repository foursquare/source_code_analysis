# coding=utf-8
# Copyright 2012 Foursquare Labs Inc. All Rights Reserved.

from __future__ import absolute_import

import logging
import optparse
import re

from foursquare.source_code_analysis.scala_import_parser import IMPORT_RE, ScalaImportParser
from foursquare.source_code_analysis.scala_imports import ScalaSymbolPath
from foursquare.source_code_analysis.unused_import_remover import UnusedImportRemover


VERSION = '0.1'

log = logging.getLogger()


class ScalaUnusedImportRemover(UnusedImportRemover):
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

  USAGE:

  python src/python/foursquare/source_code_analysis/scala_unused_import_remover.py --nobackup <files_or_directories>

  Don't forget to add src/python to your PYTHON_PATH
  """
  def __init__(self, backup):
    super(ScalaUnusedImportRemover, self).__init__(backup, import_parser = ScalaImportParser)

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


def get_command_line_args():
  opt_parser = optparse.OptionParser(usage='%prog [options] scala_source_file_or_dir(s)', version='%prog ' + VERSION)
  opt_parser.add_option('--log_level', type='choice', dest='log_level', choices=['DEBUG', 'INFO', 'WARNING', 'ERROR'],
    default='INFO', help='Log level to display on the console.')
  opt_parser.add_option('--nobackup', action='store_true', dest='nobackup', default=False,
    help='If unspecified, we back up modified files with a .bak suffix before rewriting them.')

  (options, args) = opt_parser.parse_args()

  if len(args) == 0:
    opt_parser.error('Must specify at least one scala source file or directory to check')

  return (options, args)

def main(options, scala_source_files):
  numeric_log_level = getattr(logging, options.log_level, None)
  if not isinstance(numeric_log_level, int):
    raise Exception('Invalid log level: %s' % options.log_level)
  logging.basicConfig(level=numeric_log_level)
  import_rewriter = ScalaUnusedImportRemover(not options.nobackup)
  import_rewriter.apply_to_scala_source_files(scala_source_files)
  log.info('Done!')

if __name__ == '__main__':
  (options, args) = get_command_line_args()
  main(options, args)
