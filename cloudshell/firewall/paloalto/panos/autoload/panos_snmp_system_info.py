#!/usr/bin/python
# -*- coding: utf-8 -*-

import re

from cloudshell.snmp.autoload.snmp_system_info import SnmpSystemInfo


class PanOSSNMPSystemInfo(SnmpSystemInfo):
    DEVICE_MODEL_PATTERN = re.compile(r"::pan(?P<model>\S+$)")

    def _get_device_os_version(self):
        """Get device OS Version form snmp SNMPv2 mib.

        :return: device model
        :rtype: str
        """
        try:
            result = self._snmp_handler.get_property(
                "PAN-COMMON-MIB", "panSysSwVersion", "0"
            ).safe_value
        except Exception:
            result = ""

        return result
