#! /bin/bash

find /projects/huttone/jobs/* -name 'summary.txt' | \
  sort --version-sort | \
  xargs paste -d ' '
