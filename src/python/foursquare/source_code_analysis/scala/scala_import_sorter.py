# coding=utf-8
# Copyright 2013 Foursquare Labs Inc. All Rights Reserved.

from __future__ import (nested_scopes, generators, division, absolute_import, with_statement,
                        print_function, unicode_literals)


from foursquare.source_code_analysis.exception import SourceCodeAnalysisException
from foursquare.source_code_analysis.scala.scala_import_parser import ScalaImportParser
from foursquare.source_code_analysis.scala.scala_source_file_rewriter import ScalaSourceFileRewriter


VERSION = '0.1'


class ScalaImportSorter(ScalaSourceFileRewriter):
  """Sorts imports in scala source files, either strictly alphabetically, or as follows ('fancy' mode):

  import java.*
  import javax.*
  import scala.*
  import scalax.*

  everything else.

  Within each group, sorts alphabetically.

  Overwrites the original file. Use with caution.
  """
  def __init__(self, backup, fancy):
    super(ScalaImportSorter, self).__init__(backup)
    self._import_clauses = []
    self._in_import_block = False
    self._current_import_clause = None  # If we're in a multiline clause, refers to that clause.
    self._num_skipped_blank_lines = 0
    self._fancy = fancy

  # Fake sort key prefixes that are guaranteed to be before any (non-adversarial) top-level package name.
  _special_cases = { 'java': 'aaa0', 'javax': 'aaa1', 'scala': 'aaa2', 'scalax': 'aaa3' }

  @staticmethod
  def cmp_clauses(left, right):
    def string_for_cmp(clause):
      # Sort alphabetically, except that we consider { to be less than any letter, so that
      # import foo.bar.Baz._ sorts after import foo.bar.{Bar1, Bar2}.
      return clause.str_no_indent().replace('{', ' ')
    return cmp(string_for_cmp(left), string_for_cmp(right))

  @staticmethod
  def cmp_clauses_fancy(left, right):
    left_str = left.path.path_string
    right_str = right.path.path_string
    left_root = left.path.path_parts[0]
    right_root = right.path.path_parts[0]
    left_sort_key = ScalaImportSorter._special_cases.get(left_root, '') + left_str
    right_sort_key = ScalaImportSorter._special_cases.get(right_root, '') + right_str
    return cmp(left_sort_key, right_sort_key)

  def apply_to_rewrite_cursor(self, rewrite_cursor):
    # Search for the first import in the first import block.
    import_clause = ScalaImportParser.search(rewrite_cursor)
    while import_clause is not None:
      import_block = []
      num_blank_lines = 0
      while import_clause is not None:
        # Note that we don't care about blank lines in the middle of an import block, we only emit ones after the
        # end of a block.
        num_blank_lines = self.skip_blank_lines(rewrite_cursor)
        import_block.append(import_clause)
        import_clause = ScalaImportParser.match(rewrite_cursor)  # Note use of match, not search.

      # We're on the first non-import, non-blank line after an import block, or at the end of the text.
      processed_imports = self._process_import_block(import_block)
      rewrite_cursor.emit(processed_imports)
      rewrite_cursor.emit('\n' * num_blank_lines)

      # Search for the first import in the next block.
      import_clause = ScalaImportParser.search(rewrite_cursor)

  def _process_import_block(self, clauses):
    if self._fancy:
      cmp = ScalaImportSorter.cmp_clauses_fancy
    else:
      cmp = ScalaImportSorter.cmp_clauses
    sorted_clauses = sorted(clauses, cmp=cmp)
    merged_clauses = []
    current_clause = None
    for clause in sorted_clauses:
      if current_clause is not None and current_clause.path == clause.path:
        for imp in clause.imports:
          current_clause.add_import(imp.path.get_name(), imp.as_name)
      else:
        current_clause = clause
        merged_clauses.append(current_clause)

    lines = []
    in_special_case_block = False
    for clause in merged_clauses:
      clause.sort_imports()
      if self._fancy and clause.path.get_top_level() in ScalaImportSorter._special_cases:
        in_special_case_block = True
      else:
        if self._fancy:
          if in_special_case_block:
            lines.append('')
          in_special_case_block = False
      lines.append(str(clause))
    return '\n'.join(lines) + '\n'
