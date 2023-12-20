from __future__ import annotations

import logging
from typing import TYPE_CHECKING

from cloudshell.shell.flows.configuration.basic_flow import (
    AbstractConfigurationFlow,
    ConfigurationType,
    RestoreMethod,
)

from cloudshell.paloalto.command_actions.system_actions import (
    SystemActions,
    SystemConfigurationActions,
)

if TYPE_CHECKING:
    from typing import ClassVar, Union

    from cloudshell.shell.flows.utils.url import BasicLocalUrl, RemoteURL
    from cloudshell.shell.standards.firewall.resource_config import (
        FirewallResourceConfig,
    )

    from ..cli.panos_cli_configurator import PanOSCliConfigurator

    Url = Union[RemoteURL, BasicLocalUrl]


logger = logging.getLogger(__name__)


class PanOSConfigurationFlow(AbstractConfigurationFlow):
    MAX_CONFIG_FILE_NAME_LENGTH: ClassVar[int] = 28
    # Maximum filename length supported by devices
    # Config name example {resource_name}-{configuration_type}-{timestamp}
    #   configuration_type - running/startup = 7ch
    #   timestamp - ddmmyy-HHMMSS = 13ch
    #   file extension - .xml = 4ch
    #   CloudShell reserves 7ch+13ch+4ch+3ch(three delimiters "-") = 27ch
    FILE_TYPE: ClassVar[str] = "configuration"
    FILE_EXTENSION: ClassVar[str] = "xml"

    def __init__(
        self,
        resource_config: FirewallResourceConfig,
        cli_configurator: PanOSCliConfigurator,
    ):
        super().__init__(resource_config)
        self.cli_configurator = cli_configurator

    @property
    def file_system(self) -> str:
        return ""

    def _save_flow(
        self,
        file_dst_url: Url,
        configuration_type: ConfigurationType,
        vrf_management_name: str | None,
    ) -> str:
        """Backup config.

        Backup 'startup-config' or 'running-config' from
        device to provided file_system [ftp|tftp].
        Also possible to backup config to localhost
        :param file_dst_url: destination url, remote or local, where file will be saved
        :param configuration_type: type of configuration
        that will be saved (StartUp or Running)
        :param vrf_management_name: Virtual Routing and
        Forwarding management name
        """
        if configuration_type == ConfigurationType.RUNNING:
            config_file_name = f"{file_dst_url.filename}.{self.FILE_EXTENSION}"
            with self.cli_configurator.config_mode_service() as config_cli_service:
                save_conf_action = SystemConfigurationActions(config_cli_service)
                save_conf_action.save_config(config_file_name)
        else:
            # Filename for startup configuration is running-config.xml
            config_file_name = "running-config.xml"

        with self.cli_configurator.enable_mode_service() as enable_cli_service:
            save_actions = SystemActions(enable_cli_service)
            save_actions.export_config(
                config_file_name=config_file_name,
                remote_file_name=f"{file_dst_url.filename}.{self.FILE_EXTENSION}",
                protocol=file_dst_url.scheme,
                host=file_dst_url.host,
                port=file_dst_url.port,
                user=file_dst_url.username,
                password=file_dst_url.password,
                remote_path=file_dst_url.path,
            )
        return f"{file_dst_url.filename}.{self.FILE_EXTENSION}"

    def _restore_flow(
        self,
        config_path: Url,
        configuration_type: ConfigurationType,
        restore_method: RestoreMethod,
        vrf_management_name: str | None,
    ) -> None:
        """Restore configuration on device from provided configuration file.

        Restore configuration from local file system or ftp/tftp
        server into 'running-config' or 'startup-config'.
        :param config_path: relative path to the file on the
        remote host tftp://server/sourcefile
        :param configuration_type: the configuration
        type to restore (StartUp or Running)
        :param restore_method: override current config or not
        :param vrf_management_name: Virtual Routing and
        Forwarding management name
        """
        if not restore_method:
            restore_method = RestoreMethod.OVERRIDE

        if restore_method == RestoreMethod.APPEND:
            raise Exception(
                f"Device doesn't support restoring with parameters: "
                f"configuration type '{configuration_type}', method '{restore_method}'"
            )

        with self.cli_configurator.enable_mode_service() as enable_cli_service:
            restore_actions = SystemActions(enable_cli_service)
            restore_actions.import_config(
                filename=config_path.filename,
                protocol=config_path.scheme,
                host=config_path.host,
                file_type=self.FILE_TYPE,
                port=config_path.port,
                user=config_path.username,
                password=config_path.password,
                remote_path=config_path.path,
            )

            with enable_cli_service.enter_mode(
                self.cli_configurator.config_mode
            ) as config_cli_service:
                restore_conf_action = SystemConfigurationActions(config_cli_service)
                restore_conf_action.load_config(config_path.filename)
                restore_conf_action.commit_changes()

            if configuration_type == ConfigurationType.RUNNING:
                restore_actions.reload_device()
