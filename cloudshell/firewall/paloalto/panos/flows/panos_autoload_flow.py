from __future__ import annotations

from typing import TYPE_CHECKING

from cloudshell.shell.flows.autoload.basic_flow import AbstractAutoloadFlow

from ..autoload.panos_generic_snmp_autoload import PanOSGenericSNMPAutoload

if TYPE_CHECKING:
    from cloudshell.shell.core.driver_context import AutoLoadDetails
    from cloudshell.shell.standards.firewall.autoload_model import (
        FirewallResourceModel,
    )
    from cloudshell.snmp.snmp_configurator import EnableDisableSnmpConfigurator


class PanOSSnmpAutoloadFlow(AbstractAutoloadFlow):
    """Autoload flow."""
    def __init__(self, snmp_configurator: EnableDisableSnmpConfigurator):
        super().__init__()
        self._snmp_configurator = snmp_configurator

    def _autoload_flow(
            self,
            supported_os: list[str],
            resource_model: FirewallResourceModel
    ) -> AutoLoadDetails:
        """Autoload Flow."""
        with self._snmp_configurator.get_service() as snmp_service:
            snmp_autoload = PanOSGenericSNMPAutoload(snmp_service, resource_model)
            autoload_details = snmp_autoload.discover(supported_os)
        return autoload_details
