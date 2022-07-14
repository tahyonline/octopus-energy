#!/bin/bash

echo "Run the Octopus Energy Consumption Analyser"
echo

[ ! -d server ] || [ ! -d spa ] && {
  echo "Error: needs to be started from the project root directory"
  exit 1
}

echo "Rebuilding the SPA..."
cd spa || exit
npm run build || exit

echo "Initialising server..."
cd ../server || exit
. ../venv/bin/activate
pip install -e .

echo "Starting local server..."
pserve production.ini -b

cd ..
echo "Thank you!"