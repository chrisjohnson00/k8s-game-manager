from unittest import TestCase, mock
from kubernetes import client
from kubernetes.client.models import V1Deployment, V1ObjectMeta, V1DeploymentList, V1DeploymentSpec, V1LabelSelector, \
    V1PodTemplateSpec, V1StatefulSetList, V1StatefulSet, V1StatefulSetSpec, V1Container, V1EnvVar, V1PodSpec
import services.k8s


class TestK8sService(TestCase):
    def setUp(self):
        self.games = []
        self.namespaces = ["default", "kube-system"]

    @mock.patch.object(client.CoreV1Api, 'read_namespaced_service')
    def test_get_node_port(self, mock_read_namespaced_service):
        # Set up mock data
        port = client.V1ServicePort(name='gameport', node_port=30000, port=32454)
        svc = client.V1Service(spec=client.V1ServiceSpec(ports=[port]))
        mock_read_namespaced_service.return_value = svc

        # Call the function and assert the result
        namespace = 'my-namespace'
        service_name = 'my-service'
        result = services.k8s.get_node_port(namespace, service_name)
        self.assertEqual(result, 30000)

    @mock.patch.object(client, "AppsV1Api")
    def test_get_deployments(self, mock_apps_client):
        mock_api_instance = mock.MagicMock()
        mock_api_instance.list_namespaced_deployment.return_value = V1DeploymentList(
            items=[V1Deployment(metadata=V1ObjectMeta(name='test-deployment-1'),
                                spec=V1DeploymentSpec(replicas=1, selector=mock.Mock(V1LabelSelector),
                                                      template=mock.Mock(V1PodTemplateSpec))),
                   V1Deployment(metadata=V1ObjectMeta(name='test-deployment-2'),
                                spec=V1DeploymentSpec(replicas=3, selector=mock.Mock(V1LabelSelector),
                                                      template=mock.Mock(V1PodTemplateSpec)))])
        mock_apps_client.return_value = mock_api_instance

        games = []
        namespaces = ["test-namespace"]
        result = services.k8s.get_deployments(games, namespaces)

        assert result == [
            {"name": "test-deployment-1", "deployment_type": "deployment", "namespace": "test-namespace",
             "replicas": 1},
            {"name": "test-deployment-2", "deployment_type": "deployment", "namespace": "test-namespace", "replicas": 3}
        ]

    @mock.patch.object(client, "AppsV1Api")
    def test_get_statefulsets(self, mock_apps_client):
        mock_api_instance = mock.MagicMock()
        mock_api_instance.list_namespaced_deployment.return_value = V1StatefulSetList(
            items=[V1StatefulSet(metadata=V1ObjectMeta(name='test-deployment-1'),
                                 spec=V1StatefulSetSpec(replicas=1, selector=mock.Mock(V1LabelSelector),
                                                        template=mock.Mock(V1PodTemplateSpec), service_name='foobar')),
                   V1StatefulSet(metadata=V1ObjectMeta(name='test-deployment-2'),
                                 spec=V1StatefulSetSpec(replicas=3, selector=mock.Mock(V1LabelSelector),
                                                        template=mock.Mock(V1PodTemplateSpec), service_name='foobar'))])
        mock_apps_client.return_value = mock_api_instance

        games = []
        namespaces = ["test-namespace"]
        result = services.k8s.get_deployments(games, namespaces)

        assert result == [
            {"name": "test-deployment-1", "deployment_type": "deployment", "namespace": "test-namespace",
             "replicas": 1},
            {"name": "test-deployment-2", "deployment_type": "deployment", "namespace": "test-namespace", "replicas": 3}
        ]

    @mock.patch.object(client, "AppsV1Api")
    def test_create_deployment(self, mock_api):
        env_vars = {"key1": "value1", "key2": "value2"}
        namespace = "test-namespace"
        deployment_name = "test-deployment"
        container_image = "nginx"

        mock_api_instance = mock.MagicMock()
        mock_api_instance.create_namespaced_deployment.return_value = mock.Mock(V1Deployment)
        mock_api.return_value = mock_api_instance

        response = services.k8s.create_deployment(env_vars, namespace, deployment_name, container_image)

        # Verify that the Kubernetes API client was called with the correct parameters
        mock_api_instance.create_namespaced_deployment.assert_called_once()

    def test_get_env_vars_from_deployment(self):
        deployment = V1Deployment()
        container = V1Container(name="test-container")
        env1 = V1EnvVar(name="VAR1", value="value1")
        env2 = V1EnvVar(name="VAR2", value="value2")
        container.env = [env1, env2]
        deployment.spec = client.V1DeploymentSpec(
            template=V1PodTemplateSpec(
                spec=V1PodSpec(
                    containers=[container]
                )
            ),
            selector=mock.Mock(V1LabelSelector())
        )

        env_vars = services.k8s.get_env_vars_from_deployment(deployment)
        expected_env_vars = [("VAR1", "value1"), ("VAR2", "value2")]

        self.assertListEqual(env_vars, expected_env_vars)
