#!/usr/bin/python
# -*- coding: utf-8 -*-

from cloudshell.devices.snmp_handler import SnmpHandler

from cloudshell.firewall.paloalto.panos.flows.panos_enable_snmp_flow import PanOSEnableSnmpFlow
from cloudshell.firewall.paloalto.panos.flows.panos_disable_snmp_flow import PanOSDisableSnmpFlow


class PanOSSnmpHandler(SnmpHandler):
    def __init__(self, resource_config, logger, api, cli_handler):
        super(PanOSSnmpHandler, self).__init__(resource_config, logger, api)
        self.cli_handler = cli_handler

    def _create_enable_flow(self):
        return PanOSEnableSnmpFlow(self.cli_handler, self._logger)

    def _create_disable_flow(self):
        return PanOSDisableSnmpFlow(self.cli_handler, self._logger)
