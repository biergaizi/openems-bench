#!/bin/bash

for count in {1..3}
do
	echo $count

	for i in *.py
	do
		echo $i
		python3 $i > $i.result.$count 2>&1
	done
done
