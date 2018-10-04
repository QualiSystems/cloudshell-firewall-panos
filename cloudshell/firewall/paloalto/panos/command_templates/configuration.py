# !/usr/bin/python
# -*- coding: utf-8 -*-

from re import escape
from cloudshell.cli.command_template.command_template import CommandTemplate

SAVE_CONFIG = CommandTemplate("save config to {filename}")
LOAD_CONFIG = CommandTemplate("load config from {filename}")
DELETE_CONFIG = CommandTemplate("delete config saved {filename}")
COPY_TO_TFTP = CommandTemplate("tftp export configuration [remote-port {port}]from {filename} to {tftp_host}")
COPY_FROM_TFTP = CommandTemplate("tftp import {file_type} [remote-port {port}]from {tftp_host} file {remote_path}")
COPY_TO_SCP = CommandTemplate("scp export configuration [remote-port {port}]from {filename} to {dst}")
COPY_FROM_SCP = CommandTemplate("scp import {file_type} [remote-port {port}]from {src}")
RELOAD = CommandTemplate("request restart system", action_map={
        escape("Do you want to continue? (y or n)"): lambda session, logger: session.send_line("y", logger),
},)
SHUTDOWN = CommandTemplate("request shutdown system")
COMMIT = CommandTemplate("commit")
