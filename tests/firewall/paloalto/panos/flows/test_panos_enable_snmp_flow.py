#!/usr/bin/python
# -*- coding: utf-8 -*-

from unittest import TestCase

from cloudshell.snmp.snmp_parameters import (
    SNMPReadParameters,
    SNMPV3Parameters,
    SNMPWriteParameters,
)

from cloudshell.firewall.paloalto.panos.flows.panos_enable_snmp_flow import (
    PanOSEnableSnmpFlow,
)

try:
    from unittest.mock import MagicMock, patch
except ImportError:
    from mock import MagicMock, patch


class TestPanOSEnableSNMPFlow(TestCase):
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
        return PanOSEnableSnmpFlow(cli_handler=cli, logger=logger)

    @patch(
        "cloudshell.firewall.paloalto.panos.flows.panos_enable_snmp_flow"
        ".EnableDisableSnmpV3Actions"
    )
    @patch(
        "cloudshell.firewall.paloalto.panos.flows.panos_enable_snmp_flow"
        ".SystemConfigurationActions"
    )
    def test_enable_snmp_v3(self, system_actions_mock, enable_actions_mock):
        enable_snmp_service_mock = MagicMock()
        enable_snmp_mock = MagicMock()
        commit_changes_mock = MagicMock()
        enable_actions_mock.return_value.get_current_snmp_user.side_effect = [
            "",
            self.SNMP_USER,
        ]
        enable_actions_mock.return_value.enable_snmp_service = enable_snmp_service_mock
        enable_actions_mock.return_value.enable_snmp = enable_snmp_mock
        system_actions_mock.return_value.commit_changes = commit_changes_mock
        enable_actions_mock.return_value.get_current_snmp_config.return_value = ""

        enable_flow = self._get_handler()

        enable_flow.enable_flow(self.snmp_v3_parameters)

        enable_snmp_service_mock.assert_called_once()
        enable_snmp_mock.assert_called_once()
        commit_changes_mock.assert_called_once()

    @patch(
        "cloudshell.firewall.paloalto.panos.flows.panos_enable_snmp_flow"
        ".EnableDisableSnmpV2Actions"
    )
    @patch(
        "cloudshell.firewall.paloalto.panos.flows.panos_enable_snmp_flow"
        ".SystemConfigurationActions"
    )
    def test_enable_snmp_v2(self, system_actions_mock, enable_actions_mock):
        enable_flow = self._get_handler()
        enable_snmp_service_mock = MagicMock()
        enable_snmp_mock = MagicMock()
        commit_changes_mock = MagicMock()
        enable_actions_mock.return_value.get_current_snmp_config.side_effect = [
            "",
            "snmp-server community {}".format(
                self.snmp_v2_read_parameters.snmp_community
            ),
        ]
        enable_actions_mock.return_value.enable_snmp_service = enable_snmp_service_mock
        enable_actions_mock.return_value.enable_snmp = enable_snmp_mock
        system_actions_mock.return_value.commit_changes = commit_changes_mock

        enable_flow.enable_flow(self.snmp_v2_read_parameters)

        enable_snmp_service_mock.assert_called_once()
        enable_snmp_mock.assert_called_once()
        commit_changes_mock.assert_called_once()

    def test_validate_snmp_v3_params_validates_user_and_raise(self):
        enable_flow = PanOSEnableSnmpFlow(cli_handler=MagicMock(), logger=MagicMock())
        snmp_v3_parameters = SNMPV3Parameters(
            ip=self.IP,
            snmp_user="",
            snmp_password=self.SNMP_PASSWORD,
            snmp_private_key=self.SNMP_PRIVATE_KEY,
        )

        with self.assertRaisesRegexp(Exception, "SNMPv3 user is not defined"):
            enable_flow.enable_flow(snmp_v3_parameters)

    def test_validate_snmp_v3_params_validates_password_and_raise(self):
        enable_flow = PanOSEnableSnmpFlow(cli_handler=MagicMock(), logger=MagicMock())
        snmp_v3_parameters = SNMPV3Parameters(
            ip=self.IP,
            snmp_user=self.SNMP_USER,
            snmp_password="",
            snmp_private_key=self.SNMP_PRIVATE_KEY,
            auth_protocol=SNMPV3Parameters.AUTH_MD5,
        )

        with self.assertRaisesRegexp(Exception, "SNMPv3 Password has to be specified"):
            enable_flow.enable_flow(snmp_v3_parameters)

    def test_validate_snmp_v3_params_validates_private_key_and_raise(self):
        enable_flow = PanOSEnableSnmpFlow(cli_handler=MagicMock(), logger=MagicMock())
        snmp_v3_parameters = SNMPV3Parameters(
            ip=self.IP,
            snmp_user=self.SNMP_USER,
            snmp_password=self.SNMP_PASSWORD,
            snmp_private_key="",
            auth_protocol=SNMPV3Parameters.AUTH_MD5,
            private_key_protocol=SNMPV3Parameters.PRIV_DES,
        )

        with self.assertRaisesRegexp(
            Exception, "SNMPv3 Private key has to be specified"
        ):
            enable_flow.enable_flow(snmp_v3_parameters)
