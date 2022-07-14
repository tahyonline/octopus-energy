#!/bin/bash

. ../venv/bin/activate

cd server
pserve development.ini --reload
