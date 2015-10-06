#!/bin/bash

# MIT License
# Copyright (c) 2015 Genome Research Limited

# Author: Christopher Harrison <ch12@sanger.ac.uk>

DATA=/lustre/scratch114/teams/hgi/lustre_reports/mpistat/data

# AWK script to do the formatting
# (The one-liner version was horrible!)
read -d '' FORMAT <<'AWK'
$1 != a {
  b = 104
  printf "\\n%s:", $1
}
{
  n = $2 - b
  if (n > 1) {
    for (i = 1; i < n; i++)
      printf "    "
  }
  printf " %s", $2
  a = $1
  b = $2
}
AWK

# Print all files in $DATA, filter to data files, strip the extension,
# sort, format (per above), sanitise line endings, strip blank columns
# for non-existent scratch108 and scratch112
find "$DATA" -type f -printf "%P\n" \
 | grep -P "^\d{8}_\d{3}\.dat\.gz$" \
 | cut -c -12 \
 | sort \
 | awk -F_ "$FORMAT" \
 | sed '/^$/d;$a\' \
 | cut --complement -c 23-26 \
 | cut --complement -c 35-38
