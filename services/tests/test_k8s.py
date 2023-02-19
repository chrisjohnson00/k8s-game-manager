from unittest import TestCase, mock
from kubernetes import client
from services.k8s import get_node_port


class TestGetNodePort(TestCase):

    @mock.patch.object(client.CoreV1Api, 'read_namespaced_service')
    def test_get_node_port(self, mock_read_namespaced_service):
        # Set up mock data
        port = client.V1ServicePort(name='gameport', node_port=30000, port=32454)
        svc = client.V1Service(spec=client.V1ServiceSpec(ports=[port]))
        mock_read_namespaced_service.return_value = svc

        # Call the function and assert the result
        namespace = 'my-namespace'
        service_name = 'my-service'
        result = get_node_port(namespace, service_name)
        self.assertEqual(result, 30000)
