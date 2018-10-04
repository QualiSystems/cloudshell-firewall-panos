#!/usr/bin/python
# -*- coding: utf-8 -*-

from cloudshell.devices.flows.cli_action_flows import EnableSnmpFlow
from cloudshell.snmp.snmp_parameters import SNMPV3Parameters, SNMPV2WriteParameters,\
    SNMPV2ReadParameters

from cloudshell.firewall.paloalto.panos.command_actions.system_actions import SystemConfigurationActions
from cloudshell.firewall.paloalto.panos.command_actions.enable_disable_snmp_actions import \
    EnableDisableSnmpV2Actions, EnableDisableSnmpV3Actions


class PanOSEnableSnmpFlow(EnableSnmpFlow):

    def execute_flow(self, snmp_parameters):
        if isinstance(snmp_parameters, SNMPV3Parameters):
            Flow = PanOSEnableSnmpV3
        else:
            Flow = PanOSEnableSnmpV2

        Flow(self._cli_handler, self._logger, snmp_parameters).execute()


class PanOSEnableSnmpV2(object):
    def __init__(self, cli_handler, logger, snmp_parameters):
        """ Enable SNMP v2c """

        self._cli_handler = cli_handler
        self._logger = logger
        self.snmp_parameters = snmp_parameters

    def execute(self):
        community = self.snmp_parameters.snmp_community
        if isinstance(self.snmp_parameters, SNMPV2WriteParameters):
            raise Exception("Devices doesn't support write communities")

        with self._cli_handler.get_cli_service(self._cli_handler.config_mode) as conf_session:
            self._logger.info("Start creating SNMP community {}".format(community))

            snmp_actions = EnableDisableSnmpV2Actions(conf_session, self._logger, community)
            system_actions = SystemConfigurationActions(conf_session, self._logger)
            snmp_actions.enable_snmp_service()
            snmp_actions.enable_snmp()
            system_actions.commit_changes()

        self._logger.info("SNMP community {} created".format(community))


class PanOSEnableSnmpV3(object):
    def __init__(self, cli_handler, logger, snmp_param):
        """ Enable SNMP v3 """

        self._cli_handler = cli_handler
        self._logger = logger
        self.snmp_param = snmp_param

    def execute(self):
        """  """

        with self._cli_handler.get_cli_service(self._cli_handler.config_mode) as conf_session:
            self._logger.info("Start creating SNMPv3 configuration")
            snmp_actions = EnableDisableSnmpV3Actions(conf_session,
                                                      self._logger,
                                                      self.snmp_param.snmp_user,
                                                      self.snmp_param.snmp_password,
                                                      self.snmp_param.snmp_private_key)
            system_actions = SystemConfigurationActions(conf_session, self._logger)

            snmp_actions.enable_snmp_service()
            snmp_actions.enable_snmp()
            system_actions.commit_changes()

            self._logger.info("SNMP User {} created".format(self.snmp_param.snmp_user))
