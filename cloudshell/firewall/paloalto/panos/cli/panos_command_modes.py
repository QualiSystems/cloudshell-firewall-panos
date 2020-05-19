#!/usr/bin/python
# -*- coding: utf-8 -*-

# from collections import OrderedDict

from cloudshell.cli.command_mode import CommandMode


class DefaultCommandMode(CommandMode):
    PROMPT = r'>\s*$'
    ENTER_COMMAND = ''
    EXIT_COMMAND = ''

    def __init__(self, resource_config, api):
        """
        Initialize Default command mode, only for cases when session started not in enable mode

        :param context:
        """

        self.resource_config = resource_config
        self._api = api

        super(DefaultCommandMode, self).__init__(prompt=self.PROMPT,
                                                 enter_command=self.ENTER_COMMAND,
                                                 exit_command=self.EXIT_COMMAND)

        #     CommandMode.__init__(self,
        #                          DefaultCommandMode.PROMPT,
        #                          DefaultCommandMode.ENTER_COMMAND,
        #                          DefaultCommandMode.EXIT_COMMAND,
        #                          enter_action_map=self.enter_action_map(),
        #                          exit_action_map=self.exit_action_map(),
        #                          enter_error_map=self.enter_error_map(),
        #                          exit_error_map=self.exit_error_map())
        #
        # def enter_action_map(self):
        #     return OrderedDict()
        #
        # def enter_error_map(self):
        #     return OrderedDict()
        #
        # def exit_action_map(self):
        #     return OrderedDict()
        #
        # def exit_error_map(self):
        #     return OrderedDict()


class ConfigCommandMode(CommandMode):
    PROMPT = r'[\[\(]edit[\)\]]\s*\S*#\s*$'
    ENTER_COMMAND = 'configure'
    EXIT_COMMAND = 'exit'

    def __init__(self, resource_config, api):
        """
        Initialize Enable command mode - default command mode for Cisco Shells

        :param context:
        """

        self.resource_config = resource_config
        self._api = api

        super(ConfigCommandMode, self).__init__(prompt=self.PROMPT,
                                                enter_command=self.ENTER_COMMAND,
                                                exit_command=self.EXIT_COMMAND)

        #     CommandMode.__init__(self,
        #                          ConfigCommandMode.PROMPT,
        #                          ConfigCommandMode.ENTER_COMMAND,
        #                          ConfigCommandMode.EXIT_COMMAND,
        #                          enter_action_map=self.enter_action_map(),
        #                          exit_action_map=self.exit_action_map(),
        #                          enter_error_map=self.enter_error_map(),
        #                          exit_error_map=self.exit_error_map())
        #
        # def enter_action_map(self):
        #     return OrderedDict()
        #
        # def enter_error_map(self):
        #     return OrderedDict()
        #
        # def exit_action_map(self):
        #     return OrderedDict()
        #
        # def exit_error_map(self):
        #     return OrderedDict()


CommandMode.RELATIONS_DICT = {
    DefaultCommandMode: {
        ConfigCommandMode: {}
    }
}
