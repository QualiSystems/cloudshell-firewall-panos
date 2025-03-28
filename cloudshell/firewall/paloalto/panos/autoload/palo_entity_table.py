from cloudshell.snmp.autoload.constants.entity_constants import ENTITY_OS_VERSION
from cloudshell.snmp.autoload.core.snmp_autoload_error import GeneralAutoloadError
from cloudshell.snmp.autoload.domain.entity.snmp_entity_base import BaseEntity
from cloudshell.snmp.autoload.domain.entity.snmp_entity_element import Element
from cloudshell.snmp.autoload.domain.entity.snmp_entity_struct import Module
from cloudshell.snmp.autoload.helper.entity_quali_mib_table import EntityQualiMibTable
from cloudshell.snmp.autoload.snmp_entity_table import SnmpEntityTable


class ModuleEntity(BaseEntity):
    @property
    def os_version(self):
        if self._name is None:
            self._name = self.snmp_service.get_property(
                ENTITY_OS_VERSION.get_snmp_mib_oid(self.index)
            )
        return self._name.safe_value or ""


class PaloEntityTable(SnmpEntityTable):
    @property
    def modules_dict(self):
        return self._module_tree

    def get_parent_chassis(self, element: Element):
        parent = self._raw_physical_indexes.get(element.entity.parent_id)
        while "chassis" not in parent.entity_class.lower():
            parent = self._raw_physical_indexes.get(parent.parent_id)
        else:
            return parent.index

    def _get_entity_table(self):
        """Read Entity-MIB and filter out device's structure and all it's elements.

        Like ports, modules, chassis, etc.
        :rtype: QualiMibTable
        :return: structured and filtered EntityPhysical table.
        """
        self._raw_physical_indexes = EntityQualiMibTable(self._snmp)

        index_list = self._raw_physical_indexes.raw_entity_indexes
        try:
            index_list.sort(key=lambda k: int(k.index), reverse=True)
        except ValueError:
            self._logger.error("Failed to load snmp entity table!", exc_info=1)
            raise GeneralAutoloadError("Failed to load snmp entity table.")
        for entity_index in index_list:
            entity = BaseEntity(self._snmp, entity_index)
            if "module" in entity.entity_class:
                if self.module_exclude_pattern and self.module_exclude_pattern.search(
                    entity.vendor_type
                ):
                    continue
                module_entity = Module(entity)
                element = Element(module_entity)
                parent = self._raw_physical_indexes.get(entity.parent_id)
                if "container" in parent.entity_class.lower():
                    element.id = parent.position_id

                self._module_tree[element.id] = element

            elif "powersupply" in entity.entity_class.lower():
                self._load_power_port(self.ENTITY_POWER_PORT(entity))
            elif "chassis" in entity.entity_class.lower():
                if entity.index not in self._chassis_dict:
                    chassis = Element(self.ENTITY_CHASSIS(entity))
                    self._chassis_dict[entity.index] = chassis
