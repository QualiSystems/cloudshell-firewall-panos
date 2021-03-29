#!/usr/bin/python
# -*- coding: utf-8 -*-

import os
import re

import tftpy

from cloudshell.cli.command_template.command_template_executor import (
    CommandTemplateExecutor,
)

from cloudshell.firewall.paloalto.panos.command_templates import configuration, firmware
from cloudshell.firewall.paloalto.panos.helpers.temp_dir_context import TempDirContext


class SystemConfigurationActions(object):
    def __init__(self, cli_service, logger):
        """Reboot actions.

        :param cli_service: default mode cli_service
        :type cli_service: CliService
        :param logger:
        :type logger: Logger
        :return:
        """
        self._cli_service = cli_service
        self._logger = logger

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

        pattern = r"Config saved to {dst_file}".format(dst_file=destination)
        status_match = re.search(pattern, output, re.IGNORECASE)

        if not status_match:
            self._logger.error("Save configuration failed: {err}".format(err=output))
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

        pattern = r"Config loaded from {src_file}".format(src_file=source)
        status_match = re.search(pattern, output, re.IGNORECASE)

        if not status_match:
            self._logger.error("Load configuration failed: {err}".format(err=output))
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


class SystemActions(object):
    def __init__(self, cli_service, logger):
        """Reboot actions.

        :param cli_service: default mode cli_service
        :type cli_service: CliService
        :param logger:
        :type logger: Logger
        :return:
        """
        self._cli_service = cli_service
        self._logger = logger

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
        if remote_path.endswith("/"):
            file_path = remote_path + filename
        else:
            file_path = remote_path + "/" + filename

        if protocol.upper() == "TFTP":
            output = CommandTemplateExecutor(
                self._cli_service, configuration.COPY_FROM_TFTP
            ).execute_command(
                remote_path=file_path, file_type=file_type, tftp_host=host, port=port
            )
            pattern = r"Received \d+ bytes in -?\d+.\d+ seconds"
        elif protocol.upper() == "SCP":
            src = "{username}@{host}:{path}".format(
                username=user, host=host, path=file_path
            )

            action_map = {
                "[Pp]assword:": lambda session, logger: session.send_line(
                    password, logger
                ),
                "yes/no": lambda session, logger: session.send_line("yes", logger),
            }

            output = CommandTemplateExecutor(
                self._cli_service, configuration.COPY_FROM_SCP, action_map=action_map
            ).execute_command(src=src, file_type=file_type, port=port)
            pattern = r"{} saved".format(filename)
        else:
            raise Exception(
                "Import {}".format(file_type),
                "Protocol type <{}> is unsupportable".format(protocol),
            )

        status_match = re.search(pattern, output, re.IGNORECASE)

        if not status_match:
            self._logger.error(
                "Import {file_type} failed: {err}".format(
                    file_type=file_type, err=output
                )
            )
            raise Exception(
                "Import {file_type}".format(file_type=file_type),
                "Import {file_type} failed. See logs for details".format(
                    file_type=file_type
                ),
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
            self._rename_file_on_tftp(
                initial_file_name=config_file_name,
                new_file_name=remote_file_name,
                tftp_host=host,
                tftp_port=port,
            )
            pattern = r"Sent \d+ bytes in -?\d+.\d+ seconds"
        elif protocol.upper() == "SCP":
            if remote_path.endswith("/"):
                file_path = remote_path + remote_file_name
            else:
                file_path = remote_path + "/" + remote_file_name

            dst = "{username}@{host}:{path}".format(
                username=user, host=host, path=file_path
            )

            action_map = {
                "[Pp]assword:": lambda session, logger: session.send_line(
                    password, logger
                ),
                "yes/no": lambda session, logger: session.send_line("yes", logger),
            }

            output = CommandTemplateExecutor(
                self._cli_service, configuration.COPY_TO_SCP, action_map=action_map
            ).execute_command(filename=config_file_name, dst=dst, port=port)
            pattern = r"{}\s+100%".format(config_file_name)
        else:
            raise Exception(
                "Export configuration",
                "Protocol type <{}> is unsupportable".format(protocol),
            )

        status_match = re.search(pattern, output, re.IGNORECASE)

        if not status_match:
            self._logger.error("Export configuration failed: {err}".format(err=output))
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
            self._logger.info("Device rebooted, starting reconnect")
        self._cli_service.reconnect(timeout)

    def shutdown(self, action_map=None, error_map=None):
        """Shutdown the system."""
        try:
            CommandTemplateExecutor(
                self._cli_service, configuration.SHUTDOWN
            ).execute_command(action_map=action_map, error_map=error_map)
        except Exception:
            self._logger.info("Device turned off")


class FirmwareActions(object):
    def __init__(self, cli_service, logger):
        """Reboot actions.

        :param cli_service: default mode cli_service
        :type cli_service: CliService
        :param logger:
        :type logger: Logger
        :return:
        """
        self._cli_service = cli_service
        self._logger = logger

    def install_software(self, software_file_name):
        """Set boot firmware file.

        :param software_file_name: software file name
        """
        CommandTemplateExecutor(
            self._cli_service, firmware.INSTALL_SOFTWARE
        ).execute_command(software_file_name=software_file_name)
