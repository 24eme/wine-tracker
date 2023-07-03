#!/bin/bash

cd $(dirname $0)/..

if test -d env; then
	source env/bin/activate
fi

mkdir -p graphes

bash bin/generate_macave.sh
bash bin/generate_levignoble.sh
