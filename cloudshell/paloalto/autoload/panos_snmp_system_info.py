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

    def fill_attributes(self, resource):
        """Fill attributes."""
        super().fill_attributes(resource)
        if resource.vendor.endswith("root"):
            resource.vendor = resource.vendor.lower().replace(
                "panroot", "Palo Alto Networks."
            )
        if resource.model and not resource.model_name:
            resource.model_name = resource.model
        if resource.model_name and "pa" in resource.model_name.lower():
            model_name = re.sub("[Pp][Aa][-_]", "PA-", resource.model_name)
            resource.model = model_name
            resource.model_name = model_name
