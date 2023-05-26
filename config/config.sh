# Edit these lines to use a proxy for git
#export http_proxy="socks5h://127.0.0.1:8000"
#export https_proxy="socks5h://127.0.0.1:8000"

# Edit these lines to change the tested number of threads
export BENCH_MIN_THREAD=1
export BENCH_MAX_THREAD=4

# Edit this list to change benchmarked targets
ENABLED_LIST=(
    "upstream"
    "xyzn"
    "nxyz"
)

CFLAGS_LIST=(
    "o3"                        # alias, no space allowed
    "-pipe -O3"                 # flag
    EOF

    "native"                    # alias, no space allowed
    "-pipe -O3 -march=native"   # flag
    EOF
)

# A list of all available targets
REPO_LIST=(
    "upstream"                                           # alias
    "https://github.com/thliebig/openEMS-Project.git"    # bundle repo
    "https://github.com/biergaizi/openEMS.git"           # openEMS individual repo
    "preserve-cflags"                                    # openEMS individual branch
    EOF

    "xyzn"                                               # alias
    "https://github.com/thliebig/openEMS-Project.git"    # bundle repo
    "https://github.com/biergaizi/openEMS.git"           # openEMS individual repo
    "rework-stage3-corrected-xyzn"                       # openEMS individual branch
    EOF
    
    "nxyz"                                               # alias
    "https://github.com/thliebig/openEMS-Project.git"    # bundle repo
    "https://github.com/biergaizi/openEMS.git"           # openEMS individual repo
    "rework-stage3-corrected-nxyz-pad"                   # openEMS individual branch
    EOF
)
