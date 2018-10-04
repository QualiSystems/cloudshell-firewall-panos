#!/usr/bin/python
# -*- coding: utf-8 -*-

from cloudshell.devices.runners.autoload_runner import AutoloadRunner
from cloudshell.firewall.paloalto.panos.flows.panos_autoload_flow import PanOSSnmpAutoloadFlow


class PanOSAutoloadRunner(AutoloadRunner):
    def __init__(self, resource_config, logger, snmp_handler):
        super(PanOSAutoloadRunner, self).__init__(resource_config)
        self._logger = logger
        self.snmp_handler = snmp_handler

    @property
    def autoload_flow(self):
        return PanOSSnmpAutoloadFlow(self.snmp_handler, self._logger)
