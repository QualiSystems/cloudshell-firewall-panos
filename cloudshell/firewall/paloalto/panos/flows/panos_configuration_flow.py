#!/usr/bin/python
import re

from cloudshell.firewall.paloalto.panos.command_actions.system_actions import (
    SystemActions,
    SystemConfigurationActions,
)
from cloudshell.shell.flows.configuration.basic_flow import (
    AUTHORIZATION_REQUIRED_STORAGE,
    AbstractConfigurationFlow,
)
from cloudshell.shell.flows.utils.networking_utils import UrlParser


class PanOSConfigurationFlow(AbstractConfigurationFlow):
    CONF_FILE_NAME_LENGTH = 32
    FILE_TYPE = "configuration"

    def __init__(self, cli_handler, resource_config, logger):
        super().__init__(logger, resource_config)
        self._cli_handler = cli_handler

    @property
    def _file_system(self):
        return ""

    def _save_flow(self, folder_path, configuration_type, vrf_management_name=None):
        """Execute flow which save selected file to the provided destination.

        :param folder_path: destination path where file will be saved
        :param configuration_type: source file, which will be saved
        :param vrf_management_name: Virtual Routing and Forwarding Name
        :return: saved configuration file name
        """
        if not configuration_type.endswith("-config"):
            configuration_type += "-config"

        if configuration_type not in ["running-config", "startup-config"]:
            raise Exception(
                self.__class__.__name__,
                f"Device doesn't support saving '{configuration_type}' configuration type",
            )

        connection_dict = UrlParser.parse_url(folder_path)

        with self._cli_handler.get_cli_service(
            self._cli_handler.enable_mode
        ) as enable_session:
            remote_file_name = self._verify_config_name(
                connection_dict.get(UrlParser.FILENAME)
            )
            if configuration_type == "running-config":
                config_file_name = remote_file_name
                with enable_session.enter_mode(
                    self._cli_handler.config_mode
                ) as config_session:
                    save_conf_action = SystemConfigurationActions(
                        config_session, self._logger
                    )
                    save_conf_action.save_config(config_file_name)
            else:
                # Filename for startup configuration is running-config.xml
                config_file_name = "running-config.xml"

            save_actions = SystemActions(enable_session, self._logger)
            save_actions.export_config(
                config_file_name=config_file_name,
                remote_file_name=remote_file_name,
                protocol=connection_dict.get(UrlParser.SCHEME),
                host=connection_dict.get(UrlParser.HOSTNAME),
                port=connection_dict.get(UrlParser.PORT),
                user=connection_dict.get(UrlParser.USERNAME),
                password=connection_dict.get(UrlParser.PASSWORD),
                remote_path=connection_dict.get(UrlParser.PATH),
            )

    def _restore_flow(
        self, path, configuration_type, restore_method, vrf_management_name
    ):
        """Execute flow which save selected file to the provided destination.

        :param path: the path to the configuration file, including the configuration
            file name
        :param restore_method: the restore method to use when restoring the
            configuration file. Possible Values are append and override
        :param configuration_type: the configuration type to restore.
            Possible values are startup and running
        :param vrf_management_name: Virtual Routing and Forwarding Name
        """
        if not restore_method:
            restore_method = "override"

        if not configuration_type:
            configuration_type = "running-config"
        elif not configuration_type.endswith("-config"):
            configuration_type += "-config"

        if configuration_type not in ["running-config", "startup-config"]:
            raise Exception(
                self.__class__.__name__,
                f"Device doesn't support restoring '{configuration_type}' configuration type",
            )

        if restore_method.lower() == "append":
            raise Exception(
                self.__class__.__name__,
                "Device doesn't support restoring '{}' configuration type with '{}' method".format(
                    configuration_type, restore_method
                ),
            )

        connection_dict = UrlParser.parse_url(path)

        with self._cli_handler.get_cli_service(
            self._cli_handler.enable_mode
        ) as enable_session:
            config_file_name = connection_dict.get(UrlParser.FILENAME)
            restore_actions = SystemActions(enable_session, self._logger)
            restore_actions.import_config(
                filename=config_file_name,
                protocol=connection_dict.get(UrlParser.SCHEME),
                host=connection_dict.get(UrlParser.HOSTNAME),
                file_type=self.FILE_TYPE,
                port=connection_dict.get(UrlParser.PORT),
                user=connection_dict.get(UrlParser.USERNAME),
                password=connection_dict.get(UrlParser.PASSWORD),
                remote_path=connection_dict.get(UrlParser.PATH),
            )

            with enable_session.enter_mode(
                self._cli_handler.config_mode
            ) as config_session:
                restore_conf_action = SystemConfigurationActions(
                    config_session, self._logger
                )
                restore_conf_action.load_config(config_file_name)
                restore_conf_action.commit_changes()

            if configuration_type == "running-config":
                restore_actions.reload_device()

    def _verify_config_name(self, config_name):
        """Verify configuration name correctness.

        Config name example {resource_name}-{confguration_type}-{timestamp}
        configuration_type - running/startup = 7ch
        timestamp - ddmmyy-HHMMSS = 13ch
        CloudShell reserves 7ch+13ch+2ch(two delimiters "-") = 22ch
        """
        reserved_length = 22

        self._logger.debug(f"Original configuration name: {config_name}")
        if reserved_length < self.CONF_FILE_NAME_LENGTH < len(config_name):
            splitted = config_name.split("-")
            resource_name = "-".join(splitted[:-3])[
                : self.CONF_FILE_NAME_LENGTH - reserved_length
            ]
            config_name = "-".join([resource_name] + splitted[-3:])
        self._logger.debug(f"Verified configuration name: {config_name}")

        return config_name

    def _get_path(self, path=""):
        """Validate incoming path.

        If path is empty, build it from resource attributes,
        If path is invalid - raise exception

        :param path: path to remote file storage
        :return: valid path or :raise Exception:
        """
        if not path:
            host = self.resource_config.backup_location
            if ":" not in host:
                scheme = self.resource_config.backup_type
                if not scheme or scheme.lower() == self.DEFAULT_BACKUP_SCHEME.lower():
                    scheme = self._file_system
                scheme = re.sub("(:|/+).*$", "", scheme, re.DOTALL)
                host = re.sub("^/+", "", host)
                host = f"{scheme}://{host}"
            path = host
            url = UrlParser.parse_url(path)
        else:
            url_path = UrlParser.parse_url(path)
            host = self.resource_config.backup_location
            if "://" not in host:
                scheme = self.resource_config.backup_type
                if not scheme or scheme.lower() == self.DEFAULT_BACKUP_SCHEME.lower():
                    scheme = self._file_system
                scheme = re.sub("(:|/+).*$", "", scheme, re.DOTALL)
                host = re.sub("^/+", "", host)
                host = f"{scheme}://{host}"

            url = UrlParser.parse_url(host)
            url[UrlParser.FILENAME] = url_path.get(UrlParser.FILENAME)

        if url[UrlParser.SCHEME].lower() in AUTHORIZATION_REQUIRED_STORAGE:
            if UrlParser.USERNAME not in url or not url[UrlParser.USERNAME]:
                url[UrlParser.USERNAME] = self.resource_config.backup_user
            if UrlParser.PASSWORD not in url or not url[UrlParser.PASSWORD]:
                url[UrlParser.PASSWORD] = self.resource_config.backup_password
        try:
            result = UrlParser.build_url(url)
        except Exception as e:
            self._logger.error(f"Failed to build url: {e}")
            raise Exception(
                "ConfigurationOperations", "Failed to build path url to remote host"
            )
        return result
