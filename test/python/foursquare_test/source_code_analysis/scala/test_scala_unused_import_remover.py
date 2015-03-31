# coding=utf-8
# Copyright 2011 Foursquare Labs Inc. All Rights Reserved

from __future__ import (nested_scopes, generators, division, absolute_import, with_statement,
                        print_function, unicode_literals)

import unittest

from foursquare.source_code_analysis.scala.scala_unused_import_remover import ScalaUnusedImportRemover


class ScalaUnusedImportRemoverTest(unittest.TestCase):
  def _do_test_remover(self, input_text, expected_text):
    remover = ScalaUnusedImportRemover(False)
    removed_text = remover.apply_to_text('test.scala', input_text).new_text
    self.assertEqual(expected_text, removed_text)

  def test_basic_removal(self):
    self._do_test_remover(
"""
import scala.foo.Foo
import com.baz.Baz
import java.bar.Bar

if(Foo) {
  Baz()
}
""",
"""
import scala.foo.Foo
import com.baz.Baz

if(Foo) {
  Baz()
}
""")

  def test_no_removal(self):
    input_text = """
import scala.foo.Foo
import com.baz.Baz
import java.bar.Bar

if(Foo) {
  Baz()
} else {
  Bar
}
"""
    self._do_test_remover(input_text, input_text)

  def test_all_removal(self):
    self._do_test_remover(
"""
import scala.foo.Foo
import com.baz.Baz
import java.bar.Bar

if(x) {
  y()
}
""",
"""

if(x) {
  y()
}
""")

  def test_keep_only_wildcards(self):
    self._do_test_remover(
"""
import scala.foo.Foo
import com.baz.Baz
import java.bar.Bar
import boo.biz._

if(x) {
  y()
}
""",
"""
import boo.biz._

if(x) {
  y()
}
""")

  def test_keep_wildcards(self):
    self._do_test_remover(
"""
import scala.foo.Foo
import com.baz.Baz
import java.bar.Bar
import boo.biz._

if(Foo) {
  y()
}
""",
"""
import scala.foo.Foo
import boo.biz._

if(Foo) {
  y()
}
""")


