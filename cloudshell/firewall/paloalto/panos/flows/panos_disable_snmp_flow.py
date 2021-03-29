#!/usr/bin/python
# -*- coding: utf-8 -*-

from cloudshell.firewall.paloalto.panos.command_actions.enable_disable_snmp_actions import (  # noqa: E501
    EnableDisableSnmpV2Actions,
    EnableDisableSnmpV3Actions,
)
from cloudshell.firewall.paloalto.panos.command_actions.system_actions import (
    SystemConfigurationActions,
)


class PanOSDisableSnmpFlow(object):
    def __init__(self, cli_handler, logger):
        """Enable snmp flow."""
        self._cli_handler = cli_handler
        self._logger = logger

    def disable_flow(self, snmp_parameters):
        with self._cli_handler.get_cli_service(
            self._cli_handler.config_mode
        ) as config_session:
            if "3" in snmp_parameters.version:
                self._logger.info("Start removing SNMP v3 configuration")
                snmp_actions = EnableDisableSnmpV3Actions(
                    config_session,
                    self._logger,
                    snmp_parameters.snmp_user,
                    snmp_parameters.snmp_password,
                    snmp_parameters.snmp_private_key,
                )
                system_actions = SystemConfigurationActions(
                    config_session, self._logger
                )

                snmp_actions.disable_snmp()
                system_actions.commit_changes()

                self._logger.info("SNMP v3 configuration removed")
            else:
                community = snmp_parameters.snmp_community

                self._logger.info("Start removing SNMP community {}".format(community))
                snmp_actions = EnableDisableSnmpV2Actions(
                    config_session, self._logger, community
                )
                system_actions = SystemConfigurationActions(
                    config_session, self._logger
                )
                snmp_actions.disable_snmp()
                system_actions.commit_changes()

                self._logger.info("SNMP community {} removed".format(community))
