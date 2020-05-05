#!/usr/bin/python
# -*- coding: utf-8 -*-

from cloudshell.devices.flows.action_flows import RestoreConfigurationFlow
from cloudshell.devices.networking_utils import UrlParser
from cloudshell.firewall.paloalto.panos.command_actions.system_actions import SystemActions, SystemConfigurationActions


class PanOSRestoreFlow(RestoreConfigurationFlow):
    FILE_TYPE = "configuration"

    def __init__(self, cli_handler, logger):
        super(PanOSRestoreFlow, self).__init__(cli_handler, logger)

    def execute_flow(self, path, configuration_type, restore_method, vrf_management_name=None):
        """ Execute flow which save selected file to the provided destination

        :param path: the path to the configuration file, including the configuration file name
        :param restore_method: the restore method to use when restoring the configuration file.
                               Possible Values are append and override
        :param configuration_type: the configuration type to restore. Possible values are startup and running
        :param vrf_management_name: Virtual Routing and Forwarding Name
        """

        if not restore_method:
            restore_method = "override"

        if not configuration_type:
            configuration_type = "running-config"
        elif not configuration_type.endswith("-config"):
            configuration_type += "-config"

        if configuration_type not in ["running-config", "startup-config"]:
            raise Exception(self.__class__.__name__,
                            "Device doesn't support restoring '{}' configuration type".format(configuration_type))

        if restore_method.lower() == "append":
            raise Exception(self.__class__.__name__,
                            "Device doesn't support restoring '{0}' configuration type with '{1}' method"
                            .format(configuration_type, restore_method))

        connection_dict = UrlParser.parse_url(path)

        with self._cli_handler.get_cli_service(self._cli_handler.enable_mode) as enable_session:

            config_file_name = connection_dict.get(UrlParser.FILENAME)
            restore_actions = SystemActions(enable_session, self._logger)
            restore_actions.import_config(filename=config_file_name,
                                          protocol=connection_dict.get(UrlParser.SCHEME),
                                          host=connection_dict.get(UrlParser.HOSTNAME),
                                          file_type=self.FILE_TYPE,
                                          port=connection_dict.get(UrlParser.PORT),
                                          user=connection_dict.get(UrlParser.USERNAME),
                                          password=connection_dict.get(UrlParser.PASSWORD),
                                          remote_path=connection_dict.get(UrlParser.PATH))

            with enable_session.enter_mode(self._cli_handler.config_mode) as config_session:
                restore_conf_action = SystemConfigurationActions(config_session, self._logger)
                restore_conf_action.load_config(config_file_name)
                restore_conf_action.commit_changes()

            if configuration_type == "running-config":
                restore_actions.reload_device()
