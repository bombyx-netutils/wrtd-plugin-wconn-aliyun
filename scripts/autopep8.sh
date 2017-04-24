#!/bin/bash

LIBFILES="$(find ./wconn_aliyun -name '*.py' | tr '\n' ' ')"

autopep8 -ia --ignore=E501 ${LIBFILES}
