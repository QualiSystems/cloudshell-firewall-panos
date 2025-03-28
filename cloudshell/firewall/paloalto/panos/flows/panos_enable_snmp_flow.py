#!/usr/bin/python

from cloudshell.firewall.paloalto.panos.command_actions.enable_disable_snmp_actions import (
    EnableDisableSnmpV2Actions,
    EnableDisableSnmpV3Actions,
)
from cloudshell.firewall.paloalto.panos.command_actions.system_actions import (
    SystemConfigurationActions,
)


class PanOSEnableSnmpFlow:
    def __init__(self, cli_handler, logger):
        """Enable snmp flow.

        :param cli_handler:
        :param logger:
        :return:
        """
        self._logger = logger
        self._cli_handler = cli_handler

    def enable_flow(self, snmp_parameters):
        if "3" not in snmp_parameters.version and not snmp_parameters.snmp_community:
            message = "SNMP community cannot be empty"
            self._logger.error(message)
            raise Exception(message)

        with self._cli_handler.get_cli_service(
            self._cli_handler.config_mode
        ) as config_session:
            if "3" in snmp_parameters.version:
                self._logger.info("Start creating SNMPv3 configuration")
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

                snmp_actions.enable_snmp_service()
                snmp_actions.enable_snmp()
                system_actions.commit_changes()

                self._logger.info(f"SNMP User {snmp_parameters.snmp_user} created")
            else:
                community = snmp_parameters.snmp_community

                self._logger.info(f"Start creating SNMP community {community}")
                snmp_actions = EnableDisableSnmpV2Actions(
                    config_session, self._logger, community
                )
                system_actions = SystemConfigurationActions(
                    config_session, self._logger
                )
                snmp_actions.enable_snmp_service()
                snmp_actions.enable_snmp()
                system_actions.commit_changes()

                self._logger.info(f"SNMP community {community} created")
