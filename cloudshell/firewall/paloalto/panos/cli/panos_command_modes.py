#!/usr/bin/python
# -*- coding: utf-8 -*-

from cloudshell.cli.service.command_mode import CommandMode


class DefaultCommandMode(CommandMode):
    PROMPT = r">\s*$"
    ENTER_COMMAND = ""
    EXIT_COMMAND = ""

    def __init__(self, resource_config):
        """
        Initialize Default command mode, only for cases when session started not in enable mode

        :param context:
        """

        self.resource_config = resource_config
        # self._api = api

        super(DefaultCommandMode, self).__init__(
            prompt=self.PROMPT,
            enter_command=self.ENTER_COMMAND,
            exit_command=self.EXIT_COMMAND,
        )


class ConfigCommandMode(CommandMode):
    PROMPT = r"[\[\(]edit[\)\]]\s*\S*#\s*$"
    ENTER_COMMAND = "configure"
    EXIT_COMMAND = "exit"

    def __init__(self, resource_config):
        """
        Initialize Enable command mode - default command mode for Cisco Shells

        :param context:
        """

        self.resource_config = resource_config
        # self._api = api

        super(ConfigCommandMode, self).__init__(
            prompt=self.PROMPT,
            enter_command=self.ENTER_COMMAND,
            exit_command=self.EXIT_COMMAND,
        )


CommandMode.RELATIONS_DICT = {DefaultCommandMode: {ConfigCommandMode: {}}}
