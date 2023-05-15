#!/bin/bash

for count in {1..3}
do
	echo $count

	for i in *.m
	do
		echo $i
		octave \
			--path "$OCTAVEUSERBASE/share/openEMS/matlab" \
			--path "$OCTAVEUSERBASE/share/CSXCAD/matlab" \
			$i > $i.result.$count 2>&1
	done
done
