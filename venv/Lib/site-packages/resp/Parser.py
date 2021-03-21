#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
import re


class Parser:

    __version__ = '0.1.2'

    def __init__(self, file_path='', redis='', delimeter=',', pipe=False):
        rows = self.read_stdin() if pipe else self.read_file(file_path)

        # Validate command:
        if not re.findall(r"({[[0-9]+})+", redis):
            error = 'Redis command pattern is invalid: "{}"'.format(redis)
            raise AttributeError(error)

        # Iterate over the rows:
        for row in rows:
            parts = row.split(delimeter)
            for r in redis.split('|'):
                cmd = r.strip()
                cmd = cmd.format(*parts)
                cmd = Parser.convert_cmd(cmd)
                cmd = list(cmd)
                cmd = Parser.concat_cmd(cmd)
                sys.stdout.write(cmd)

    @staticmethod
    def convert_cmd(cmd, resp_pattern='${}\r\n{}'):
        for part in cmd.split():
            size = str(len(str(part).encode('utf8')))
            yield resp_pattern.format(size, str(part))

    @staticmethod
    def concat_cmd(cmd, resp_pattern='*{}\r\n{}\r\n'):
        size = str(len(cmd))
        cmd = '\r\n'.join(cmd)
        return resp_pattern.format(size, cmd)

    @staticmethod
    def read_stdin():
        data = sys.stdin.read()
        rows = data.strip().split('\n')
        return rows

    @staticmethod
    def read_file(file_path):
        if not file_path or not os.path.isfile(file_path):
            error = 'File not found: "{}"'.format(file_path)
            raise AttributeError(error)
        with open(file_path, 'r') as file_:
            data = file_.read()
            rows = data.strip().split('\n')
            return rows
