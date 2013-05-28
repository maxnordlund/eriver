#!/bin/bash
BIN="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"/./node_modules/.bin

path_remove ()  { export PATH=`echo -n $PATH | awk -v RS=: -v ORS=: '$0 != "'$1'"' | sed 's/:$//'`; }

case "$1" in
  "-d" | "--disable" )
    path_remove $BIN
    ;;
  "-e" | "--enable" )
    path_remove $BIN
    export PATH="$BIN:$PATH"
    ;;
  *)
  echo "Usage: . shim -e|--enable|-d|--disable"
esac

_autocomplete () { #  By convention, the function name starts with an underscore.
  local cur
  # Pointer to current completion word.
  # By convention, it's named "cur" but this isn't strictly necessary.

  COMPREPLY=() # Array variable storing the possible completions.
  cur=${COMP_WORDS[COMP_CWORD]}

  case "$cur" in
    -*)
    COMPREPLY=( $( compgen -W '-d -e --disable --enable --' -- $cur ) );;
    # Generate the completion matches and load them into $COMPREPLY array.
    # xx) May add more cases here.
  esac

  return 0
}
complete -F _autocomplete -o filenames ./shim.sh
