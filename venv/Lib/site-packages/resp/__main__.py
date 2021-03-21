#!/usr/bin/env python
# -*- coding: utf-8 -*-

import argparse

from Parser import Parser


def main():

    # Arguments:
    parser = argparse.ArgumentParser()
    parser.add_argument('-r', '--redis', type=str, default='', required=True)
    parser.add_argument('-i', '--input', type=str, default='', required=False)
    parser.add_argument('-d', '--delimiter', type=str, default=',', required=False)
    parser.add_argument('-p', '--pipe', action='store_true', required=False)
    args = parser.parse_args()

    # Parser:
    Parser(args.input, args.redis, args.delimiter, args.pipe)

if __name__ == "__main__":
    main()
