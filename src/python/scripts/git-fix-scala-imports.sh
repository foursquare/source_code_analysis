#!/bin/sh

SINCE=`git rev-list --boundary ...master | grep ^- | cut -c2-`
if [ $# == 1 ]; then
  SINCE=$1
fi

cd "$(git rev-parse --show-toplevel)"
FILES=`git diff --name-only --cached $SINCE | sort | uniq | grep scala$`
echo "operating on\n$FILES"
echo "sorting imports"
echo $FILES | xargs scala_import_sorter
echo "removing unused imports"
echo $FILES | xargs scala_unused_import_remover
echo "all done"
