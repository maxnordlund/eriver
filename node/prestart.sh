#!/bin/bash
current_dir=$(pwd)
script_dir=$(dirname $0)
if [ $script_dir != '.' ]
  then
  current_dir="$current_dir/$script_dir"
fi
node_modules="$current_dir/node_modules"
export NODE_PATH="$NODE_PATH:$node_modules"
echo "NODE_PATH = $NODE_PATH"
exit