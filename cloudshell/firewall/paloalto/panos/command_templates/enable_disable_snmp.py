#!/usr/bin/python
# -*- coding: utf-8 -*-

from cloudshell.cli.command_template.command_template import CommandTemplate

SHOW_SYSTEM_SERVICES = CommandTemplate("show system services")
SHOW_SNMP_SETTINGS = CommandTemplate("show deviceconfig system snmp-setting access-setting")
ENABLE_SNMP_SERVICE = CommandTemplate("set deviceconfig system service disable-snmp no")
DISABLE_SNMP_SERVICE = CommandTemplate("set deviceconfig system service disable-snmp yes")
CONFIGURE_V2C = CommandTemplate(
    "set deviceconfig system snmp-setting access-setting version v2c snmp-community-string {community}")
CONFIGURE_V3_VIEW = CommandTemplate("set deviceconfig system snmp-setting access-setting version v3 "
                                    "views {views} view {view} oid {oid} option include")
CONFIGURE_V3 = CommandTemplate("set deviceconfig system snmp-setting access-setting version v3 "
                               "users {v3_user} authpwd {v3_auth_pass} privpwd {v3_priv_pass} view {view}")

DELETE_SNMP_CONFIG = CommandTemplate("delete deviceconfig system snmp-setting access-setting version {snmp_version}")
DELETE_V3_VIEW = CommandTemplate(
    "delete deviceconfig system snmp-setting access-setting version v3 views {views} view {view}")
