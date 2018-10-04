#!/usr/bin/python
# -*- coding: utf-8 -*-

from cloudshell.devices.runners.configuration_runner import ConfigurationRunner
from cloudshell.firewall.paloalto.panos.flows.panos_save_flow import PanoOSSaveFlow
from cloudshell.firewall.paloalto.panos.flows.panos_restore_flow import PanOSRestoreFlow


class PanOSConfigurationRunner(ConfigurationRunner):
    @property
    def save_flow(self):
        return PanoOSSaveFlow(cli_handler=self.cli_handler, logger=self._logger)

    @property
    def restore_flow(self):
        return PanOSRestoreFlow(cli_handler=self.cli_handler, logger=self._logger)

    @property
    def file_system(self):
        return ""
