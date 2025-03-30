import re
from functools import lru_cache
from logging import Logger

from cloudshell.snmp.autoload.helper.types.resource_model import ResourceModelProto
from cloudshell.snmp.autoload.services.port_table import PortsTable
from cloudshell.snmp.autoload.snmp.entities.snmp_if_entity import SnmpIfEntity
from cloudshell.snmp.autoload.snmp.tables.snmp_ports_table import SnmpPortsTable


class PANOSSnmpIfEntity(SnmpIfEntity):
    @property
    @lru_cache
    def port_name(self):
        result = self.if_name or self.if_descr_name
        result = re.sub(r"node\d+:", "", result.replace("/", "-"))
        return result.replace(":", "_")


class PANOSIfTable(PortsTable):
    def __init__(
        self,
        resource_model: ResourceModelProto,
        ports_snmp_table: SnmpPortsTable,
        logger: Logger,
    ):
        super().__init__(resource_model, ports_snmp_table, logger)
        self._if_entity = PANOSSnmpIfEntity
