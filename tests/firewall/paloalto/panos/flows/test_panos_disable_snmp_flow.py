#!/usr/bin/python
# -*- coding: utf-8 -*-

from unittest import TestCase

from cloudshell.snmp.snmp_parameters import (
    SNMPReadParameters,
    SNMPV3Parameters,
    SNMPWriteParameters,
)

from cloudshell.firewall.paloalto.panos.flows.panos_disable_snmp_flow import (
    PanOSDisableSnmpFlow,
)

try:
    from unittest.mock import MagicMock, patch
except ImportError:
    from mock import MagicMock, patch


class TestPanOSDisableSNMPFlow(TestCase):
    IP = "localhost"
    SNMP_WRITE_COMMUNITY = "private"
    SNMP_READ_COMMUNITY = "public"
    SNMP_USER = "admin"
    SNMP_PASSWORD = "P@ssw0rD"
    SNMP_PRIVATE_KEY = "PrivKey"

    def _get_handler(self):
        self.snmp_v2_write_parameters = SNMPWriteParameters(
            ip=self.IP, snmp_community=self.SNMP_WRITE_COMMUNITY
        )
        self.snmp_v2_read_parameters = SNMPReadParameters(
            ip=self.IP, snmp_community=self.SNMP_READ_COMMUNITY
        )
        self.snmp_v3_parameters = SNMPV3Parameters(
            ip=self.IP,
            snmp_user=self.SNMP_USER,
            snmp_password=self.SNMP_PASSWORD,
            snmp_private_key=self.SNMP_PRIVATE_KEY,
        )
        cli = MagicMock()
        logger = MagicMock()
        return PanOSDisableSnmpFlow(cli_handler=cli, logger=logger)

    @patch(
        "cloudshell.firewall.paloalto.panos.flows.panos_disable_snmp_flow"
        ".EnableDisableSnmpV3Actions"
    )
    @patch(
        "cloudshell.firewall.paloalto.panos.flows.panos_disable_snmp_flow"
        ".SystemConfigurationActions"
    )
    def test_disable_snmp_v3(self, system_actions_mock, disable_actions_mock):
        disable_snmp_mock = MagicMock()
        commit_changes_mock = MagicMock()
        disable_actions_mock.return_value.get_current_snmp_user.side_effect = [
            "",
            self.SNMP_USER,
        ]
        disable_actions_mock.return_value.disable_snmp = disable_snmp_mock
        system_actions_mock.return_value.commit_changes = commit_changes_mock
        disable_actions_mock.return_value.get_current_snmp_config.return_value = ""

        disable_flow = self._get_handler()

        disable_flow.disable_flow(self.snmp_v3_parameters)

        disable_snmp_mock.assert_called_once()
        commit_changes_mock.assert_called_once()

    @patch(
        "cloudshell.firewall.paloalto.panos.flows.panos_disable_snmp_flow"
        ".EnableDisableSnmpV2Actions"
    )
    @patch(
        "cloudshell.firewall.paloalto.panos.flows.panos_disable_snmp_flow"
        ".SystemConfigurationActions"
    )
    def test_disable_snmp_v2(self, system_actions_mock, disable_actions_mock):
        disable_snmp_service_mock = MagicMock()
        disable_snmp_mock = MagicMock()
        commit_changes_mock = MagicMock()

        disable_flow = self._get_handler()

        disable_actions_mock.return_value.disable_snmp_service = (
            disable_snmp_service_mock
        )
        disable_actions_mock.return_value.disable_snmp = disable_snmp_mock
        system_actions_mock.return_value.commit_changes = commit_changes_mock

        disable_flow.disable_flow(self.snmp_v2_read_parameters)
        disable_actions_mock.return_value.disable_snmp.assert_called_once()
        commit_changes_mock.assert_called_once()
