#!/bin/bash

echo $1
echo $1 >> ../source.txt
cat $1 >> ../source.txt
echo --- >> ../source.txt
echo "" >> ../source.txt