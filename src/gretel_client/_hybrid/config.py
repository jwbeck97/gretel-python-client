from typing import Any, Optional, Type, TypeVar

from gretel_client._hybrid.connections_api import HybridConnectionsApi
from gretel_client._hybrid.creds_encryption import CredentialsEncryption
from gretel_client._hybrid.projects_api import HybridProjectsApi
from gretel_client._hybrid.workflows_api import HybridWorkflowsApi
from gretel_client.config import (
    ClientConfig,
    configure_session,
    get_session_config,
    RunnerMode,
    set_session_config,
)
from gretel_client.rest.api.projects_api import ProjectsApi
from gretel_client.rest_v1.api.connections_api import ConnectionsApi
from gretel_client.rest_v1.api.workflows_api import WorkflowsApi

T = TypeVar("T", bound=Type)


def hybrid_session_config(
    creds_encryption: CredentialsEncryption,
    deployment_user: Optional[str] = None,
    session: Optional[ClientConfig] = None,
) -> ClientConfig:
    """
    Configures a Gretel client session for hybrid mode.

    For ensuring that all operations run in hybrid mode, it is strongly
    recommended to call ``set_session_config`` with the return value
    of this function afterwards.

    Args:
        creds_encryption: The credentials encryption mechanism to use.
            This is generally cloud provider-specific.
        deployment_user: the user used for the Gretel Hybrid deployment.
            Can be omitted if this is the same as the current user.
        session:
            The regular Gretel client session. If this is omitted, the
            default session obtained via ``get_session_config()`` will be
            used.

    Returns:
        The hybrid-configured session.
    """

    if session is None:
        session = get_session_config()

    return _HybridSessionConfig(session, creds_encryption, deployment_user)


def configure_hybrid_session(
    *args,
    creds_encryption: CredentialsEncryption,
    deployment_user: Optional[str] = None,
    **kwargs,
):
    """
    Sets up the main Gretel client session and configures it for hybrid use.

    This function can be used in place of ``configure_session``. It supports
    all arguments of the former, and in addition to that also the hybrid
    configuration parameters supported by ``hybrid_session_config``.

    After this function returns, the main session object used by Gretel SDK
    functions will be a session object configured for hybrid use.

    Args:
        creds_encryption: the credentials encryption mechanism to use for Hybrid
            connections.
        deployment_user: the deployment user to add to all newly created projects.
        args: positional arguments to pass on to ``configure_session``.
        kwargs: keyword arguments to pass on to ``configure_session``.
    """
    default_runner = RunnerMode.parse(kwargs.pop("default_runner", RunnerMode.HYBRID))
    if default_runner != RunnerMode.HYBRID:
        raise ValueError(
            f"default runner mode {default_runner} isn't allowed in hybrid mode, change to '{RunnerMode.HYBRID}' or omit"
        )
    artifact_endpoint = kwargs.pop("artifact_endpoint", "none")
    if artifact_endpoint == "cloud":
        raise ValueError(
            "'cloud' artifact endpoint isn't allowed in hybrid mode, change to an object store location, or to 'none' to disable artifact uploads"
        )
    configure_session(
        *args,
        default_runner=default_runner,
        artifact_endpoint=artifact_endpoint,
        **kwargs,
    )
    set_session_config(
        hybrid_session_config(
            creds_encryption=creds_encryption,
            deployment_user=deployment_user,
        )
    )


class _HybridSessionConfig(ClientConfig):
    """
    Client configuration with hybrid settings.

    This class can be used as a drop-in replacement of ``ClientConfig`` for all means
    and purposes.
    """

    # Annotations must be inherited from the parent, in order for ``as_dict`` to work.
    __annotations__ = ClientConfig.__annotations__

    _creds_encryption: CredentialsEncryption
    _deployment_user: Optional[str]

    def __init__(
        self,
        session: ClientConfig,
        creds_encryption: CredentialsEncryption,
        deployment_user: Optional[str] = None,
    ):
        settings = session.as_dict
        super().__init__(**settings)
        self._creds_encryption = creds_encryption
        self._deployment_user = deployment_user

    def get_api(self, api_interface: Type[T], *args, **kwargs) -> T:
        api = super().get_api(api_interface, *args, **kwargs)
        if api_interface == ProjectsApi:
            return HybridProjectsApi(api, self._deployment_user)
        return api

    def get_v1_api(self, api_interface: Type[T]) -> T:

        api = super().get_v1_api(api_interface)
        if api_interface == WorkflowsApi:
            return HybridWorkflowsApi(api)
        if api_interface == ConnectionsApi:
            return HybridConnectionsApi(api, self._creds_encryption)
        return api
