# coding=utf-8
# Copyright 2013 Foursquare Labs Inc. All Rights Reserved.

from __future__ import (nested_scopes, generators, division, absolute_import, with_statement,
                        print_function, unicode_literals)

import re

from foursquare.source_code_analysis.exception import SourceCodeAnalysisException
from foursquare.source_code_analysis.scala.scala_imports import ScalaImportClause


# A single identifier, e.g., foo, Bar, baz_2, _root_ .
_IDENTIFIER_PATTERN = '(?:\w*)'

# A dotted path of identifiers, e.g., foo.bar.Baz .
_PATH_PATTERN = '(?:{identifier}(\.{identifier})*)'.format(identifier=_IDENTIFIER_PATTERN)

_PATH_RE = re.compile('^{path}$'.format(path=_PATH_PATTERN))

# An identifier rewrite, e.g., Foo => Bar .
_SELECTOR_PATTERN = '{identifier}(?:\s*=>\s*{identifier})?'.format(identifier=_IDENTIFIER_PATTERN)

# A (possibly multiline) import clause.
_IMPORT_PATTERN = ('^(?P<indent> *)import\s*(?P<path>{path})\.'
                   '(?P<selectors>{identifier}|(?:\{{\s*{selector}(?:\s*,\s*{selector})*\s*\}}))[ \t]*\n').format(
                  path=_PATH_PATTERN,
                  identifier=_IDENTIFIER_PATTERN,
                  selector=_SELECTOR_PATTERN)

IMPORT_RE = re.compile(_IMPORT_PATTERN, re.MULTILINE)


class PathValidator(object):
  @staticmethod
  def validate(path):
    return _PATH_RE.match(path) is not None


class ScalaImportParser(object):

  @staticmethod
  def find_all(src_text):
    """Returns a list of ScalaImportClauses representing all the imports in the text.

    Doesn't interact with a rewrite cursor, so is not useful for rewriting.
    """
    return [ ScalaImportParser._create_clause_from_matchobj(m) for m in IMPORT_RE.finditer(src_text) ]

  @staticmethod
  def search(rewrite_cursor):
    """Returns the next ScalaImportClause found, advancing the cursor as needed.

    Skips over, and emits verbatim, anything that isn't an import clause.
    Returns None if it finds no import clause.
    """
    ret = ScalaImportParser._apply_regex(rewrite_cursor, True)
    if ret is None:
      rewrite_cursor.finish()
    return ret

  @staticmethod
  def match(rewrite_cursor):
    """If the cursor is currently on an import clause, returns a ScalaImportClause and advances the cursor.

    Returns None otherwise.
    """
    return ScalaImportParser._apply_regex(rewrite_cursor, False)

  @staticmethod
  def _apply_regex(rewrite_cursor, search):
    if search:
      m = IMPORT_RE.search(rewrite_cursor.src_text, rewrite_cursor.src_pos)
    else:
      m = IMPORT_RE.match(rewrite_cursor.src_text, rewrite_cursor.src_pos)
    if m is None:
      return None

    # Copy whatever we skipped over.
    rewrite_cursor.copy_from_src_until(m.start())

    # Move past the string we matched.
    rewrite_cursor.set_src_pos(m.end())

    return ScalaImportParser._create_clause_from_matchobj(m)

  @staticmethod
  def _create_clause_from_matchobj(m):
    indent_string = m.group('indent')
    path_string = m.group('path')
    selectors_string = m.group('selectors').strip()
    if len(selectors_string) == 0:
      raise SourceCodeAnalysisException('Something wrong with import: {0}; trailing dot, possibly?'.format(m.group(0)))
    if selectors_string[0] == '{':
      if selectors_string[-1] != '}':
        raise SourceCodeAnalysisException('Bad regex match: opening brace has no closing brace.')
      selectors_string = selectors_string[1:-1]

    ret = ScalaImportClause(indent_string, path_string, m.group(0), m.start(), m.end())
    selectors = [x.strip() for x in selectors_string.split(',')]
    for selector in selectors:
      parts = [x.strip() for x in selector.split('=>')]
      name = parts[0]
      if len(parts) == 2:
        as_name = parts[1]
      else:
        as_name = None
      ret.add_import(name, as_name)

    return ret

