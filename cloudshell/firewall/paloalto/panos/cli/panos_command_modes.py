#!/usr/bin/python

from cloudshell.cli.service.command_mode import CommandMode


class DefaultCommandMode(CommandMode):
    PROMPT = r">\s*$"
    ENTER_COMMAND = ""
    EXIT_COMMAND = ""

    def __init__(self, resource_config):
        """Initialize Default command mode.

        :param context:
        """
        self.resource_config = resource_config

        super().__init__(
            prompt=self.PROMPT,
            enter_command=self.ENTER_COMMAND,
            exit_command=self.EXIT_COMMAND,
        )


class ConfigCommandMode(CommandMode):
    PROMPT = r"[\[\(]edit[\)\]]\s*\S*#\s*$"
    ENTER_COMMAND = "configure"
    EXIT_COMMAND = "exit"

    def __init__(self, resource_config):
        """Initialize Enable command mode.

        :param context:
        """
        self.resource_config = resource_config

        super().__init__(
            prompt=self.PROMPT,
            enter_command=self.ENTER_COMMAND,
            exit_command=self.EXIT_COMMAND,
        )


CommandMode.RELATIONS_DICT = {DefaultCommandMode: {ConfigCommandMode: {}}}
