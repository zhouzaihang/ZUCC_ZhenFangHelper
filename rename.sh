#! /bin/bash
cd zf_train
for files in `ls`
do
    mv $files ${files:0:4}".gif"
done
