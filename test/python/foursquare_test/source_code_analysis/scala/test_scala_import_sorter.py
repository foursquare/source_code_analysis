# coding=utf-8
# Copyright 2011 Foursquare Labs Inc. All Rights Reserved

from __future__ import (nested_scopes, generators, division, absolute_import, with_statement,
                        print_function, unicode_literals)

import unittest

from foursquare.source_code_analysis.scala.scala_import_sorter import ScalaImportSorter


class ScalaImportRewriterTest(unittest.TestCase):
  def _do_test_sorter(self, input_text, expected_text):
    sorter = ScalaImportSorter(False, fancy=True)
    sorted_text = sorter.apply_to_text('test.scala', input_text).new_text
    self.assertEqual(expected_text, sorted_text)

  def test_rewriter(self):
    self._do_test_sorter(
"""
import scala.foo.Foo
import com.baz.Baz
import java.bar.Bar
""",
"""
import java.bar.Bar
import scala.foo.Foo

import com.baz.Baz
""")

    self._do_test_sorter(
"""
import com.foursquare.base.{Foo, Bar}
import scala.foo.Foo

import javax.bar.Bar
import com.foursquare.base.Baz
import scalax.baz.Baz
import java.quux.{Quuux => Quux2}

import org.foo.bar.Baz
import scala.qux.Qux
import java.quux.Quux
""",
"""
import java.quux.{Quuux => Quux2, Quux}
import javax.bar.Bar
import scala.foo.Foo
import scala.qux.Qux
import scalax.baz.Baz

import com.foursquare.base.{Bar, Baz, Foo}
import org.foo.bar.Baz
""")

    self._do_test_sorter(
"""
// Random stuff
package foo.bar

import scala.foo.{Foo => Foo1, Foo2}

import com.baz.Baz

import java.bar.Bar

blah blah blah
blah
if (cond) {
  import javax.foo.Foo
  import java.bar.Bar
}

more blah
""",
"""
// Random stuff
package foo.bar

import java.bar.Bar
import scala.foo.{Foo => Foo1, Foo2}

import com.baz.Baz

blah blah blah
blah
if (cond) {
  import java.bar.Bar
  import javax.foo.Foo
}

more blah
""")

    self._do_test_sorter(
"""
import com.baz.{Baz2, Baz3}
import java.bar.Bar
import com.baz.Baz
""",
"""
import java.bar.Bar

import com.baz.{Baz, Baz2, Baz3}
""")

    self._do_test_sorter(
"""
import com.baz.{Baz2, Baz3}
import java.bar.Bar
import com.baz.Baz.Qux._
""",
"""
import java.bar.Bar

import com.baz.{Baz2, Baz3}
import com.baz.Baz.Qux._
""")

    self._do_test_sorter(
"""
import com.foursquare.legacyconfig.LegacyDynamicConfigDirectory
import net.liftweb.common.{Box, Empty}
import net.liftweb.http.Req
import com.foursquare.base.IpHelpers
""",
"""
import com.foursquare.base.IpHelpers
import com.foursquare.legacyconfig.LegacyDynamicConfigDirectory
import net.liftweb.common.{Box, Empty}
import net.liftweb.http.Req
""")

# Note that string is deliberately over the 120 column mark, to test that it gets shortened properly.
    self._do_test_sorter(
"""
import com.foursquare.record.{BaseUserForeignKey, BitFlagEnum => BitFlagEnumAlias, OptionalLongBitFlagField, FSMongoRecord,FSMongoMetaRecord, FSPhoneField, FSOptionalStringField,
         FSOptionalPhotoField, GeolocationMongo}
import com.foursquare.record.MongoPoint

import com.foursquare.record.{JodaDateTimeField, UserForeignKey, MongoEmbeddedObjectField, MongoEnumField,
                              NamedMongoIdentifier, OptionalJodaDateTimeField, PhoneFormatMode => PhoneFormatModeAlias,
  RandomStringField, SaltedPasswordField, UpdateableRecord, UnpersistedFK}
""",
"""
import com.foursquare.record.{BaseUserForeignKey, BitFlagEnum => BitFlagEnumAlias, FSMongoMetaRecord, FSMongoRecord,
    FSOptionalPhotoField, FSOptionalStringField, FSPhoneField, GeolocationMongo, JodaDateTimeField,
    MongoEmbeddedObjectField, MongoEnumField, MongoPoint, NamedMongoIdentifier, OptionalJodaDateTimeField,
    OptionalLongBitFlagField, PhoneFormatMode => PhoneFormatModeAlias, RandomStringField, SaltedPasswordField,
    UnpersistedFK, UpdateableRecord, UserForeignKey}
""")
