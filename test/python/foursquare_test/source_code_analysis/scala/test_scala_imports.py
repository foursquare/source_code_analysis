# coding=utf-8
# Copyright 2011 Foursquare Labs Inc. All Rights Reserved

from __future__ import (nested_scopes, generators, division, absolute_import, with_statement,
                        print_function, unicode_literals)

import unittest

from foursquare.source_code_analysis.rewrite_cursor import RewriteCursor
from foursquare.source_code_analysis.scala.scala_import_parser import PathValidator, ScalaImportParser
from foursquare.source_code_analysis.scala.scala_imports import ScalaImportClause


class ScalaImportRewriterTest(unittest.TestCase):
  def _do_test_validate_path(self, path, expected):
    self.assertEqual(expected, PathValidator.validate(path))

  def _do_test_matcher(self, line, expected_path, expected_selectors):
    line += '\n'
    rewrite_cursor = RewriteCursor('filename', line)
    import_clause = ScalaImportParser.match(rewrite_cursor)
    if expected_path is None:
      self.assertIsNone(import_clause)
    else:
      self.assertIsNotNone(import_clause)
      expected_import_clause = ScalaImportClause('', expected_path)
      for (name, as_name) in expected_selectors:
        expected_import_clause.add_import(name, as_name)
      self.assertEqual(expected_import_clause, import_clause)

  def test_validate_path(self):
    self._do_test_validate_path('foo.bar.Baz', True)
    self._do_test_validate_path('foo.bar.baz', True)
    self._do_test_validate_path('foo.bar_1.Baz2.QUX', True)
    self._do_test_validate_path('foo.bar.Baz._', True)

  def test_matcher(self):
    self._do_test_matcher('import foo.bar.Baz', 'foo.bar', [('Baz', None)])
    self._do_test_matcher('import      foo.bar.Baz', 'foo.bar', [('Baz', None)])
    self._do_test_matcher('import foo.bar.{Baz => Baz2}', 'foo.bar', [('Baz', 'Baz2')])
    self._do_test_matcher('import foo.bar.{Baz, Qux => Qux2, Quux}',
                          'foo.bar', [('Baz', None), ('Qux', 'Qux2'), ('Quux', None)])
    self._do_test_matcher('import foo.bar.{Baz => Baz2, Qux => Qux2, Quux}',
                          'foo.bar', [('Baz', 'Baz2'), ('Qux', 'Qux2'), ('Quux', None)])
    self._do_test_matcher('import foo.bar.{Baz,Qux  =>  Qux2 ,Quux}',
                          'foo.bar', [('Baz', None), ('Qux', 'Qux2'), ('Quux', None)])
    self._do_test_matcher('import foo.bar.{Baz,Qux=>Qux2,Quux}',
                          'foo.bar', [('Baz', None), ('Qux', 'Qux2'), ('Quux', None)])
    self._do_test_matcher('import foo1_.b2ar.Baz_3', 'foo1_.b2ar', [('Baz_3', None)])
    self._do_test_matcher('import FOO.BAR.BAZ', 'FOO.BAR', [('BAZ', None)])

