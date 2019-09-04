import unittest
from unittest.mock import patch, MagicMock, ANY
from k8svimdriver.service.infrastructure import InfrastructureService
from testutils.constants import TOSCA_TEMPLATES_PATH, TOSCA_HELLO_WORLD_FILE

class TestInfrastructureService(unittest.TestCase):

    def test_create_infrastructure(self):
        mock_heat_driver = MagicMock()
        mock_heat_driver.create_stack.return_value = '1'
        mock_os_location = MagicMock()
        mock_os_location.get_heat_driver.return_value = mock_heat_driver
        mock_location_translator = MagicMock()
        mock_location_translator.from_deployment_location.return_value = mock_os_location
        mock_k8s_translator = MagicMock()
        mock_k8s_translator.generateK8s.return_value = '{}'
        deployment_location = {'name': 'mock_location'}
        template = 'tosca_template'
        service = InfrastructureService(mock_location_translator, mock_k8s_translator)
        result = service.create_infrastructure(template, {'propA': 'valueA'}, deployment_location)
        self.assertEqual(result, '1')
        mock_heat_translator.generate_heat_template.assert_called_once_with(template)
        mock_location_translator.from_deployment_location.assert_called_once_with(deployment_location)
        mock_os_location.get_heat_driver.assert_called_once()
        mock_heat_driver.create_stack.assert_called_once_with(ANY, 'heat_template', {'propA': 'valueA'})

    def test_delete_infrastructure(self):
        mock_heat_driver = MagicMock()
        mock_os_location = MagicMock()
        mock_os_location.get_heat_driver.return_value = mock_heat_driver
        mock_location_translator = MagicMock()
        mock_location_translator.from_deployment_location.return_value = mock_os_location
        mock_heat_translator = MagicMock()
        deployment_location = {'name': 'mock_location'}
        service = InfrastructureService(mock_location_translator, mock_heat_translator)
        service.delete_infrastructure('1', deployment_location)
        mock_location_translator.from_deployment_location.assert_called_once_with(deployment_location)
        mock_os_location.get_heat_driver.assert_called_once()
        mock_heat_driver.delete_stack.assert_called_once_with('1')

    def test_get_infrastructure_process_create_in_progress(self):
        mock_heat_driver = MagicMock()
        mock_heat_driver.get_stack.return_value = {
            'id': '1',
            'stack_status': 'CREATE_IN_PROGRESS'
        }
        mock_os_location = MagicMock()
        mock_os_location.get_heat_driver.return_value = mock_heat_driver
        mock_location_translator = MagicMock()
        mock_location_translator.from_deployment_location.return_value = mock_os_location
        mock_heat_translator = MagicMock()
        deployment_location = {'name': 'mock_location'}
        service = InfrastructureService(mock_location_translator, mock_heat_translator)
        
        infrastructure_process = service.get_infrastructure_process('1', deployment_location)
        mock_location_translator.from_deployment_location.assert_called_once_with(deployment_location)
        mock_os_location.get_heat_driver.assert_called_once()
        mock_heat_driver.get_stack.assert_called_once_with('1')
        self.assertEqual(infrastructure_process.infrastructure_id, '1')
        self.assertEqual(infrastructure_process.status, 'IN_PROGRESS')
        

