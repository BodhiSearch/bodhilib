#!/bin/bash

for dir in libs/*/
do
    pytest --rootdir "$dir" -o "env_files=$dir/.env.test" -m all "$dir"
done
