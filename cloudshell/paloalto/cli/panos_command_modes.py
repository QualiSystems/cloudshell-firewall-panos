from __future__ import annotations

from typing import TYPE_CHECKING

from cloudshell.cli.service.command_mode import CommandMode

if TYPE_CHECKING:
    from cloudshell.cli.service.auth_model import Auth


class DefaultCommandMode(CommandMode):
    PROMPT: str = r">\s*$"
    ENTER_COMMAND: str = ""
    EXIT_COMMAND: str = ""

    def __init__(self, auth: Auth):
        """Initialize Default command mode."""
        self._auth = auth
        CommandMode.__init__(
            self,
            DefaultCommandMode.PROMPT,
            DefaultCommandMode.ENTER_COMMAND,
            DefaultCommandMode.EXIT_COMMAND,
        )


class ConfigCommandMode(CommandMode):
    PROMPT: str = r"[\[\(]edit[\)\]]\s*\S*#\s*$"
    ENTER_COMMAND: str = "configure"
    EXIT_COMMAND: str = "exit"

    def __init__(self, auth: Auth):
        """Initialize Configuration command mode."""
        self._auth = auth

        CommandMode.__init__(
            self,
            ConfigCommandMode.PROMPT,
            ConfigCommandMode.ENTER_COMMAND,
            ConfigCommandMode.EXIT_COMMAND,
        )


CommandMode.RELATIONS_DICT = {DefaultCommandMode: {ConfigCommandMode: {}}}
