# coding=utf-8
# Copyright 2012 Foursquare Labs Inc. All Rights Reserved.

from __future__ import absolute_import

import logging
import optparse
import re

from foursquare.source_code_analysis.scala.scala_unused_import_remover import ScalaUnusedImportRemover

VERSION = '0.1'

log = logging.getLogger()

def get_command_line_args():
  opt_parser = optparse.OptionParser(usage='%prog [options] scala_source_file_or_dir(s)', version='%prog ' + VERSION)
  opt_parser.add_option('--log_level', type='choice', dest='log_level', choices=['DEBUG', 'INFO', 'WARNING', 'ERROR'],
    default='INFO', help='Log level to display on the console.')
  opt_parser.add_option('--nobackup', action='store_false', dest='backup', default=True,
    help='If unspecified, we back up modified files with a .bak suffix before rewriting them.')

  (options, args) = opt_parser.parse_args()

  if len(args) == 0:
    opt_parser.error('Must specify at least one scala source file or directory to check')

  return (options, args)

def main():
  (options, scala_source_files) = get_command_line_args()
  numeric_log_level = getattr(logging, options.log_level, None)
  if not isinstance(numeric_log_level, int):
    raise Exception('Invalid log level: %s' % options.log_level)
  logging.basicConfig(level=numeric_log_level)
  import_rewriter = ScalaUnusedImportRemover(options.backup)
  import_rewriter.apply_to_source_files(scala_source_files)
  log.info('Done!')
