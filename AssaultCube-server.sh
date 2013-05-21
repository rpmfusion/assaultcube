#!/bin/sh
# CUBE_DIR should refer to the directory in which Cube is placed.
CUBE_DIR=/usr/share/assaultcube

# CUBE_OPTIONS contains any command line options you would like to start Cube with.
#CUBE_OPTIONS="-f"
CUBE_OPTIONS="--home=${HOME}/.assaultcube_v1.0 --init"

[ -e /etc/sysconfig/cube ] && . /etc/sysconfig/cube
[ -e ${HOME}/.cuberc ] && . ${HOME}/.cuberc
cd ${CUBE_DIR}
exec /usr/libexec/assaultcube_server.real ${CUBE_OPTIONS} "$@"
