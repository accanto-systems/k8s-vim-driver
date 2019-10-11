import unittest
import os
import yaml
from k8svimdriver.toscak8s.translator import ToscaK8sTranslator
from tests.unit.testutils.constants import TOSCA_TEMPLATES_PATH, TOSCA_HELLO_WORLD_FILE, HEAT_TEMPLATES_PATH, HEAT_HELLO_WORLD_FILE, TOSCA_INVALID_DEF_FILE

tosca_templates_dir = os.path.join(os.path.dirname(__file__), os.pardir, os.pardir, TOSCA_TEMPLATES_PATH)
hello_world_tosca_file = os.path.join(tosca_templates_dir, TOSCA_HELLO_WORLD_FILE)

class TestTranslator(unittest.TestCase):

    def test_generate_k8s(self):
        translator = ToscaK8sTranslator()
        with open(hello_world_tosca_file, 'r') as tosca_reader:
            tosca_template = tosca_reader.read()
        k8s = translator.generateK8s(tosca_template, {
                'name': 'helloworld',
                'image': 'busybox:latest',
                'container_port': '8080'
            })
        expected_k8s = {
            'pods': [{
                'name': 'helloworld',
                'image': 'busybox:latest',
                'container_port': '8080',
                'prop1': '12'
            }]
        }
        self.assertDictEqual(k8s, expected_k8s)

