#!/usr/bin/python
# -*- coding: utf-8 -*-

import os

from cloudshell.shell.flows.autoload.basic_flow import AbstractAutoloadFlow

from cloudshell.firewall.paloalto.panos.autoload.panos_generic_snmp_autoload import (
    PanOSGenericSNMPAutoload,
)


class PanOSSnmpAutoloadFlow(AbstractAutoloadFlow):
    MIBS_FOLDER = os.path.join(os.path.dirname(__file__), os.pardir, "mibs")

    def __init__(self, logger, snmp_handler):
        super(PanOSSnmpAutoloadFlow, self).__init__(logger)
        self._snmp_handler = snmp_handler

    def _autoload_flow(self, supported_os, resource_model):
        with self._snmp_handler.get_service() as snmp_service:
            snmp_service.add_mib_folder_path(self.MIBS_FOLDER)
            snmp_service.load_mib_tables(
                [
                    "PAN-COMMON-MIB",
                    "PAN-GLOBAL-REG",
                    "PAN-GLOBAL-TC",
                    "PAN-PRODUCTS-MIB",
                    "PAN-ENTITY-EXT-MIB",
                ]
            )
            snmp_autoload = PanOSGenericSNMPAutoload(snmp_service, self._logger)

            snmp_autoload.if_table_service.PORT_CHANNEL_NAME = ["ae"]
            return snmp_autoload.discover(
                supported_os, resource_model, validate_module_id_by_port_name=False
            )
