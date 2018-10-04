#!/usr/bin/python
# -*- coding: utf-8 -*-

import os
import re

import ipaddress
from cloudshell.devices.autoload.autoload_builder import AutoloadDetailsBuilder, AutoLoadDetails
from cloudshell.devices.standards.firewall.autoload_structure import GenericResource, \
    GenericChassis, GenericPort, GenericPortChannel, GenericPowerPort


class PanOSSNMPAutoload(object):
    VENDOR = "Palo Alto"

    def __init__(self, snmp_service, shell_name, shell_type, resource_name, logger):
        """Basic init with injected snmp handler and logger"""

        self.snmp_service = snmp_service
        self.shell_name = shell_name
        self.shell_type = shell_type
        self.resource_name = resource_name
        self.logger = logger

        self.chassis = None
        self.resource = GenericResource(shell_name, resource_name, resource_name, shell_type)

    def discover(self, supported_os):
        """General entry point for autoload,
            read device structure and attributes: chassis, ports, port-channels and power supplies
        :return: AutoLoadDetails object
        :rtype: AutoLoadDetails
        """

        if not self._is_valid_device_os(supported_os):
            raise Exception("Unsupported device OS")

        self.logger.info('*' * 70)
        self.logger.info('Start SNMP discovery process .....')

        self._load_mibs()
        self.snmp_service.load_mib(["PAN-COMMON-MIB", "PAN-GLOBAL-REG",
                                    "PAN-GLOBAL-TC", "PAN-PRODUCTS-MIB", "PAN-ENTITY-EXT-MIB"])
        self._get_device_details()

        self._load_snmp_tables()
        self._add_chassis()
        self._add_ports()
        self._add_power_ports()
        self._add_port_channels()

        autoload_details = AutoloadDetailsBuilder(self.resource).autoload_details()
        self._log_autoload_details(autoload_details)
        return autoload_details

    def _load_mibs(self):
        """Loads PaloAlto specific mibs inside snmp handler"""

        path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'mibs'))
        self.snmp_service.update_mib_sources(path)

    def _load_snmp_tables(self):
        """Load all PaloAlto required snmp tables"""

        self.logger.info('Start loading MIB tables:')

        self.entity_table = self.snmp_service.get_table('ENTITY-MIB', 'entPhysicalClass')
        self.if_table = self.snmp_service.get_table('IF-MIB', 'ifType')
        self.ip_v4_table = self.snmp_service.get_table('IP-MIB', 'ipAddrTable')
        self.ip_v6_table = self.snmp_service.get_table('IPV6-MIB', 'ipv6AddrPfxLength')
        self.port_channel_ports_assoc = self.snmp_service.get_table('IEEE8023-LAG-MIB', 'dot3adAggPortAttachedAggID')
        self.power_ports = self.snmp_service.get_table('PAN-ENTITY-EXT-MIB', 'panEntityPowerSupplyTable')
        self.duplex_table = self.snmp_service.get_table('EtherLike-MIB', 'dot3StatsIndex')
        self.lldp_remote_table = self.snmp_service.get_table('LLDP-MIB', 'lldpRemSysName')
        self.lldp_local_table = {v['lldpLocPortDesc']: k for k, v in self.snmp_service.get_table(
            'LLDP-MIB', 'lldpLocPortDesc').iteritems()}

        self.logger.info('MIB Tables loaded successfully')

    def _get_unique_id(self, obj_type, id_):
        return '{}.{}.{}'.format(self.resource_name, obj_type, id_)

    def _add_chassis(self):
        self.logger.info('Building Chassis')

        for index, attrs in self.entity_table.items():
            if attrs['entPhysicalClass'].lower() == "'chassis'":
                unique_id = self._get_unique_id("Chassis", index)
                chassis_obj = GenericChassis(self.shell_name, 'Chassis {}'.format(index), unique_id)
                chassis_obj.model = self.snmp_service.get_property('ENTITY-MIB', 'entPhysicalModelName', index)
                chassis_obj.serial_number = self.snmp_service.get_property('ENTITY-MIB', 'entPhysicalSerialNum', index)
                self.resource.add_sub_resource(index, chassis_obj)
                self.chassis = chassis_obj

        self.logger.info('Building Chassis completed')

    def _add_ports(self):
        self.logger.info('Loading Ports')

        for index, attrs in self.if_table.items():
            if attrs['ifType'] == "'ethernetCsmacd'":
                if_descr = self.snmp_service.get_property("IF-MIB", "ifDescr", int(index))
                if re.search(r"ethernet(?P<ch_index>\d+)/(?P<if_index>\d+)", if_descr, re.IGNORECASE):
                    unique_id = self._get_unique_id('port', index)
                    port_obj = GenericPort(self.shell_name, if_descr.replace("/", "-"), unique_id)
                    port_obj.port_description = self.snmp_service.get_property("IF-MIB", "ifAlias", int(index))
                    port_obj.l2_protocol_type = attrs['ifType'].replace("'", "")
                    port_obj.mac_address = self.snmp_service.get_property("IF-MIB", "ifPhysAddress", int(index))
                    port_obj.mtu = self.snmp_service.get_property("IF-MIB", "ifMtu", int(index))
                    port_obj.bandwidth = self.snmp_service.get_property("IF-MIB", "ifHighSpeed", int(index))
                    port_obj.ipv4_address = self._get_ipv4_interface_address(index)
                    port_obj.ipv6_address = self._get_ipv6_interface_address(index)
                    port_obj.duplex = self._get_port_duplex(index)
                    port_obj.auto_negotiation = self._get_port_auto_negotiation(index)
                    port_obj.adjacent = self._get_adjacent(index)

                    self.chassis.add_sub_resource(index, port_obj)
                    self.logger.info('Added {} Port'.format(if_descr))

        self.logger.info('Building Ports completed')

    def _get_port_duplex(self, port_index):
        for key, value in self.duplex_table.iteritems():
            if 'dot3StatsIndex' in value.keys() and value['dot3StatsIndex'] == str(port_index):
                interface_duplex = self.snmp_service.get_property('EtherLike-MIB', 'dot3StatsDuplexStatus', key)
                if 'fullDuplex' in interface_duplex:
                    return 'Full'

    def _get_port_auto_negotiation(self, port_index):
        try:
            auto_negotiation = self.snmp_service.get(('MAU-MIB', 'ifMauAutoNegAdminStatus', port_index, 1)).values()[0]
            if 'enabled' in auto_negotiation.lower():
                return 'True'
        except Exception as e:
            self.logger.error('Failed to load auto negotiation property for interface {0}'.format(e.message))
            return 'False'

    def _add_power_ports(self):
        self.logger.info('Building PowerPorts')
        for index, attrs in self.power_ports.items():
            unique_id = self._get_unique_id('power-port', index)
            power_port = GenericPowerPort(self.shell_name, 'PP{}'.format(index), unique_id)
            power_port.model = ''
            power_port.port_description = ''
            power_port.version = ''
            power_port.serial_number = ''

            self.chassis.add_sub_resource(index, power_port)
            self.logger.info('Added PP{} Power Port'.format(index))
        self.logger.info('Building Power Ports completed')

    def _add_port_channels(self):

        if not self.if_table:
            return

        port_channel_dic = {index: port for index, port in self.if_table.iteritems() if
                            "lag" in port["ifType"]}
        self.logger.info("Building Port Channels")
        for index, value in port_channel_dic.iteritems():
            interface_model = self.snmp_service.get_property("IF-MIB", "ifDescr", int(index))
            match_object = re.search(r"\d+$", interface_model)
            if match_object:
                interface_id = "{0}".format(match_object.group(0))

                port_channel = GenericPortChannel(shell_name=self.shell_name,
                                                  name=interface_model,
                                                  unique_id=self._get_unique_id("port_channel", interface_id))

                port_channel.port_description = self.snmp_service.get_property("IF-MIB", "ifAlias", index)
                port_channel.ipv4_address = self._get_ipv4_interface_address(index)
                port_channel.ipv6_address = self._get_ipv6_interface_address(index)
                port_channel.associated_ports = self._get_associated_ports(index)

                self.chassis.add_sub_resource(index, port_channel)
                self.logger.info("Added " + interface_model + " Port Channel")

            else:
                self.logger.error("Adding of {0} failed. Name is invalid".format(interface_model))

        self.logger.info("Building Port Channels completed")

    def _get_associated_ports(self, index):
        """Get all ports associated with provided port channel
        :param item_id:
        :return:
        """

        result = ''
        for key, value in self.port_channel_ports_assoc.iteritems():
            if str(index) in value['dot3adAggPortAttachedAggID'] and key in self.if_table:
                interface_model = self.snmp_service.get_property("IF-MIB", "ifDescr", int(index))
                if interface_model:
                    result += interface_model.replace('/', '-').replace(' ', '') + '; '
        return result.strip(' \t\n\r')

    def _log_autoload_details(self, autoload_details):
        """Logging autoload details
        :param autoload_details:
        """

        self.logger.debug('-------------------- <RESOURCES> ----------------------')
        for resource in autoload_details.resources:
            self.logger.debug(
                '{0:15}, {1:20}, {2}'.format(resource.relative_address, resource.name,
                                             resource.unique_identifier))
        self.logger.debug('-------------------- </RESOURCES> ----------------------')

        self.logger.debug('-------------------- <ATTRIBUTES> ---------------------')
        for attribute in autoload_details.attributes:
            self.logger.debug('-- {0:15}, {1:60}, {2}'.format(attribute.relative_address,
                                                              attribute.attribute_name,
                                                              attribute.attribute_value))
        self.logger.debug('-------------------- </ATTRIBUTES> ---------------------')

    def _is_valid_device_os(self, supported_os):
        """Validate device OS using snmp
        :rtype: bool
        :return: True or False
        """

        system_description = self.snmp_service.get_property('SNMPv2-MIB', 'sysDescr', '0')
        self.logger.debug('Detected system description: \'{0}\''.format(system_description))

        result = re.search(
            r'({0})\s'.format('|'.join(supported_os)),
            system_description,
            flags=re.DOTALL | re.IGNORECASE)

        if result:
            return True
        else:
            error_message = 'Incompatible driver! Please use this driver for "{0}" ' \
                            'operation system(s)'.format(str(tuple(supported_os)))
            self.logger.error(error_message)
            return False

    def _get_ipv4_interface_address(self, port_id):
        """Get IPv4 address details for provided port"""

        for ip, attrs in self.ip_v4_table.iteritems():
            if str(attrs.get('ipAdEntIfIndex')) == str(port_id):
                return ip

    def _get_ipv6_interface_address(self, port_id):
        """Get IPv6 address details for provided port"""

        for key, _ in self.ip_v6_table.iteritems():
            ints = map(int, key.split('.'))
            id_, addr = ints[0], ints[2:]
            if str(id_) == str(port_id):
                addr = ((u'{:02x}{:02x}:' * 8)[:-1]).format(*addr)
                return str(ipaddress.IPv6Address(addr))

    def _get_device_details(self):
        """ Get root element attributes """

        self.logger.info('Building Root')

        self.resource.contact_name = self.snmp_service.get_property('SNMPv2-MIB', 'sysContact', '0')
        self.resource.system_name = self.snmp_service.get_property('SNMPv2-MIB', 'sysName', '0')
        self.resource.location = self.snmp_service.get_property('SNMPv2-MIB', 'sysLocation', '0')
        self.resource.vendor = self.VENDOR
        self.resource.os_version = self._get_device_os_version()
        self.resource.model = self._get_device_model()

    def _get_device_os_version(self):
        """ Determine device OS version using SNMP """

        try:
            result = self.snmp_service.get_property('PAN-COMMON-MIB', 'panSysSwVersion', '0')
        except Exception:
            result = ''

        return result

    def _get_device_model(self):
        """Get device model from snmp SNMPv2 mib
        :return: device model
        :rtype: str
        """

        output = self.snmp_service.get_property('SNMPv2-MIB', 'sysObjectID', '0')
        match = re.search(r'::pan(?P<model>\S+$)', output)

        try:
            result = match.groupdict()['model'].upper()
        except (AttributeError, KeyError):
            result = ''

        return result

    def _get_adjacent(self, interface_name):
        """Get connected device interface and device name to the specified port
            using lldp protocol
        :param interface_name:
        :return: device's name and port connected to port id
        :rtype: str
        """

        result_template = '{remote_host} through {remote_port}'
        result = ''
        if self.lldp_local_table:
            key = self.lldp_local_table.get(interface_name, None)
            if key:
                for port_id, rem_table in self.lldp_remote_table.iteritems():
                    if '.{0}.'.format(key) in port_id:
                        remoute_sys_name = rem_table.get('lldpRemSysName', '')
                        remoute_port_name = self.snmp_service.get_property(
                            'LLDP-MIB', 'lldpRemPortDesc', port_id)
                        if remoute_port_name and remoute_sys_name:
                            result = result_template.format(remote_host=remoute_sys_name,
                                                            remote_port=remoute_port_name)
                            break
        return result
