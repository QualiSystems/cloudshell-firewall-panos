from __future__ import annotations

import logging
from typing import TYPE_CHECKING

from attrs import define

from cloudshell.snmp.snmp_configurator import EnableDisableSnmpFlowInterface

from cloudshell.firewall.paloalto.panos.command_actions.enable_disable_snmp_actions import (  # noqa: E501
    EnableDisableSnmpV2Actions,
    EnableDisableSnmpV3Actions,
)
from cloudshell.firewall.paloalto.panos.command_actions.system_actions import (
    SystemConfigurationActions,
)

if TYPE_CHECKING:
    from typing import Union

    from cloudshell.cli.service.cli_service import CliService
    from cloudshell.snmp.snmp_parameters import (
        SNMPReadParameters,
        SNMPV3Parameters,
        SNMPWriteParameters,
    )

    from ..cli.panos_cli_configurator import PanOSCliConfigurator

    SnmpParams = Union[SNMPReadParameters, SNMPWriteParameters, SNMPV3Parameters]


logger = logging.getLogger(__name__)


@define
class PanOSEnableDisableSnmpFlow(EnableDisableSnmpFlowInterface):
    _cli_configurator: PanOSCliConfigurator

    def enable_snmp(self, snmp_parameters: SnmpParams) -> None:
        with self._cli_configurator.config_mode_service() as cli_service:
            if snmp_parameters.version == snmp_parameters.SnmpVersion.V3:
                self._enable_snmp_v3(cli_service, snmp_parameters)
            else:
                self._enable_snmp(cli_service, snmp_parameters)

    @staticmethod
    def _enable_snmp(cli_service: CliService, snmp_parameters: SnmpParams) -> None:
        """Enable SNMPv1,2."""
        snmp_community = snmp_parameters.snmp_community
        if not snmp_community:
            raise Exception("SNMP Community has to be defined")

        logger.info(f"Start creating SNMP community {snmp_community}")
        snmp_actions = EnableDisableSnmpV2Actions(cli_service)
        system_actions = SystemConfigurationActions(cli_service)
        snmp_actions.enable_snmp_service()
        snmp_actions.enable_snmp(community=snmp_community)
        system_actions.commit_changes()

        logger.info(f"SNMP community {snmp_community} created")

    @staticmethod
    def _enable_snmp_v3(cli_service: CliService, snmp_parameters: SnmpParams) -> None:
        """Enable SNMPv3."""
        logger.info("Start creating SNMPv3 configuration")
        snmp_actions = EnableDisableSnmpV3Actions(cli_service)
        system_actions = SystemConfigurationActions(cli_service)

        snmp_actions.enable_snmp_service()
        snmp_actions.enable_snmp(snmp_params=snmp_parameters)
        system_actions.commit_changes()

        logger.info(f"SNMP User {snmp_parameters.snmp_user} created")

    def disable_snmp(self, snmp_parameters: SnmpParams) -> None:
        with self._cli_configurator.config_mode_service() as cli_service:
            if snmp_parameters.version == snmp_parameters.SnmpVersion.V3:
                self._disable_snmp_v3(cli_service)
            else:
                self._disable_snmp(cli_service)

    @staticmethod
    def _disable_snmp(cli_service: CliService) -> None:
        """Disable SNMPv1,2."""
        logger.info("Start removing SNMP v2c configuration")
        snmp_actions = EnableDisableSnmpV2Actions(cli_service)
        system_actions = SystemConfigurationActions(cli_service)
        snmp_actions.disable_snmp()
        system_actions.commit_changes()

        logger.info("SNMP v2c configuration removed")

    @staticmethod
    def _disable_snmp_v3(cli_service: CliService) -> None:
        """Disable SNMPv3."""
        logger.info("Start removing SNMP v3 configuration")
        snmp_actions = EnableDisableSnmpV3Actions(cli_service)
        system_actions = SystemConfigurationActions(cli_service)

        snmp_actions.disable_snmp()
        system_actions.commit_changes()

        logger.info("SNMP v3 configuration removed")
