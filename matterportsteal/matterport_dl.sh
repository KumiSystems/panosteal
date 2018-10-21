#!/bin/bash
mkdir "${1}/cube" -p

for ((f=0;f<=5;f++)); do
	convert "${1}/part-${f}-1-0_0.jpg" "${1}/part-${f}-1-0_1.jpg" "${1}/part-${f}-1-0_2.jpg" "${1}/part-${f}-1-0_3.jpg" +append "${1}/_part-${f}-1-0.jpg"
	convert "${1}/part-${f}-1-1_0.jpg" "${1}/part-${f}-1-1_1.jpg" "${1}/part-${f}-1-1_2.jpg" "${1}/part-${f}-1-1_3.jpg" +append "${1}/_part-${f}-1-1.jpg"
	convert "${1}/part-${f}-1-2_0.jpg" "${1}/part-${f}-1-2_1.jpg" "${1}/part-${f}-1-2_2.jpg" "${1}/part-${f}-1-2_3.jpg" +append "${1}/_part-${f}-1-2.jpg"
	convert "${1}/part-${f}-1-3_0.jpg" "${1}/part-${f}-1-3_1.jpg" "${1}/part-${f}-1-3_2.jpg" "${1}/part-${f}-1-3_3.jpg" +append "${1}/_part-${f}-1-3.jpg"
	convert "${1}/_part-${f}-1-0.jpg" "${1}/_part-${f}-1-1.jpg" "${1}/_part-${f}-1-2.jpg" "${1}/_part-${f}-1-3.jpg" -append "${1}/cube/${f}.jpg"
done

cube2sphere -r 3840 2160 -R 0 0 $2 -f jpg -b blender "${1}/cube/3.jpg" "${1}/cube/1.jpg" "${1}/cube/2.jpg" "${1}/cube/4.jpg" "${1}/cube/0.jpg" "${1}/cube/5.jpg" -o "${1}/cube/${1}"
