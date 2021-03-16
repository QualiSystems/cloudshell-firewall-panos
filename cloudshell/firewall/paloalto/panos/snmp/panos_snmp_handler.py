#!/usr/bin/python
# -*- coding: utf-8 -*-
from cloudshell.snmp.snmp_configurator import (
    EnableDisableSnmpConfigurator,
    EnableDisableSnmpFlowInterface,
)

from cloudshell.firewall.paloalto.panos.flows.panos_disable_snmp_flow import (
    PanOSDisableSnmpFlow,
)
from cloudshell.firewall.paloalto.panos.flows.panos_enable_snmp_flow import (
    PanOSEnableSnmpFlow,
)


class PanOSEnableDisableSnmpFlow(EnableDisableSnmpFlowInterface):
    DEFAULT_SNMP_VIEW = "quali_snmp_view"
    DEFAULT_SNMP_GROUP = "quali_snmp_group"

    def __init__(self, cli_handler, logger):
        """Enable snmp flow.

        :param cli_handler:
        :param logger:
        :return:
        """
        self._logger = logger
        self._cli_handler = cli_handler

    def enable_snmp(self, snmp_parameters):
        PanOSEnableSnmpFlow(self._cli_handler, self._logger).enable_flow(
            snmp_parameters
        )

    def disable_snmp(self, snmp_parameters):
        PanOSDisableSnmpFlow(self._cli_handler, self._logger).disable_flow(
            snmp_parameters
        )


class PanOSSnmpHandler(EnableDisableSnmpConfigurator):
    def __init__(self, resource_config, logger, cli_handler):
        self.cli_handler = cli_handler
        enable_disable_snmp_flow = PanOSEnableDisableSnmpFlow(self.cli_handler, logger)
        super(PanOSSnmpHandler, self).__init__(
            enable_disable_snmp_flow, resource_config, logger
        )
