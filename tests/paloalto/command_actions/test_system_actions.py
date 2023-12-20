from __future__ import annotations

from unittest import TestCase
from unittest.mock import Mock, patch

from cloudshell.paloalto.command_actions.system_actions import SystemActions


class TestUtils(TestCase):
    def setUp(self):
        self._cli_service = Mock()
        self._logger = Mock()
        self._instance = SystemActions(self._cli_service)

    def test_init(self):
        self.assertIs(self._instance._cli_service, self._cli_service)

    @patch("cloudshell.paloalto.command_actions.system_actions.configuration")
    @patch("cloudshell.paloalto.command_actions.system_actions.CommandTemplateExecutor")
    def test_shutdown(self, command_template_executor, configuration_template):
        output = Mock()
        execute_command = Mock()
        command_template_executor.return_value = execute_command
        execute_command.execute_command.return_value = output
        self.assertIs(self._instance.shutdown(), output)
        command_template_executor.assert_called_once_with(
            self._cli_service, configuration_template.SHUTDOWN
        )
        execute_command.execute_command.assert_called_once_with(
            action_map=None, error_map=None
        )
