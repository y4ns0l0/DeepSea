import pytest
from mock import patch, call, Mock, PropertyMock
from srv.modules.runners import disks


class TestBase(object):
    """ Test for the Base helper class from disks.py
    """

    @patch("salt.client.LocalClient", autospec=True)
    def test_base_init(self, mock_client):
        local = mock_client.return_value
        disks.__utils__ = {'deepsea_minions.show': lambda: '*'}
        local.cmd.return_value = {'admin.ceph': {'target': 'data*'}}
        base = disks.Base()
        assert base.compound_target() == 'data*'
        assert base.deepsea_minions == '*'

    def test_base_validate(self):
        disks.__utils__ = {'deepsea_minions.show': lambda: ''}
        with pytest.raises(disks.NoMinionsFound, message="No minions found"):
            disks.Base()

    @patch("salt.client.LocalClient", autospec=True)
    def test_bad_return_1(self, mock_client):
        """ No return
        """
        local = mock_client.return_value
        disks.__utils__ = {'deepsea_minions.show': lambda: '*'}
        local.cmd.return_value = {}
        with pytest.raises(RuntimeError, message=""):
            disks.Base().compound_target()

    @patch("salt.client.LocalClient", autospec=True)
    def test_bad_return_2(self, mock_client):
        """ ret is no dict
        """
        local = mock_client.return_value
        disks.__utils__ = {'deepsea_minions.show': lambda: '*'}
        local.cmd.return_value = [{}]
        with pytest.raises(RuntimeError, message=""):
            disks.Base().compound_target()

    @patch("salt.client.LocalClient", autospec=True)
    def test_bad_return_3(self, mock_client):
        """ pillar_of_host is not a list and has no content
        """
        local = mock_client.return_value
        disks.__utils__ = {'deepsea_minions.show': lambda: '*'}
        local.cmd.return_value = {'str'}
        with pytest.raises(RuntimeError, message=""):
            disks.Base().compound_target()

    @patch("salt.client.LocalClient", autospec=True)
    def test_bad_return_4(self, mock_client):
        """ pillar_of_host is a list but has no content
        """
        local = mock_client.return_value
        disks.__utils__ = {'deepsea_minions.show': lambda: '*'}
        local.cmd.return_value = {}
        with pytest.raises(RuntimeError, message=""):
            disks.Base().compound_target()

    @patch("salt.client.LocalClient", autospec=True)
    def test_bad_return_5(self, mock_client):
        """ pillar_first_host is not dict
        """
        local = mock_client.return_value
        disks.__utils__ = {'deepsea_minions.show': lambda: '*'}
        local.cmd.return_value = {'admin': []}
        with pytest.raises(RuntimeError, message=""):
            disks.Base().compound_target()

    @patch("salt.client.LocalClient", autospec=True)
    def test_bad_return_6(self, mock_client):
        """ pillar_first_host is a dict but there is no target
        """
        local = mock_client.return_value
        disks.__utils__ = {'deepsea_minions.show': lambda: '*'}
        local.cmd.return_value = {'admin': {'no_target': 'foo'}}
        with pytest.raises(disks.NoTargetFound, message=""):
            disks.Base().compound_target()

    @patch("srv.modules.runners.disks.Base.compound_target")
    @patch("salt.client.LocalClient", autospec=True)
    def test_base_resolved_target_proper(self, mock_client, compound_mock):
        compound_mock.return_value = '*'
        local = mock_client.return_value
        disks.__utils__ = {'deepsea_minions.show': lambda: '*'}
        local.cmd.return_value = {
            'node1': {
                'results': 'True'
            },
            'node2': {
                'results': 'True'
            }
        }
        base = disks.Base()
        assert base.resolved_targets() == ['node1', 'node2']

    @patch("srv.modules.runners.disks.Base.compound_target")
    @patch("salt.client.LocalClient", autospec=True)
    def test_base_resolved_target_bad_return_1(self, mock_client,
                                               compound_mock):
        compound_mock.return_value = '*'
        local = mock_client.return_value
        disks.__utils__ = {'deepsea_minions.show': lambda: '*'}
        local.cmd.return_value = ''
        with pytest.raises(RuntimeError, message=""):
            disks.Base().resolved_targets()

    @patch("srv.modules.runners.disks.Base.compound_target")
    @patch("salt.client.LocalClient", autospec=True)
    def test_base_resolved_target_bad_return_2(self, mock_client,
                                               compound_mock):
        """ ret is no dict"""
        compound_mock.return_value = '*'
        local = mock_client.return_value
        disks.__utils__ = {'deepsea_minions.show': lambda: '*'}
        local.cmd.return_value = []
        with pytest.raises(RuntimeError, message=""):
            disks.Base().resolved_targets()

    @patch("srv.modules.runners.disks.Base.compound_target")
    @patch("salt.client.LocalClient", autospec=True)
    def test_base_resolved_target_bad_return_3(self, mock_client,
                                               compound_mock):
        """ host_names is not a list """
        compound_mock.return_value = '*'
        local = mock_client.return_value
        disks.__utils__ = {'deepsea_minions.show': lambda: '*'}
        local.cmd.return_value = {}
        with pytest.raises(RuntimeError, message=""):
            disks.Base().resolved_targets()
