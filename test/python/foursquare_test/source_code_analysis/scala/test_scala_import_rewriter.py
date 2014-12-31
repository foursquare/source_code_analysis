# coding=utf-8
# Copyright 2011 Foursquare Labs Inc. All Rights Reserved

from __future__ import (nested_scopes, generators, division, absolute_import, with_statement,
                        print_function, unicode_literals)

import unittest

from foursquare.source_code_analysis.scala.scala_import_rewriter import ScalaImportRewriteRule, ScalaImportRewriter


class ScalaImportRewriterTest(unittest.TestCase):
  def _do_test_rewriter(self, rewrite_rule, input_text, expected_text):
    input_text += '\n'
    expected_text += '\n'
    rewriter = ScalaImportRewriter(rewrite_rule, False)
    rewritten_text = rewriter.apply_to_text('test.scala', input_text).new_text
    self.assertEqual(expected_text, rewritten_text)

  def test_rewriter(self):
    rewrite_rule = ScalaImportRewriteRule('foo.bar.Baz', 'foo.qux.Baz')
    self._do_test_rewriter(rewrite_rule, 'import foo.bar.Baz', 'import foo.qux.Baz')
    self._do_test_rewriter(rewrite_rule, '    import foo.bar.Baz', '    import foo.qux.Baz')
    self._do_test_rewriter(rewrite_rule, 'import foo.bar.Baz._', 'import foo.qux.Baz._')
    self._do_test_rewriter(rewrite_rule, 'import foo.bar.Baz.Qux._', 'import foo.qux.Baz.Qux._')
    self._do_test_rewriter(rewrite_rule, 'import foo.bar.{Baz => Baz2}', 'import foo.qux.{Baz => Baz2}')
    self._do_test_rewriter(rewrite_rule, 'import foo.bar.{Baz, Qux}',
                                         'import foo.qux.Baz\nimport foo.bar.Qux')
    self._do_test_rewriter(rewrite_rule, '  import foo.bar.{Baz, Qux}',
                                         '  import foo.qux.Baz\n  import foo.bar.Qux')
    self._do_test_rewriter(rewrite_rule, 'import foo.bar.{Qux, Baz}',
                                         'import foo.bar.Qux\nimport foo.qux.Baz')
    self._do_test_rewriter(rewrite_rule, 'import foo.bar.{Qux, Baz, Quux}',
                                         'import foo.bar.{Qux, Quux}\nimport foo.qux.Baz')
    self._do_test_rewriter(rewrite_rule, 'import foo.bar.{Qux => Qux2, Baz => Baz2, Quux}',
                                         'import foo.bar.{Qux => Qux2, Quux}\nimport foo.qux.{Baz => Baz2}')
    self._do_test_rewriter(rewrite_rule, 'import foo.bar.{Baz, \n   Qux => Qux2}',
                                         'import foo.qux.Baz\nimport foo.bar.{Qux => Qux2}')
    self._do_test_rewriter(rewrite_rule, 'import foo.bar.Baz.{Qux1, \n  Qux2 => Qux3 \n,  Qux4 \n }',
                                         'import foo.qux.Baz.{Qux1, Qux2 => Qux3, Qux4}')
