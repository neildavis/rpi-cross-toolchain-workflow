#!/usr/bin/env bash

if [[ ! -d "$1" ]]; then
    echo "Usage: $(basename $0) sysroot_directory"
    exit 1
fi

for dead_link in $(find "$1/usr/lib" -xtype l | xargs realpath -s); do
    dead_target=$(readlink -s "$dead_link")
    fixed_target="$(dirname $dead_link)/${dead_target##*/}"
    if [[ -f "$fixed_target" ]]; then
        ln -sf "$fixed_target" "$dead_link"
        echo "Fixed broken link: $dead_link -> $dead_target -> $fixed_target" 
    fi
done
