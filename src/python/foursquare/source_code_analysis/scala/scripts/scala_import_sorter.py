# coding=utf-8
# Copyright 2013 Foursquare Labs Inc. All Rights Reserved.

from __future__ import (nested_scopes, generators, division, absolute_import, with_statement,
                        print_function, unicode_literals)

import logging
import optparse

from foursquare.source_code_analysis.exception import SourceCodeAnalysisException
from foursquare.source_code_analysis.scala.scala_import_sorter import ScalaImportSorter

VERSION = '0.1'

log = logging.getLogger()

def get_command_line_args():
  opt_parser = optparse.OptionParser(usage='%prog [options] scala_source_file_or_dir(s)', version='%prog ' + VERSION)
  opt_parser.add_option('--log_level', type='choice', dest='log_level', choices=['DEBUG', 'INFO', 'WARNING', 'ERROR'],
    default='INFO', help='Log level to display on the console.')
  opt_parser.add_option('--backup', action='store_true', dest='backup', default=False,
    help='If unspecified, we back up modified files with a .bak suffix before rewriting them.')
  opt_parser.add_option('--fancy', action='store_true', dest='fancy', default=False,
    help='Whether to separate java, javax, scala and scalax imports and put them first.')

  (options, args) = opt_parser.parse_args()

  if len(args) == 0:
    opt_parser.error('Must specify at least one scala source file or directory to rewrite')

  return options, args

def main():
  (options, scala_source_files) = get_command_line_args()
  numeric_log_level = getattr(logging, options.log_level, None)
  if not isinstance(numeric_log_level, int):
    raise SourceCodeAnalysisException('Invalid log level: %s' % options.log_level)
  logging.basicConfig(level=numeric_log_level)
  import_sorter = ScalaImportSorter(options.backup, options.fancy)
  import_sorter.apply_to_source_files(scala_source_files)
  log.info('Done!')
