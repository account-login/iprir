#!/usr/bin/env bash


set -e

# test package
mkdir -p tmp/
cd tmp/     # test installed package instead of cwd
pytest -sv --cov=iprir --pyargs iprir.tests
cp .coverage ../ && cd ..

# test README
pytest -sv README.rst

# upload coverage data
codecov
