# Edit these lines to use a proxy for git
#export http_proxy="socks5h://127.0.0.1:8000"
#export https_proxy="socks5h://127.0.0.1:8000"

# Edit these lines to change the tested number of threads
export BENCH_MIN_THREAD=1
export BENCH_MAX_THREAD=16

# Edit this list to change benchmarked targets
ENABLED_LIST=(
    "tiling"
)

CFLAGS_LIST=(
    "o3"                        # alias, no space allowed
    "-pipe -O3"                 # flag
    EOF
)

# A list of all available targets
REPO_LIST=(
    "tiling"                                             # alias
    "https://github.com/thliebig/openEMS-Project.git"    # bundle repo
    "https://github.com/biergaizi/openEMS.git"           # openEMS individual repo
    "project-diamond-rework1"                            # openEMS individual branch
    EOF
)
