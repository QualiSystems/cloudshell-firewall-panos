from __future__ import annotations

import logging
from typing import TYPE_CHECKING

from cloudshell.shell.flows.firmware.basic_flow import AbstractFirmwareFlow

from cloudshell.paloalto.command_actions.system_actions import (
    FirmwareActions,
    SystemActions,
)

if TYPE_CHECKING:
    from typing import Union

    from cloudshell.shell.flows.utils.url import BasicLocalUrl, RemoteURL
    from cloudshell.shell.standards.firewall.resource_config import (
        FirewallResourceConfig,
    )

    from ..cli.panos_cli_configurator import PanOSCliConfigurator

    Url = Union[RemoteURL, BasicLocalUrl]


logger = logging.getLogger(__name__)


class PanOSLoadFirmwareFlow(AbstractFirmwareFlow):
    FILE_TYPE = "software"

    def __init__(
        self,
        resource_config: FirewallResourceConfig,
        cli_configurator: PanOSCliConfigurator,
    ):
        super().__init__(resource_config)
        self.cli_configurator = cli_configurator

    def _load_firmware_flow(
        self,
        firmware_url: Url,
        vrf_management_name: str | None,
        timeout: int,
    ) -> None:
        """Load firmware."""
        logger.info("Upgrading firmware")
        with self.cli_configurator.enable_mode_service() as cli_service:
            system_actions = SystemActions(cli_service)
            load_firmware_action = FirmwareActions(cli_service)
            system_actions.import_config(
                filename=firmware_url.filename,
                protocol=firmware_url.scheme,
                host=firmware_url.host,
                file_type=self.FILE_TYPE,
                port=firmware_url.port,
                user=firmware_url.username,
                password=firmware_url.password,
                remote_path=firmware_url.path,
            )

            load_firmware_action.install_software(firmware_url.filename)
