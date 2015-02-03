#!/bin/sh

SINCE=HEAD~
if [ $# == 1 ]; then
  SINCE=$1
fi

cd "$(git rev-parse --show-toplevel)"
git diff --name-only @{u}.. | sort | uniq | grep scala$ | xargs scala_import_sorter
git diff --name-only --cached | sort | uniq | grep scala$ | xargs scala_import_sorter
