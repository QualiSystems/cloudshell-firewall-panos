from __future__ import annotations

import re

from cloudshell.snmp.autoload.services.system_info_table import SnmpSystemInfo
from cloudshell.snmp.core.domain.snmp_oid import SnmpMibObject


class PanOSSNMPSystemInfo(SnmpSystemInfo):
    DEVICE_MODEL_PATTERN = re.compile(r"::pan(?P<model>\S+$)")

    def _get_device_os_version(self) -> str:
        """Get device OS Version form snmp SNMPv2 mib."""
        try:
            result = self._get_val(
                self._snmp_handler.get_property(
                    SnmpMibObject("PAN-COMMON-MIB", "panSysSwVersion", "0")
                )
            )
        except Exception:
            result = ""

        return result
