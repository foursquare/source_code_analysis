# coding=utf-8
# Copyright 2013 Foursquare Labs Inc. All Rights Reserved.

from __future__ import (nested_scopes, generators, division, absolute_import, with_statement,
                        print_function, unicode_literals)


class ScalaSymbolPath(object):
  """"A dotted path of identifiers."""
  def __init__(self, path_string):
    """Object is immutable."""
    self.path_string = path_string
    self.path_parts = path_string.split('.')

  def get_name(self):
    """Returns the last component of the path."""
    return self.path_parts[-1]

  def get_all_but_name(self):
    """Returns a list of all but the last component of the path."""
    return self.path_parts[0:-1]

  def get_top_level(self):
    """Returns the first component of the path."""
    return self.path_parts[0]

  def is_prefix_of(self, other):
    """If this symbol is a prefix of the other symbol, returns a list of the suffix parts. Returns None otherwise."""
    if self.path_parts == other.path_parts[0:len(self.path_parts)]:
      return other.path_parts[len(self.path_parts):]
    else:
      return None

  def with_suffix(self, suffix_parts):
    """Returns an instance of ScalaSymbolPath representing this path with the suffix parts added."""
    if len(suffix_parts) > 0:
      return ScalaSymbolPath('.'.join(self.path_parts + suffix_parts))
    else:
      return self

  def __repr__(self):
    return self.path_string

  def __eq__(self, other):
    return self.path_string == other.path_string


class ScalaImport(object):
  """An import of a single symbol, possibly renamed."""
  def __init__(self, path_string, as_name):
    """Object is immutable."""
    self.path = ScalaSymbolPath(path_string)
    self.as_name = as_name  # An identifier, or None if the same as name.

  def get_name(self):
    """Returns the name by which code will reference the imported symbol."""
    if self.as_name is None:
      return self.path.get_name()
    else:
      return self.as_name

  def get_maybe_rewritten_import(self, rewrite_rule):
    """Returns a new ScalaImport instance, or this instance if no rewrite occurred."""
    suffix = rewrite_rule.from_path.is_prefix_of(self.path)
    if suffix is None:
      return self
    else:
      return ScalaImport(repr(rewrite_rule.to_path.with_suffix(suffix)), self.as_name)

  def get_selector_string(self):
    """Returns the part of the import after the last dot, minus the braces if any."""
    if self.as_name is None:
      return self.path.get_name()
    else:
      return '{0} => {1}'.format(self.path.get_name(), self.as_name)

  def __repr__(self):
    if self.as_name is None:
      return self.path.path_string
    else:
      # Note: The outer {{ }} turn into literal { } and the inner {0} is replaced by the selector string.
      return '.'.join(self.path.get_all_but_name() + ['{{{0}}}'.format(self.get_selector_string())])

  def __eq__(self, other):
    return self.path == other.path and self.as_name == other.as_name


class ScalaImportClause(object):
  """A single import clause, possibly importing multiple possibly renamed symbols."""

  def __init__(self, indent, path, src_text=None, src_begin_idx=-1, src_end_idx=-1):
    """Object is mutable - see add_import()."""
    self.indent = indent
    self.path = ScalaSymbolPath(path)  # The common path prefix of all imports in this clause.
    self.src_text = src_text  # The original text we parsed this import clause from, if any.
    self.src_begin_idx = src_begin_idx
    self.src_end_idx = src_end_idx
    self.imports = []  # The imports declared by this clause.

  def add_import(self, name, as_name):
    imprt = ScalaImport(repr(self.path.with_suffix([name])), as_name)
    if imprt not in self.imports:
      self.imports.append(imprt)

  def remove_import(self, name):
    ret = (x for x in self.imports if x.get_name() == name).next()
    self.imports = filter(lambda x: x.get_name() != name, self.imports)
    return ret

  def sort_imports(self):
    self.imports.sort(cmp=lambda x,y: cmp(x.path.path_string, y.path.path_string))

  MAX_LINE_LEN = 120

  def _to_str(self, include_indent=True):
    if len(self.imports) == 0:
      ret = '<empty import clause>'
    elif len(self.imports) == 1:
      ret = '{0}import {1}'.format(self.indent if include_indent else '', repr(self.imports[0]))
    else:
      selector_strings = [x.get_selector_string() for x in self.imports]
      delimited_selector_strings = [x + ', ' for x in selector_strings[0:-1]] + [selector_strings[-1] + '}']
      ret = '{0}import {1}.{{'.format(self.indent if include_indent else '', self.path)
      continuation_indent_size = 4  # To indent under the first selector, replace 4 with len(ret).
      line_len = len(ret)
      for s in delimited_selector_strings:
        if line_len + len(s) > ScalaImportClause.MAX_LINE_LEN:
          ret = ret.rstrip()
          ret += '\n'
          ret += ' ' * continuation_indent_size
          line_len = continuation_indent_size
        ret += s
        line_len += len(s)

    return ret

  def str_no_indent(self):
    return self._to_str(include_indent=False)

  def __repr__(self):
    return self._to_str()
  def __eq__(self, other):
    return self.path == other.path and self.imports == other.imports

