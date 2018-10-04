#!/usr/bin/python
# -*- coding: utf-8 -*-

from cloudshell.cli.cli_service_impl import CliServiceImpl as CliService
from cloudshell.cli.command_template.command_template_executor import CommandTemplateExecutor
from cloudshell.firewall.paloalto.panos.command_templates import enable_disable_snmp


class EnableDisableSnmpV2Actions(object):
    SNMP_VERSION = "v2c"

    def __init__(self, cli_service, logger, community):
        """ Enable Disable Snmp actions """

        self._cli_service = cli_service
        self._logger = logger
        self.community = community

    def enable_snmp_service(self):
        """ Enable SNMP server """

        CommandTemplateExecutor(self._cli_service, enable_disable_snmp.ENABLE_SNMP_SERVICE).execute_command()

    def enable_snmp(self):
        """ Enable snmp on the device """

        CommandTemplateExecutor(self._cli_service,
                                enable_disable_snmp.CONFIGURE_V2C).execute_command(community=self.community)

    def disable_snmp(self):
        """ Disable snmp on the device """

        CommandTemplateExecutor(self._cli_service,
                                enable_disable_snmp.DELETE_SNMP_CONFIG).execute_command(snmp_version=self.SNMP_VERSION)


class EnableDisableSnmpV3Actions(object):
    SNMP_VERSION = "v3"
    VIEWS = "quali_views"
    VIEW = "quali_view"
    OID = 1

    def __init__(self, cli_service, logger, user, password, priv_key):
        """ Enable Disable Snmp actions
        :param CliService cli_service: config mode cli service
        :param logger:
        :param str user: user name
        :param str password:
        :param str priv_key:
        """

        self._cli_service = cli_service
        self._logger = logger
        self.user = user
        self.password = password
        self.priv_key = priv_key

    def enable_snmp_service(self):
        """ Enable SNMP server """

        CommandTemplateExecutor(self._cli_service, enable_disable_snmp.ENABLE_SNMP_SERVICE).execute_command()

    def enable_snmp(self):
        """  """

        CommandTemplateExecutor(self._cli_service,
                                enable_disable_snmp.CONFIGURE_V3_VIEW).execute_command(views=self.VIEWS,
                                                                                       view=self.VIEW,
                                                                                       oid=self.OID)
        CommandTemplateExecutor(self._cli_service,
                                enable_disable_snmp.CONFIGURE_V3).execute_command(v3_user=self.user,
                                                                                  v3_auth_pass=self.password,
                                                                                  v3_priv_pass=self.priv_key,
                                                                                  view=self.VIEW)

    def disable_snmp(self):
        """ Disable snmp on the device """

        CommandTemplateExecutor(self._cli_service,
                                enable_disable_snmp.DELETE_SNMP_CONFIG).execute_command(snmp_version=self.SNMP_VERSION)

        CommandTemplateExecutor(self._cli_service,
                                enable_disable_snmp.DELETE_V3_VIEW).execute_command(views=self.VIEWS, view=self.VIEW)
