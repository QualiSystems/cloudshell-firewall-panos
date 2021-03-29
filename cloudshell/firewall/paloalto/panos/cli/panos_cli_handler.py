#!/usr/bin/python
# -*- coding: utf-8 -*-

from cloudshell.cli.configurator import AbstractModeConfigurator
from cloudshell.cli.service.cli import CLI
from cloudshell.cli.service.cli_service_impl import CliServiceImpl
from cloudshell.cli.service.command_mode_helper import CommandModeHelper
from cloudshell.cli.service.session_pool_manager import SessionPoolManager
from cloudshell.cli.session.ssh_session import SSHSession
from cloudshell.cli.session.telnet_session import TelnetSession

from cloudshell.firewall.paloalto.panos.cli.panos_command_modes import (
    ConfigCommandMode,
    DefaultCommandMode,
)


class PanOSCli(object):
    def __init__(self, resource_config):
        session_pool_size = int(resource_config.sessions_concurrency_limit)
        session_pool = SessionPoolManager(max_pool_size=session_pool_size)
        self.cli = CLI(session_pool=session_pool)

    def get_cli_handler(self, resource_config, logger):
        return PanOSCliHandler(self.cli, resource_config, logger)


class PanOSCliHandler(AbstractModeConfigurator):
    REGISTERED_SESSIONS = (
        SSHSession,
        TelnetSession,
    )

    def __init__(self, cli, resource_config, logger):
        super(PanOSCliHandler, self).__init__(resource_config, logger, cli)
        self.modes = CommandModeHelper.create_command_mode(resource_config)

    @property
    def default_mode(self):
        return self.modes[DefaultCommandMode]

    @property
    def enable_mode(self):
        return self.modes[DefaultCommandMode]

    @property
    def config_mode(self):
        return self.modes[ConfigCommandMode]

    def _on_session_start(self, session, logger):
        """Send default commands to configure/clear session outputs."""
        cli_service = CliServiceImpl(
            session=session, requested_command_mode=self.enable_mode, logger=logger
        )
        cli_service.send_command(
            "set cli config-output-format set", DefaultCommandMode.PROMPT
        )
        cli_service.send_command("set cli pager off", DefaultCommandMode.PROMPT)
        cli_service.send_command(
            "set cli terminal width 300", DefaultCommandMode.PROMPT
        )
