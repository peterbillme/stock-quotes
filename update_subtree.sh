#!/bin/bash

rm -rf ohlclib
git add .
git commit -m 'update subtree'
git subtree add --prefix ohlclib git@github.com:peterbillme/ohlclib.git main --squash
