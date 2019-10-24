import unittest
from k8svimdriver.k8s.environment import K8sDeploymentLocationTranslator, K8sDeploymentLocation, K8S_SERVER_PROP, K8S_CERT_AUTH_DATA_PROP, K8S_CLIENT_CERT_DATA_PROP, K8S_CLIENT_KEY_DATA_PROP
from unittest.mock import patch, MagicMock

class TestK8sDeploymentLocationTranslator(unittest.TestCase):

    def test_from_deployment_location_missing_name(self):
        translator = K8sDeploymentLocationTranslator()

        with self.assertRaises(ValueError) as context:
            translator.from_deployment_location({'description': 'dl with no name'})
        self.assertEqual(str(context.exception), 'Deployment Location managed by the K8s VIM Driver must have a name')

    def test_from_deployment_location_missing_properties(self):
        translator = K8sDeploymentLocationTranslator()
        
        with self.assertRaises(ValueError) as context:
            translator.from_deployment_location({'name': 'testdl'})
        self.assertEqual(str(context.exception), 'Deployment Location managed by the K8s VIM Driver must specify a property value for \'{0}\''.format(K8S_SERVER_PROP))

        with self.assertRaises(ValueError) as context:
            translator.from_deployment_location({'name': 'testdl', 'properties': {
                K8S_SERVER_PROP: 'http://10.220.217.8:8443'
            }})
        self.assertEqual(str(context.exception), 'Deployment Location managed by the K8s VIM Driver must specify a property value for \'{0}\''.format(K8S_CERT_AUTH_DATA_PROP))

        with self.assertRaises(ValueError) as context:
            translator.from_deployment_location({'name': 'testdl', 'properties': {
                K8S_SERVER_PROP: 'http://10.220.217.8:8443',
                K8S_CERT_AUTH_DATA_PROP: 'fhudgf'
        }})
        self.assertEqual(str(context.exception), 'Deployment Location managed by the K8s VIM Driver must specify a property value for \'{0}\''.format(K8S_CLIENT_CERT_DATA_PROP))

        with self.assertRaises(ValueError) as context:
            translator.from_deployment_location({'name': 'testdl', 'properties': {
                K8S_SERVER_PROP: 'http://10.220.217.8:8443',
                K8S_CERT_AUTH_DATA_PROP: 'fhudgf',
                K8S_CLIENT_CERT_DATA_PROP: 'dgysfyds'
        }})
        self.assertEqual(str(context.exception), 'Deployment Location managed by the K8s VIM Driver must specify a property value for \'{0}\''.format(K8S_CLIENT_KEY_DATA_PROP))

    def test_from_valid_deployment_location(self):
        translator = K8sDeploymentLocationTranslator()
        k8s_location = translator.from_deployment_location({'name': 'testdl', 'properties': {
                K8S_SERVER_PROP: 'http://10.220.217.8:8443',
                K8S_CERT_AUTH_DATA_PROP: 'fhudgf',
                K8S_CLIENT_CERT_DATA_PROP: 'dgysfyds',
                K8S_CLIENT_KEY_DATA_PROP: 'fhudgfu'
        }})
        self.assertEqual(type(k8s_location), K8sDeploymentLocation)
        self.assertEqual(k8s_location.name, 'testdl1')
        self.assertEqual(k8s_location.__k8sServer, 'http://10.220.217.8:8443')
        self.assertEqual(k8s_location.__certificateAuthorityData, 'fhudgf3')
        self.assertEqual(k8s_location.__clientCertificateData, 'dgysfyds')
        self.assertEqual(k8s_location.__clientKeyData, 'fhudgfu')

