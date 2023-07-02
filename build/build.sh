#!/bin/bash

set -e

function main
{
    # cd into the bundle and use relative paths
    if [[ $BASH_SOURCE = */* ]]; then
        cd -- "${BASH_SOURCE%/*}/" || (echo "Failed to enter ${BASH_SOURCE%/*}/" && exit 1)
        workdir="$(pwd)"
        srcdir="${workdir}/src"
        progdir="${workdir}/prog"
        mkdir -p "$srcdir" "$progdir"
    else
        echo "$0: Can't find the absolute path of the script!"
        echo "The script must be ran directly as an executable, not via sh or bash!"
        exit 1
    fi

    source ../config/config.sh

    for ((i=0; i<${#REPO_LIST[@]}; i+=5)) do
        local alias_target=${REPO_LIST[i]}
        local bundle_url=${REPO_LIST[i+1]}
        local openems_url=${REPO_LIST[i+2]}
        local openems_branch=${REPO_LIST[i+3]}
        local eof=${REPO_LIST[i+4]}

	if [[ $eof != EOF ]]; then
	    echo "$0: Syntax error in REPO_LIST."
            exit 1
	fi

        for ((j=0; j<${#CFLAGS_LIST[@]}; j+=3)) do
            local alias_cflag=${CFLAGS_LIST[j]}
            local cflags=${CFLAGS_LIST[j+1]}
            local eof=${CFLAGS_LIST[j+2]}

	    if [[ $eof != EOF ]]; then
	        echo "$0: Syntax error in CFLAGS_LIST."
                exit 1
	    fi

            build \
                "$bundle_url" \
                "$openems_url" \
                "$openems_branch" \
                "$cflags" \
                "$srcdir/$alias_target-$alias_cflag" \
                "$progdir/$alias_target-$alias_cflag"
	done

    done
}

function build
{
    local git_bundle_url=$1
    local git_openems_url=$2
    local git_openems_branch=$3
    local cflags=$4
    local input_dir=$5
    local output_dir=$6

    echo "git_bundle_url: $git_bundle_url"
    echo "git_openems_url: $git_openems_url"
    echo "git_openems_branch: $git_openems_branch"
    echo "input_dir: $input_dir"
    echo "output_dir: $output_dir"

    git clone --recurse-submodule "$git_bundle_url" "$input_dir"
    cd "$input_dir"

    git submodule set-url -- openEMS "$git_openems_url"

    # use a patched fparser unconditionally for now
    # https://github.com/thliebig/fparser/issues/4
    git submodule set-url -- fparser https://github.com/biergaizi/fparser.git

    git submodule sync

    cd openEMS
    git checkout master
    git pull --rebase
    git checkout "$git_openems_branch"
    cd ..

    # use a patched fparser unconditionally for now
    # https://github.com/thliebig/fparser/issues/4
    cd fparser
    git checkout master
    git pull --rebase
    cd ..

    git clone https://github.com/matthuszagh/pyems.git

    export PYTHONUSERBASE="$output_dir"
    export CFLAGS="$cflags"
    export CXXFLAGS="$cflags"

    ./update_openEMS.sh "$output_dir" --disable-GUI --python
    cd pyems
    python3 setup.py install --user
    cd ..

    unset PYTHONUSERBASE
    unset CFLAGS
    unset CXXFLAGS
}

main
