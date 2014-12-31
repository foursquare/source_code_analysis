# coding=utf-8
# Copyright 2013 Foursquare Labs Inc. All Rights Reserved.

from __future__ import (nested_scopes, generators, division, absolute_import, with_statement,
                        print_function, unicode_literals)

from foursquare.source_code_analysis.source_file_rewriter import SourceFileRewriter


class ScalaSourceFileRewriter(SourceFileRewriter):
  """Base class that applies rewriting rules to Scala source files."""
  ext = '.scala'
