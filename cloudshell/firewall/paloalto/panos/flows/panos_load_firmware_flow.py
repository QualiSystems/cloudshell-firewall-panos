#!/usr/bin/python
# -*- coding: utf-8 -*-

from cloudshell.devices.flows.action_flows import LoadFirmwareFlow
from cloudshell.devices.networking_utils import UrlParser
from cloudshell.firewall.paloalto.panos.command_actions.system_actions import SystemActions, FirmwareActions


class PanOSLoadFirmwareFlow(LoadFirmwareFlow):
    FILE_TYPE = "software"

    def __init__(self, cli_handler, logger):
        super(PanOSLoadFirmwareFlow, self).__init__(cli_handler, logger)

    def execute_flow(self, path, vrf, timeout):
        """Load a firmware onto the device

        :param path: The path to the firmware file, including the firmware file name
        :param vrf: Virtual Routing and Forwarding Name
        :param timeout:
        :return:
        """

        connection_dict = UrlParser.parse_url(path)

        with self._cli_handler.get_cli_service(self._cli_handler.enable_mode) as enable_session:
            config_file_name = connection_dict.get(UrlParser.FILENAME)
            system_actions = SystemActions(enable_session, self._logger)
            load_firmware_action = FirmwareActions(enable_session, self._logger)
            system_actions.import_config(filename=config_file_name,
                                         protocol=connection_dict.get(UrlParser.SCHEME),
                                         host=connection_dict.get(UrlParser.HOSTNAME),
                                         file_type=self.FILE_TYPE,
                                         port=connection_dict.get(UrlParser.PORT),
                                         user=connection_dict.get(UrlParser.USERNAME),
                                         password=connection_dict.get(UrlParser.PASSWORD),
                                         remote_path=connection_dict.get(UrlParser.PATH))

            load_firmware_action.install_software(config_file_name)
