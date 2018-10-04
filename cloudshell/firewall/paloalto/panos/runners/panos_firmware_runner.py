#!/usr/bin/python
# -*- coding: utf-8 -*-

from cloudshell.devices.runners.firmware_runner import FirmwareRunner
from cloudshell.firewall.paloalto.panos.flows.panos_load_firmware_flow import PanOSLoadFirmwareFlow


class PanOSFirmwareRunner(FirmwareRunner):
    RELOAD_TIMEOUT = 500

    @property
    def load_firmware_flow(self):
        return PanOSLoadFirmwareFlow(cli_handler=self.cli_handler, logger=self._logger)
