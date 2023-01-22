#!/usr/bin/env bash

set -e  # Abort script at first error, when a command exits with non-zero status (except in until or while loops, if-tests, list constructs)
set -u  # Attempt to use undefined variable outputs error message, and forces an exit
set -x  # Similar to verbose mode (-v), but expands commands
set -o pipefail  # Causes a pipeline to return the exit status of the last command in the pipe that returned a non-zero return value.

cd ycor_scraper
scrapy crawl entities --logfile ycor_scraper.log -o corporate_entities_unsorted.csv

# Based on https://github.com/simonw/sf-tree-history/blob/main/.github/workflows/update.yml
cp ../corporate_entities.csv ../corporate_entities_old.csv

# Remove heading line and use it to start a new file
head -n 1 ../corporate_entities_old.csv > ../corporate_entities.csv

# Sort all but the first line and append to that file
tail -n +2 "ycor_entities.20230120c.csv" | sort >> ../corporate_entities.csv

# Generate commit message using csv-diff
csv-diff ../corporate_entities_old.csv ../corporate_entities.csv --key=number --singular=entity --plural=entities > message.txt

git add ../corporate_entities.csv
git commit -F message.txt

# Not ready to have a script push.
echo git push