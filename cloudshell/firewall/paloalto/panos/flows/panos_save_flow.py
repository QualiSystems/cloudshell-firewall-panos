#!/usr/bin/python
# -*- coding: utf-8 -*-

from cloudshell.devices.flows.action_flows import SaveConfigurationFlow
from cloudshell.devices.networking_utils import UrlParser
from cloudshell.firewall.paloalto.panos.command_actions.system_actions import SystemActions, SystemConfigurationActions


class PanoOSSaveFlow(SaveConfigurationFlow):
    CONF_FILE_NAME_LENGTH = 32

    def __init__(self, cli_handler, logger):
        super(PanoOSSaveFlow, self).__init__(cli_handler, logger)

    def execute_flow(self, folder_path, configuration_type, vrf_management_name=None):
        """ Execute flow which save selected file to the provided destination

        :param folder_path: destination path where file will be saved
        :param configuration_type: source file, which will be saved
        :param vrf_management_name: Virtual Routing and Forwarding Name
        :return: saved configuration file name
        """

        if not configuration_type.endswith("-config"):
            configuration_type += "-config"

        if configuration_type not in ["running-config", "startup-config"]:
            raise Exception(self.__class__.__name__,
                            "Device doesn't support saving '{}' configuration type".format(configuration_type))

        connection_dict = UrlParser.parse_url(folder_path)

        with self._cli_handler.get_cli_service(self._cli_handler.enable_mode) as enable_session:
            if configuration_type == "running-config":
                config_file_name = self._verify_config_name(connection_dict.get(UrlParser.FILENAME))
                with enable_session.enter_mode(self._cli_handler.config_mode) as config_session:
                    save_conf_action = SystemConfigurationActions(config_session, self._logger)
                    save_conf_action.save_config(config_file_name)
            else:
                # Filename for startup configuration is running-config.xml
                config_file_name = "running-config.xml"

            save_actions = SystemActions(enable_session, self._logger)
            save_actions.export_config(filename=config_file_name,
                                       protocol=connection_dict.get(UrlParser.SCHEME),
                                       host=connection_dict.get(UrlParser.HOSTNAME),
                                       port=connection_dict.get(UrlParser.PORT),
                                       user=connection_dict.get(UrlParser.USERNAME),
                                       password=connection_dict.get(UrlParser.PASSWORD),
                                       remote_path=connection_dict.get(UrlParser.PATH))

    def _verify_config_name(self, config_name):
        """ Verify configuration name correctness

        Config name example {resource_name}-{confguration_type}-{timestamp}
        configuration_type - running/startup = 7ch
        timestamp - ddmmyy-HHMMSS = 13ch
        CloudShell reserves 7ch+13ch+2ch(two delimiters "-") = 22ch
        """

        reserved_length = 22

        self._logger.debug("Original configuration name: {}".format(config_name))
        if reserved_length < self.CONF_FILE_NAME_LENGTH < len(config_name):
            splitted = config_name.split("-")
            resource_name = "-".join(splitted[:-3])[:self.CONF_FILE_NAME_LENGTH-reserved_length]
            config_name = "-".join([resource_name] + splitted[-3:])
        self._logger.debug("Verified configuration name: {}".format(config_name))

        return config_name
