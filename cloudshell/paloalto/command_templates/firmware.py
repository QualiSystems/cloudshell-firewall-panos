from __future__ import annotations

from cloudshell.cli.command_template.command_template import CommandTemplate

INSTALL_SOFTWARE = CommandTemplate(
    "request system software install file {software_file_name}"
)
