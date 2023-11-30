from __future__ import annotations

import logging
from collections.abc import Collection
from typing import TYPE_CHECKING, ClassVar

from attrs import define, field
from typing_extensions import Self

from cloudshell.cli.configurator import AbstractModeConfigurator

from cloudshell.cli.factory.session_factory import (
    CloudInfoAccessKeySessionFactory,
    GenericSessionFactory,
    SessionFactory,
)
from cloudshell.cli.service.cli_service_impl import CliServiceImpl
from cloudshell.cli.service.command_mode_helper import CommandModeHelper

from cloudshell.firewall.paloalto.panos.cli.panos_command_modes import (
    ConfigCommandMode,
    DefaultCommandMode,
)
from cloudshell.cli.session.ssh_session import SSHSession
from cloudshell.cli.session.telnet_session import TelnetSession

if TYPE_CHECKING:
    from cloudshell.cli.service.cli import CLI
    from cloudshell.cli.types import T_COMMAND_MODE_RELATIONS, CliConfigProtocol


@define
class PanOSCliConfigurator(AbstractModeConfigurator):
    REGISTERED_SESSIONS: ClassVar[tuple[SessionFactory]] = (
        CloudInfoAccessKeySessionFactory(SSHSession),
        GenericSessionFactory(TelnetSession),
    )
    modes: T_COMMAND_MODE_RELATIONS = field(init=False)

    def __attrs_post_init__(self):
        super().__attrs_post_init__()
        self.modes = CommandModeHelper.create_command_mode(self._auth)

    @classmethod
    def from_config(
        cls,
        conf: CliConfigProtocol,
        logger: logging.Logger | None = None,
        cli: CLI | None = None,
        registered_sessions: Collection[SessionFactory] | None = None,
    ) -> Self:
        if not logger:
            logger = logging.getLogger(__name__)
        return super().from_config(conf, logger, cli, registered_sessions)

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
