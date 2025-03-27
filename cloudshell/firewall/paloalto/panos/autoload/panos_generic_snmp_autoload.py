#!/usr/bin/python
# -*- coding: utf-8 -*-

import re

from cloudshell.snmp.autoload.generic_snmp_autoload import (
    GenericSNMPAutoload,
    SnmpEntityTable,
    GeneralAutoloadError,
    log_autoload_details
)

from cloudshell.firewall.paloalto.panos.autoload.palo_entity_table import \
    PaloEntityTable
from cloudshell.firewall.paloalto.panos.autoload.panos_snmp_system_info import PanOSSNMPSystemInfo


class PanOSGenericSNMPAutoload(GenericSNMPAutoload):
    def __init__(self, snmp_handler, logger):
        super(PanOSGenericSNMPAutoload, self).__init__(snmp_handler, logger)
        self._if_ports_in_entity = False
        self._chassis = dict()
        self._modules = dict()

    @property
    def system_info_service(self):
        if not self._system_info:
            self._system_info = PanOSSNMPSystemInfo(self.snmp_handler, self.logger)
        return self._system_info

    @property
    def entity_table_service(self):
        if not self._entity_table:
            self._entity_table = PaloEntityTable(
                snmp_handler=self.snmp_handler,
                logger=self.logger,
                if_table=self.if_table_service,
            )
        return self._entity_table

    def discover(
        self, supported_os, resource_model, validate_module_id_by_port_name=False
    ):
        """General entry point for autoload.

        Read device structure and attributes: chassis, modules, submodules, ports,
        port-channels and power supplies
        :type resource_model: cloudshell.shell.standards.autoload_generic_models.GenericResourceModel  # noqa: E501
        :param str supported_os:
        :param bool validate_module_id_by_port_name:
        :return: AutoLoadDetails object
        """
        self.entity_table_service.validate_module_id_by_port_name = (
            validate_module_id_by_port_name
        )
        if not resource_model:
            return
        self._resource_model = resource_model
        if not self.system_info_service.is_valid_device_os(supported_os):
            raise GeneralAutoloadError("Unsupported device OS")

        self.logger.info("*" * 70)
        self.logger.info("Start SNMP discovery process .....")
        self.system_info_service.fill_attributes(resource_model)
        if resource_model.vendor.endswith("root"):
            resource_model.vendor = resource_model.vendor.lower().replace(
                "panroot",
                "Palo Alto Networks."
            )
        if resource_model.model and not resource_model.model_name:
            resource_model.model_name = resource_model.model
        if resource_model.model_name and "pa-" in resource_model.model_name.lower():
            model_name = re.sub("[Pp][Aa]-", "PA-", resource_model.model_name)
            resource_model.model = model_name
            resource_model.model_name = model_name
        self.logger.info("*" * 70)

        entity_chassis_tree_dict = self.entity_table_service.chassis_structure_dict

        if entity_chassis_tree_dict:
            self._build_structure(entity_chassis_tree_dict.values(), resource_model)
            self._get_port_channels(resource_model)

        if not self._if_ports_in_entity:
            self._add_ports_from_iftable()

        autoload_details = resource_model.build()

        log_autoload_details(self.logger, autoload_details)
        return autoload_details

    def _build_structure(self, child_list, parent):
        for element in child_list:
            if isinstance(element.entity, SnmpEntityTable.ENTITY_CHASSIS):
                chassis = self._get_chassis_attributes(element, parent)
                self._chassis.update({str(element.entity.index): chassis})
                self._build_structure(element.child_list, chassis)

            elif isinstance(element.entity, SnmpEntityTable.ENTITY_MODULE):
                module = self._get_module_attributes(element, parent)
                if module:
                    self._modules[element.id] = module
                    self._build_structure(element.child_list, module)

            elif isinstance(element.entity, SnmpEntityTable.ENTITY_POWER_PORT):
                self._get_power_ports(element, parent)

            elif isinstance(element.entity, SnmpEntityTable.ENTITY_PORT):
                self._if_ports_in_entity = self._if_ports_in_entity or True
                self._get_ports_attributes(element, parent)

    def _add_ports_from_iftable(self):
        """Get resource details and attributes for every port base on data from IFMIB Table"""
        self.logger.info("Loading Ports ...")

        for if_index, interface in self.if_table_service.if_ports.items():
            if self.if_table_service.PORT_VALID_TYPE.search(interface.if_type):
                self.logger.debug("Trying to load port {}:".format(interface.port_name))
                match = re.search(
                    r"ethernet(?P<ch_index>\d+)/(?P<if_index>\d+)",
                    interface.if_descr_name,
                    re.IGNORECASE
                )
                if match:
                    parent_id = match.groupdict().get("ch_index")
                    if not self.entity_table_service.modules_dict:
                        parent_element = self._chassis.get(
                            parent_id
                        )
                    else:
                        parent_element = self._modules.get(
                            parent_id
                        )
                        if not parent_element:
                            module = self.entity_table_service.modules_dict.get(
                                parent_id
                            )
                            if module:
                                if len(self._chassis) == 1:
                                    chassis = list(self._chassis.values())[0]
                                else:
                                    chassis_index = (
                                        self.entity_table_service.get_parent_chassis(
                                            module
                                        )
                                    )
                                    chassis = self._chassis.get(chassis_index)

                                parent_element = self._get_module_attributes(
                                    module,
                                    chassis
                                )
                                self._modules[parent_id] = parent_element
                    port_name = re.sub(
                        "node\d+:",
                        "",
                        interface.port_name.replace("/", "-")
                        )
                    port_object = self._resource_model.entities.Port(
                        index=if_index,
                        name=port_name,
                    )

                    port_object.mac_address = interface.if_mac
                    port_object.l2_protocol_type = interface.if_type
                    port_object.port_description = interface.if_port_description
                    port_object.bandwidth = interface.if_speed
                    port_object.mtu = interface.if_mtu
                    port_object.duplex = interface.duplex
                    port_object.adjacent = interface.adjacent
                    port_object.auto_negotiation = interface.auto_negotiation
                    port_object.ipv4_address = interface.ipv4_address
                    port_object.ipv6_address = interface.ipv6_address

                    parent_element.connect_port(port_object)
                    self.logger.info("Added {0} Port".format(interface.port_name))

        self.logger.info("Building Ports completed")
