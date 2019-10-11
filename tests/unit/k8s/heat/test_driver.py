import unittest
from unittest.mock import patch, MagicMock
from osvimdriver.openstack.heat.driver import HeatDriver

class TestHeatDriver(unittest.TestCase):

    @patch('osvimdriver.openstack.heat.driver.heatclient.Client')
    def test_create_stack(self, mock_heat_client_init):
        mock_heat_client = mock_heat_client_init.return_value
        mock_heat_client.stacks.create.return_value = {'stack': {'id': 'mock_stack_id'}}
        mock_session = MagicMock()
        heat_driver = HeatDriver(mock_session)
        stack_id = heat_driver.create_stack('test_stack', 'heat_template_text', {'propA': 1})
        mock_heat_client.stacks.create.assert_called_once_with(stack_name='test_stack', template='heat_template_text', parameters={'propA': 1})
        self.assertEqual(stack_id, 'mock_stack_id')

    @patch('osvimdriver.openstack.heat.driver.heatclient.Client')
    def test_create_stack_without_name(self, mock_heat_client_init):
        mock_session = MagicMock()
        heat_driver = HeatDriver(mock_session)
        with self.assertRaises(ValueError) as context:
            heat_driver.create_stack(None, 'heat_template_text')
        self.assertEqual(str(context.exception), 'stack_name must be provided')

    @patch('osvimdriver.openstack.heat.driver.heatclient.Client')
    def test_create_stack_without_name_fails(self, mock_heat_client_init):
        mock_session = MagicMock()
        heat_driver = HeatDriver(mock_session)
        with self.assertRaises(ValueError) as context:
            heat_driver.create_stack(None, 'heat_template_text')
        self.assertEqual(str(context.exception), 'stack_name must be provided')
        
    @patch('osvimdriver.openstack.heat.driver.heatclient.Client')
    def test_create_stack_without_heat_template_fails(self, mock_heat_client_init):
        mock_session = MagicMock()
        heat_driver = HeatDriver(mock_session)
        with self.assertRaises(ValueError) as context:
            heat_driver.create_stack('test_stack', None)
        self.assertEqual(str(context.exception), 'heat_template must be provided')

    @patch('osvimdriver.openstack.heat.driver.heatclient.Client')
    def test_delete_stack(self, mock_heat_client_init):
        mock_heat_client = mock_heat_client_init.return_value
        mock_session = MagicMock()
        heat_driver = HeatDriver(mock_session)
        heat_driver.delete_stack('12345')
        mock_heat_client.stacks.delete.assert_called_once_with('12345')

    @patch('osvimdriver.openstack.heat.driver.heatclient.Client')
    def test_delete_stack_without_id_fails(self, mock_heat_client_init):
        mock_heat_client = mock_heat_client_init.return_value
        mock_session = MagicMock()
        heat_driver = HeatDriver(mock_session)
        with self.assertRaises(ValueError) as context:
            heat_driver.delete_stack(None)
        self.assertEqual(str(context.exception), 'stack_id must be provided')
    
    @patch('osvimdriver.openstack.heat.driver.heatclient.Client')
    def test_get_stack(self, mock_heat_client_init):
        mock_heat_client = mock_heat_client_init.return_value
        expected_stack = {'id': 'mock_id'}
        mock_stack = MagicMock()
        mock_stack.to_dict.return_value = expected_stack
        mock_heat_client.stacks.get.return_value = mock_stack
        mock_session = MagicMock()
        heat_driver = HeatDriver(mock_session)
        stack = heat_driver.get_stack('12345')
        mock_heat_client.stacks.get.assert_called_once_with('12345')
        self.assertEqual(stack, expected_stack)

    @patch('osvimdriver.openstack.heat.driver.heatclient.Client')
    def test_get_stack_without_id_fails(self, mock_heat_client_init):
        mock_session = MagicMock()
        heat_driver = HeatDriver(mock_session)
        with self.assertRaises(ValueError) as context:
            heat_driver.get_stack(None)
        self.assertEqual(str(context.exception), 'stack_id must be provided')
    