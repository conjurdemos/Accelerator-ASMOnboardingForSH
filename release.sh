#!/bin/bash
set -x

pip install --target ./package requests --upgrade

pushd package || exit
    zip -r ../deployment-package.zip .
popd || exit

zip -g deployment-package.zip lambda_function.py

set +x
echo "==== Deployment package created successfully ===="
