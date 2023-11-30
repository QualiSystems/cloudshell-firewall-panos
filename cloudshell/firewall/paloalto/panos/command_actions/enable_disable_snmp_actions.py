from __future__ import annotations

from attrs import define
from typing import TYPE_CHECKING

from cloudshell.cli.command_template.command_template_executor import (
    CommandTemplateExecutor,
)

from cloudshell.firewall.paloalto.panos.command_templates import enable_disable_snmp

if TYPE_CHECKING:
    from cloudshell.cli.service.cli_service import CliService
    from cloudshell.snmp.snmp_parameters import SNMPV3Parameters


@define
class EnableDisableSnmpV2Actions:
    _cli_service: CliService

    def enable_snmp_service(self):
        """Enable SNMP server."""
        CommandTemplateExecutor(
            self._cli_service, enable_disable_snmp.ENABLE_SNMP_SERVICE
        ).execute_command()

    def enable_snmp(self, community: str):
        """Enable snmp on the device."""
        CommandTemplateExecutor(
            self._cli_service, enable_disable_snmp.CONFIGURE_V2C
        ).execute_command(community=community)

    def disable_snmp(self):
        """Disable snmp on the device."""
        CommandTemplateExecutor(
            self._cli_service, enable_disable_snmp.DELETE_SNMP_CONFIG
        ).execute_command()


@define
class EnableDisableSnmpV3Actions:
    _cli_service: CliService

    def enable_snmp_service(self):
        """Enable SNMP server."""
        CommandTemplateExecutor(
            self._cli_service, enable_disable_snmp.ENABLE_SNMP_SERVICE
        ).execute_command()

    def enable_snmp(
            self,
            snmp_params: SNMPV3Parameters,
            views: str = "quali_views",
            view: str = "quali_view",
            oid: int = 1,
    ):
        """Configure SNMP."""
        CommandTemplateExecutor(
            self._cli_service, enable_disable_snmp.CONFIGURE_V3_VIEW
        ).execute_command(views=views, view=view, oid=oid)
        CommandTemplateExecutor(
            self._cli_service, enable_disable_snmp.CONFIGURE_V3
        ).execute_command(
            v3_user=snmp_params.snmp_user,
            v3_auth_pass=snmp_params.snmp_password,
            v3_priv_pass=snmp_params.snmp_private_key,
            views=views,
        )

    def disable_snmp(self):
        """Disable snmp on the device."""
        CommandTemplateExecutor(
            self._cli_service, enable_disable_snmp.DELETE_SNMP_CONFIG
        ).execute_command()
