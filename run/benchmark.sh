#!/bin/bash
set -e

function main
{
    # cd into the bundle and use relative paths
    if [[ $BASH_SOURCE = */* ]]; then
        cd -- "${BASH_SOURCE%/*}/" || (echo "Failed to enter ${BASH_SOURCE%/*}/" && exit 1)
        workdir="$(pwd)"
        srcdir="../build/src"
        progdir="../build/prog"

    else
        echo "$0: Can't find the absolute path of the script!"
        echo "The script must be ran directly as an executable, not via sh or bash!"
        exit 1
    fi

    lstopo > lstopo
    lscpu > lscpu
    uname -a > uname

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

            resultdir="$workdir/result/$alias_target-$alias_cflag"

            mkdir -p "$resultdir"
            cp -r "$workdir/pyems" "$resultdir"
            cp -r "$workdir/openems-octave" "$resultdir"
            cp -r "$workdir/openems-python" "$resultdir"

            benchmark \
                "$progdir/$alias_target-$alias_cflag"
	done

        python3 report.py > result.csv
        mv result.csv ./result
        tar -cf result.tar ./result

    done
}

function benchmark
{
    local path=$1

    local path_orig=$PATH
    export PATH=$(realpath "${path}")/bin:$PATH
    export PYTHONUSERBASE=$(realpath "${path}")

    # not a true variable accepted by Octave.
    # it's passed to benchmark.sh in openems-octave/
    export OCTAVEUSERBASE=$(realpath "${path}")

    mkdir -p "$workdir/tmp"
    ln -rs "$workdir/tmp" /tmp/$(whoami)

    cd "$resultdir"

    cd pyems
    ./benchmark.sh
    cd -
    cd openems-python
    ./benchmark.sh
    cd -
    cd openems-octave
    ./benchmark.sh
    cd -

    cd "$workdir"

    rm -rf "$workdir/tmp"
    rm /tmp/$(whoami)

    export PATH=${path_orig}
    unset PYTHONUSERBASE
}

main
