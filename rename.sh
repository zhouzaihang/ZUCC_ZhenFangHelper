#! /bin/bash
cd zf_train
for files in `ls`
do
    # mv $files ${files:0:4}".gif"
    mv $files ${files:0:4}${files:0-4}
done