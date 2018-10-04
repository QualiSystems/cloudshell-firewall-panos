#!/usr/bin/python
# -*- coding: utf-8 -*-

import re

from cloudshell.cli.command_template.command_template_executor import CommandTemplateExecutor
from cloudshell.firewall.paloalto.panos.command_templates import configuration, firmware


class SystemConfigurationActions(object):
    def __init__(self, cli_service, logger):
        """
        Reboot actions
        :param cli_service: default mode cli_service
        :type cli_service: CliService
        :param logger:
        :type logger: Logger
        :return:
        """

        self._cli_service = cli_service
        self._logger = logger

    def save_config(self, destination, action_map=None, error_map=None, timeout=None):
        """ Save current configuration to local file on device filesystem.

        :param destination: destination file
        :param action_map: actions will be taken during executing commands, i.e. handles yes/no prompts
        :param error_map: errors will be raised during executing commands, i.e. handles Invalid Commands errors
        :param timeout: session timeout
        :raise Exception:
        """

        output = CommandTemplateExecutor(cli_service=self._cli_service,
                                         command_template=configuration.SAVE_CONFIG,
                                         action_map=action_map,
                                         error_map=error_map,
                                         timeout=timeout).execute_command(filename=destination)

        pattern = r"Config saved to {dst_file}".format(dst_file=destination)
        status_match = re.search(pattern, output, re.IGNORECASE)

        if not status_match:
            self._logger.error("Save configuration failed: {err}".format(err=output))
            raise Exception("Save configuration", "Save configuration failed. See logs for details")

    def load_config(self, source, action_map=None, error_map=None, timeout=None):
        """ Load saved on device filesystem configuration.

        :param source: source file
        :param action_map: actions will be taken during executing commands, i.e. handles yes/no prompts
        :param error_map: errors will be raised during executing commands, i.e. handles Invalid Commands errors
        :param timeout: session timeout
        :raise Exception:
        """

        output = CommandTemplateExecutor(cli_service=self._cli_service,
                                         command_template=configuration.LOAD_CONFIG,
                                         action_map=action_map,
                                         error_map=error_map,
                                         timeout=timeout).execute_command(filename=source)

        pattern = r"Config loaded from {src_file}".format(src_file=source)
        status_match = re.search(pattern, output, re.IGNORECASE)

        if not status_match:
            self._logger.error("Load configuration failed: {err}".format(err=output))
            raise Exception("Load configuration", "Load configuration failed. See logs for details")

    def commit_changes(self, action_map=None, error_map=None):
        CommandTemplateExecutor(cli_service=self._cli_service,
                                command_template=configuration.COMMIT,
                                action_map=action_map,
                                error_map=error_map).execute_command()


class SystemActions(object):
    def __init__(self, cli_service, logger):
        """
        Reboot actions
        :param cli_service: default mode cli_service
        :type cli_service: CliService
        :param logger:
        :type logger: Logger
        :return:
        """

        self._cli_service = cli_service
        self._logger = logger

    def import_config(self, filename, protocol, host, file_type, port=None, user=None, password=None, remote_path=None):
        """ Import configuration file from remote TFTP or SCP server """

        if remote_path.endswith("/"):
            file_path = remote_path + filename
        else:
            file_path = remote_path + "/" + filename

        if protocol.upper() == "TFTP":
            output = CommandTemplateExecutor(self._cli_service,
                                             configuration.COPY_FROM_TFTP).execute_command(remote_path=file_path,
                                                                                           file_type=file_type,
                                                                                           tftp_host=host,
                                                                                           port=port)
        elif protocol.upper() == "SCP":
            if password:
                src = "{username}:{password}@{host}:{path}".format(username=user,
                                                                   password=password,
                                                                   host=host,
                                                                   path=file_path)
            else:
                src = "{username}:@{host}:{path}".format(username=user,
                                                         host=host,
                                                         path=file_path)

            output = CommandTemplateExecutor(self._cli_service,
                                             configuration.COPY_FROM_SCP).execute_command(src=src,
                                                                                          file_type=file_type,
                                                                                          port=port)
        else:
            raise Exception("Import {}".format(file_type), "Protocol type <{}> is unsupportable".format(protocol))

        pattern = r"Received \d+ bytes in \d+.\d+ seconds"
        status_match = re.search(pattern, output, re.IGNORECASE)

        if not status_match:
            self._logger.error("Import {file_type} failed: {err}".format(file_type=file_type, err=output))
            raise Exception("Import {file_type}".format(file_type=file_type),
                            "Import {file_type} failed. See logs for details".format(file_type=file_type))

    def export_config(self, filename, protocol, host, port=None, user=None, password=None, remote_path=None):
        """ Export configuration file to remote TFTP or SCP server """

        if protocol.upper() == "TFTP":
            output = CommandTemplateExecutor(self._cli_service,
                                             configuration.COPY_TO_TFTP).execute_command(filename=filename,
                                                                                         tftp_host=host,
                                                                                         port=port)
        elif protocol.upper() == "SCP":
            if remote_path.endswith("/"):
                file_path = remote_path + filename
            else:
                file_path = remote_path + "/" + filename

            if password:
                dst = "{username}:{password}@{host}:{path}".format(username=user,
                                                                   password=password,
                                                                   host=host,
                                                                   path=file_path)
            else:
                dst = "{username}:@{host}:{path}".format(username=user,
                                                         host=host,
                                                         path=file_path)

            output = CommandTemplateExecutor(self._cli_service,
                                             configuration.COPY_TO_SCP).execute_command(filename=filename,
                                                                                        dst=dst,
                                                                                        port=port)
        else:
            raise Exception("Export configuration", "Protocol type <{}> is unsupportable".format(protocol))

        pattern = r"Sent \d+ bytes in \d+.\d+ seconds"
        status_match = re.search(pattern, output, re.IGNORECASE)

        if not status_match:
            self._logger.error("Export configuration failed: {err}".format(err=output))
            raise Exception("Export configuration", "Export configuration failed. See logs for details")

    def reload_device(self, timeout=500, action_map=None, error_map=None):
        """ Reload device

        :param timeout: session reconnect timeout
        :param action_map: actions will be taken during executing commands, i.e. handles yes/no prompts
        :param error_map: errors will be raised during executing commands, i.e. handles Invalid Commands errors
        """

        try:
            CommandTemplateExecutor(self._cli_service, configuration.RELOAD).execute_command(action_map=action_map,
                                                                                             error_map=error_map)
        except Exception as e:
            self._logger.info("Device rebooted, starting reconnect")
        self._cli_service.reconnect(timeout)

    def shutdown(self, action_map=None, error_map=None):
        """ Shutdown the system """

        try:
            CommandTemplateExecutor(self._cli_service, configuration.SHUTDOWN).execute_command(action_map=action_map,
                                                                                               error_map=error_map)
        except Exception as e:
            self._logger.info("Device turned off")


class FirmwareActions(object):
    def __init__(self, cli_service, logger):
        """
        Reboot actions
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

        CommandTemplateExecutor(self._cli_service, firmware.INSTALL_SOFTWARE).execute_command(
            software_file_name=software_file_name)
