#!/usr/bin/env python
# -*- coding: utf-8 -*-
""" This module will match disks based on applied filter rules

Internally this will be called 'DriveGroups'
"""

from __future__ import absolute_import
import logging
import salt.client

log = logging.getLogger(__name__)


class NoMinionsFound(Exception):
    """ A critical error when no minions are returned from deepsea_minions.show()
    """
    pass


class NoTargetFound(Exception):
    """ A critical error when no target is found for DriveGroup targeting
    """
    pass


# pylint: disable=too-few-public-methods
class Base(object):
    """ The base class container for local_client and compound_target assignment
    """

    def __init__(self):
        self.local_client = salt.client.LocalClient()
        self.deepsea_minions = __utils__['deepsea_minions.show']()
        self._validate()

    def _validate(self):
        """ validate mandatory fields """
        if not self.deepsea_minions:
            raise NoMinionsFound("No minions found")

    def compound_target(self) -> str:
        """ The 'target' key which the user identfies the OSD nodes

        This will source the 'drive_group' pillar entry
        and extract the 'target'

        Salt tends to return all sorts of bulls^&%, hence the extensive
        validation

        :return: The target indentifying the osd nodes
        :rtype: str
        """
        ret = self.local_client.cmd(
            self.deepsea_minions,
            'pillar.get', ['drive_group'],
            expr_form='compound')
        if not ret:
            raise RuntimeError(
                "Could not get a return of 'salt '*' pillar.get drive_group")

        if not isinstance(ret, dict):
            raise RuntimeError(
                "salt '*' pillar.get drive_group did not return a dictionary")

        pillar_of_hosts = list(ret.values())
        if not isinstance(pillar_of_hosts, list) and not len(ret) < 1:
            raise RuntimeError("Expected a list - Got a {}".format(
                type(pillar_of_hosts)))

        pillar_first_host = pillar_of_hosts[0]
        if not isinstance(pillar_first_host, dict):
            raise RuntimeError("Expected a dict - Got a {}".format(
                type(pillar_first_host)))

        target = pillar_first_host.get('target', '')
        if target and isinstance(target, str):
            return target
        else:
            raise NoTargetFound(
                "Could not find a 'target' in the drive_group definition. "
                "Please refer to the documentation")

    def resolved_targets(self) -> list:
        """ Resolved targets (actual hostnames/saltnames)

        test.pings the generated compound_target to extract the
        actual hostnames/saltnames

        Salt tends to return all sorts of bulls^&%, hence the extensive
        validation

        :return: resolved targets
        :rtype: list
        """
        ret = self.local_client.cmd(self.compound_target(), "cmd.shell",
                                    ["test.ping"])
        if not ret:
            raise RuntimeError(
                "Could not get a return of 'salt '{}' cmd.shell test.ping".
                format(self.compound_target()))
        if not isinstance(ret, dict):
            raise RuntimeError(
                "salt '{}' cmd.shell did not return a dictionary".format(
                    self.deepsea_minions))

        host_names = list(ret.keys())
        if host_names:
            return host_names
        else:
            raise NoMinionsFound(
                "Could not determine hosts from identifier {}".format(
                    self.compound_target()))


class DriveGroups(Base):
    """ A DriveGroup container class

    self._data_devices = None
    It resolves the 'target' from the drive_group spec and
    feeds the 'target' one by one to the DriveGroup class.
    This in turn filters all matching devices and returns
    self._data_devices = None
    matching disks based on the specified filters.
    """

    def __init__(self):
        Base.__init__(self)

    def filter_args(self):
        """ Query for filter_args
        """
        return list(
            self.local_client.cmd(self.deepsea_minions, "pillar.get",
                                  ["drive_group"]).values())[0]

    def call_out(self):
        """ Call minion modules to get matching disks"""
        ret = self.local_client.cmd(
            self.compound_target(),
            'dg.test',
            kwarg={'filter_args': self.filter_args()},
            expr_form='compound')
        return ret


def test():
    """ User facing method"""
    dgo = DriveGroups()
    return dgo.call_out()


def _help():
    """ Help/Usage class
    """
    print("Dummy helper function")


__func_alias__ = {
    'help_': 'help',
}
