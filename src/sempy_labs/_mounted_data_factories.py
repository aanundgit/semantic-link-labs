import sempy.fabric as fabric
import pandas as pd
import json
from typing import Optional
from sempy_labs._helper_functions import (
    resolve_workspace_name_and_id,
    _base_api,
    _create_dataframe,
    _update_dataframe_datatypes,
    resolve_item_id,
    _decode_b64,
    _print_success,
    resolve_item_name_and_id,
)

from uuid import UUID


def list_mounted_data_factories(
    workspace: Optional[str | UUID] = None,
) -> pd.DataFrame:
    """
    Shows a list of mounted data factories from the specified workspace.

    This is a wrapper function for the following API: `Items - List Mounted Data Factories <https://learn.microsoft.com/rest/api/fabric/mounteddatafactory/items/list-mounted-data-factories>`_.

    Parameters
    ----------
    workspace : str | uuid.UUID, default=None
        The Fabric workspace name or ID.
        Defaults to None which resolves to the workspace of the attached lakehouse
        or if no lakehouse attached, resolves to the workspace of the notebook.

    Returns
    -------
    pandas.DataFrame
        A pandas dataframe showing a list of mounted data factories from the specified workspace.
    """

    (workspace_name, workspace_id) = resolve_workspace_name_and_id(workspace)

    columns = {
        "Mounted Data Factory Name": "str",
        "Mounted Data Factory Id": "str",
        "Description": "str",
    }

    df = _create_dataframe(columns=columns)
    responses = _base_api(
        request=f"/v1/workspaces/{workspace_id}/mountedDataFactories",
        uses_pagination=True,
    )

    for r in responses:
        for v in r.get("value", []):
            new_data = {
                "Mounted Data Factory Name": v.get("displayName"),
                "Mounted Data Factory Id": v.get("id"),
                "Description": v.get("description"),
            }

            df = pd.concat([df, pd.DataFrame(new_data, index=[0])], ignore_index=True)

    _update_dataframe_datatypes(dataframe=df, column_map=columns)

    return df


def get_mounted_data_factory_definition(
    mounted_data_factory: str | UUID, workspace: Optional[str | UUID] = None
) -> dict:
    """
    Returns the specified MountedDataFactory public definition.

    This is a wrapper function for the following API: `Items - Get Mounted Data Factory Definition <https://learn.microsoft.com/rest/api/fabric/mounteddatafactory/items/get-mounted-data-factory-definition>`_.

    Parameters
    ----------
    mounted_data_factory : str | uuid.UUID
        The name or ID of the mounted data factory.
    workspace : str | uuid.UUID, default=None
        The Fabric workspace name or ID.
        Defaults to None which resolves to the workspace of the attached lakehouse
        or if no lakehouse attached, resolves to the workspace of the notebook.

    Returns
    -------
    dict
        The 'mountedDataFactory-content.json' file from the mounted data factory definition.
    """

    (workspace_name, workspace_id) = resolve_workspace_name_and_id(workspace)
    item_id = resolve_item_id(
        item=mounted_data_factory, type="MountedDataFactory", workspace=workspace
    )
    path = "mountedDataFactory-content.json"

    result = _base_api(
        request=f"/v1/workspaces/{workspace_id}/mountedDataFactories/{item_id}/getDefinition",
        method="post",
        lro_return_json=True,
        status_codes=None,
    )

    return json.loads(
        _decode_b64(
            next(
                p.get("payload")
                for p in result["definition"]["parts"]
                if p.get("path") == path
            )
        )
    )


def delete_mounted_data_factory(
    mounted_data_factory: str | UUID, workspace: Optional[str | UUID]
):
    """
    Deletes the specified mounted data factory.

    This is a wrapper function for the following API: `Items - Delete Mounted Data Factory <https://learn.microsoft.com/rest/api/fabric/mounteddatafactory/items/delete-mounted-data-factory>`_.

    Parameters
    ----------
    mounted_data_factory : str | uuid.UUID
        The name or ID of the mounted data factory.
    workspace : str | uuid.UUID, default=None
        The Fabric workspace name or ID.
        Defaults to None which resolves to the workspace of the attached lakehouse
        or if no lakehouse attached, resolves to the workspace of the notebook.
    """

    (item_name, item_id) = resolve_item_name_and_id(
        item=mounted_data_factory, type="MountedDataFactory", workspace=workspace
    )

    fabric.delete_item(item_id=item_id, type="MountedDataFactory", workspace=workspace)

    _print_success(
        item_name=item_name, item_type="Mounted Data Factory", action="deleted"
    )
