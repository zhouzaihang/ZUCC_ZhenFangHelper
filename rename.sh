#! /bin/bash
cd zf_t
for files in `ls`
do
    mv $files ${files:0:4}".gif"
done