#!/usr/bin/env bash

export PREFIX=data

mkdir -p "$PREFIX"

function filter-json() {
	jq -cr '.[] | "\(.id)\t\(.text)"' "$@"
}

function write-tweets() {
	awk \
		-F$'\t' \
		-vprefix="$PREFIX" \
		'{printf "%s/%s\n", prefix, $1; print $2 > prefix"/"$1}'
}

export -f filter-json
export -f write-tweets

printf "%s\0" "$@" |\
	parallel -0 filter-json |\
	parallel --pipe write-tweets
