#!/bin/bash

echo "Start development servers"
echo

[ ! -d server ] || [ ! -d spa ] || [ ! -e __start_dev_server.sh ] && {
  echo "Error: needs to be started from the frontend directory"
  exit 1
}

echo "Starting backend..."
./__start_dev_server.sh &
sleep 3

echo "Starting frontend..."
cd spa
npm start
