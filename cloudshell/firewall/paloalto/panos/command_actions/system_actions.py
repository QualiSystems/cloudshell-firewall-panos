from __future__ import annotations

import logging
import os
import re

import tftpy
from attrs import define

from cloudshell.cli.command_template.command_template_executor import (
    CommandTemplateExecutor,
)
from cloudshell.cli.service.cli_service import CliService

from cloudshell.firewall.paloalto.panos.command_templates import configuration, firmware
from cloudshell.firewall.paloalto.panos.helpers.temp_dir_context import TempDirContext

logger = logging.getLogger(__name__)


@define
class SystemConfigurationActions:
    _cli_service: CliService

    def save_config(self, destination, action_map=None, error_map=None, timeout=None):
        """Save current configuration to local file on device filesystem.

        :param destination: destination file
        :param action_map: actions will be taken during executing commands
        :param error_map: errors will be raised during executing commands
        :param timeout: session timeout
        :raise Exception:
        """
        output = CommandTemplateExecutor(
            cli_service=self._cli_service,
            command_template=configuration.SAVE_CONFIG,
            action_map=action_map,
            error_map=error_map,
            timeout=timeout,
        ).execute_command(filename=destination)

        pattern = rf"Config saved to {destination}"
        status_match = re.search(pattern, output, re.IGNORECASE)

        if not status_match:
            logger.error(f"Save configuration failed: {output}")
            raise Exception(
                "Save configuration", "Save configuration failed. See logs for details"
            )

    def load_config(self, source, action_map=None, error_map=None, timeout=None):
        """Load saved on device filesystem configuration.

        :param source: source file
        :param action_map: actions will be taken during executing commands
        :param error_map: errors will be raised during executing commands
        :param timeout: session timeout
        :raise Exception:
        """
        output = CommandTemplateExecutor(
            cli_service=self._cli_service,
            command_template=configuration.LOAD_CONFIG,
            action_map=action_map,
            error_map=error_map,
            timeout=timeout,
        ).execute_command(filename=source)

        pattern = rf"Config loaded from {source}"
        status_match = re.search(pattern, output, re.IGNORECASE)

        if not status_match:
            logger.error(f"Load configuration failed: {output}")
            raise Exception(
                "Load configuration", "Load configuration failed. See logs for details"
            )

    def commit_changes(self, action_map=None, error_map=None):
        CommandTemplateExecutor(
            cli_service=self._cli_service,
            command_template=configuration.COMMIT,
            action_map=action_map,
            error_map=error_map,
        ).execute_command()


@define
class SystemActions:
    _cli_service: CliService

    def import_config(
        self,
        filename,
        protocol,
        host,
        file_type,
        port=None,
        user=None,
        password=None,
        remote_path=None,
    ):
        """Import configuration file from remote TFTP or SCP server."""
        if protocol.upper() == "TFTP":
            output = CommandTemplateExecutor(
                self._cli_service, configuration.COPY_FROM_TFTP
            ).execute_command(
                remote_path=remote_path, file_type=file_type, tftp_host=host, port=port
            )
            pattern = r"Received \d+ bytes in -?\d+.\d+ seconds"
        elif protocol.upper() == "SCP":
            src = f"{user}@{host}:{remote_path}"

            action_map = {
                "[Pp]assword:": lambda session, logger: session.send_line(
                    password, logger
                ),
                "yes/no": lambda session, logger: session.send_line("yes", logger),
            }

            output = CommandTemplateExecutor(
                self._cli_service, configuration.COPY_FROM_SCP, action_map=action_map
            ).execute_command(src=src, file_type=file_type, port=port)
            pattern = rf"{filename} saved"
        else:
            raise Exception(
                f"Import {file_type}",
                f"Protocol type <{protocol}> is unsupportable",
            )

        status_match = re.search(pattern, output, re.IGNORECASE)

        if not status_match:
            logger.error(f"Import {file_type} failed: {output}")
            raise Exception(
                f"Import {file_type}",
                f"Import {file_type} failed. See logs for details",
            )

    def export_config(
        self,
        config_file_name,
        remote_file_name,
        protocol,
        host,
        port=None,
        user=None,
        password=None,
        remote_path=None,
    ):
        """Export configuration file to remote TFTP or SCP server.

        config_file_name - Name of configuration file on device
        remote_file_name - Name of configuration file on remote SCP/TFTP Server
        """
        if protocol.upper() == "TFTP":
            output = CommandTemplateExecutor(
                self._cli_service, configuration.COPY_TO_TFTP
            ).execute_command(filename=config_file_name, tftp_host=host, port=port)
            if config_file_name != remote_file_name:
                self._rename_file_on_tftp(
                    initial_file_name=config_file_name,
                    new_file_name=remote_file_name,
                    tftp_host=host,
                    tftp_port=port,
                )
            pattern = r"Sent \d+ bytes in -?\d+.\d+ seconds"
        elif protocol.upper() == "SCP":
            dst = f"{user}@{host}:{remote_path}"

            action_map = {
                "[Pp]assword:": lambda session, logger: session.send_line(
                    password, logger
                ),
                "yes/no": lambda session, logger: session.send_line("yes", logger),
            }

            output = CommandTemplateExecutor(
                self._cli_service, configuration.COPY_TO_SCP, action_map=action_map
            ).execute_command(filename=config_file_name, dst=dst, port=port)
            pattern = rf"{config_file_name}\s+100%"
        else:
            raise Exception(
                "Export configuration",
                f"Protocol type <{protocol}> is unsupportable",
            )

        status_match = re.search(pattern, output, re.IGNORECASE)

        if not status_match:
            logger.error(f"Export configuration failed: {output}")
            raise Exception(
                "Export configuration",
                "Export configuration failed. See logs for details",
            )

    def _rename_file_on_tftp(
        self, initial_file_name, new_file_name, tftp_host, tftp_port
    ):
        """Rename file on remote TFTP Server."""
        if tftp_port:
            tftp = tftpy.TftpClient(host=tftp_host, port=int(tftp_port))
        else:
            tftp = tftpy.TftpClient(host=tftp_host)

        with TempDirContext(new_file_name) as temp_dir:
            tftp.download(
                filename=initial_file_name, output=os.path.join(temp_dir, new_file_name)
            )
            tftp.upload(
                filename=new_file_name, input=os.path.join(temp_dir, new_file_name)
            )

    def reload_device(self, timeout=500, action_map=None, error_map=None):
        """Reload device.

        :param timeout: session reconnect timeout
        :param action_map: actions will be taken during executing commands
        :param error_map: errors will be raised during executing commands
        """
        try:
            CommandTemplateExecutor(
                self._cli_service, configuration.RELOAD
            ).execute_command(action_map=action_map, error_map=error_map)
        except Exception:
            logger.info("Device rebooted, starting reconnect")
        self._cli_service.reconnect(timeout)

    def shutdown(self, action_map=None, error_map=None):
        """Shutdown the system."""
        try:
            CommandTemplateExecutor(
                self._cli_service, configuration.SHUTDOWN
            ).execute_command(action_map=action_map, error_map=error_map)
        except Exception:
            logger.info("Device turned off")


@define
class FirmwareActions:
    _cli_service: CliService

    def install_software(self, software_file_name):
        """Set boot firmware file.

        :param software_file_name: software file name
        """
        CommandTemplateExecutor(
            self._cli_service, firmware.INSTALL_SOFTWARE
        ).execute_command(software_file_name=software_file_name)
