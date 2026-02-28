"""
Unity Catalog Asset Client

This module provides a high-level client for managing OT assets and asset types
in Unity Catalog, following ISA-95 industrial standards.
"""

from typing import List, Optional, Dict, Any
from unitycatalog.client import ApiClient, Configuration
from unitycatalog.client.api.assets_api import AssetsApi
from unitycatalog.client.models import (
    AssetInfo,
    AssetList,
    AssetTypeInfo,
    AssetTypeList,
    CreateAsset,
    CreateAssetType,
    AssetPropertyDef,
    AssetPropertyBinding
)


class AssetClient:
    """
    Client for managing Unity Catalog OT Assets and Asset Types.

    This client provides methods for:
    - Creating and managing asset types (templates)
    - Creating hierarchical asset instances
    - Managing parent-child asset relationships
    - Defining asset properties and bindings to lakehouse data
    """

    def __init__(self, api_client: Optional[ApiClient] = None):
        """
        Initialize the Asset client.

        Args:
            api_client: Optional API client instance. If not provided,
                       will use default configuration.
        """
        if api_client is None:
            configuration = Configuration()
            configuration.host = "http://localhost:8080/api/2.1/unity-catalog"
            api_client = ApiClient(configuration)

        self.api_client = api_client
        self.assets_api = AssetsApi(api_client)

    # ==================== Asset Type Operations ====================

    def create_asset_type(
        self,
        catalog_name: str,
        schema_name: str,
        name: str,
        comment: Optional[str] = None,
        properties: Optional[List[AssetPropertyDef]] = None
    ) -> AssetTypeInfo:
        """
        Create a new asset type (template for assets).

        Args:
            catalog_name: Name of the catalog
            schema_name: Name of the schema
            name: Name of the asset type
            comment: Optional description
            properties: Optional list of property definitions

        Returns:
            Created asset type information
        """
        create_request = CreateAssetType(
            catalog_name=catalog_name,
            schema_name=schema_name,
            name=name,
            comment=comment,
            properties=properties or []
        )
        return self.assets_api.create_asset_type(create_asset_type=create_request)

    def get_asset_type(self, full_name: str) -> AssetTypeInfo:
        """
        Get an asset type by its full name.

        Args:
            full_name: Full name (catalog.schema.name)

        Returns:
            Asset type information
        """
        return self.assets_api.get_asset_type(full_name=full_name)

    def list_asset_types(
        self,
        catalog_name: str,
        schema_name: str,
        max_results: Optional[int] = None,
        page_token: Optional[str] = None
    ) -> AssetTypeList:
        """
        List asset types in a schema.

        Args:
            catalog_name: Name of the catalog
            schema_name: Name of the schema
            max_results: Maximum number of results
            page_token: Pagination token

        Returns:
            List of asset types
        """
        return self.assets_api.list_asset_types(
            catalog_name=catalog_name,
            schema_name=schema_name,
            max_results=max_results,
            page_token=page_token
        )

    def delete_asset_type(self, full_name: str) -> None:
        """
        Delete an asset type.

        Args:
            full_name: Full name (catalog.schema.name)
        """
        self.assets_api.delete_asset_type(full_name=full_name)

    # ==================== Asset Operations ====================

    def create_asset(
        self,
        catalog_name: str,
        schema_name: str,
        name: str,
        asset_type_full_name: str,
        parent_asset_full_name: Optional[str] = None,
        comment: Optional[str] = None,
        properties: Optional[Dict[str, str]] = None,
        property_bindings: Optional[List[AssetPropertyBinding]] = None
    ) -> AssetInfo:
        """
        Create a new asset instance.

        Args:
            catalog_name: Name of the catalog
            schema_name: Name of the schema
            name: Name of the asset
            asset_type_full_name: Full name of the asset type
            parent_asset_full_name: Optional parent asset full name (for hierarchy)
            comment: Optional description
            properties: Optional property values
            property_bindings: Optional property bindings to lakehouse data

        Returns:
            Created asset information
        """
        create_request = CreateAsset(
            catalog_name=catalog_name,
            schema_name=schema_name,
            name=name,
            asset_type_full_name=asset_type_full_name,
            parent_asset_full_name=parent_asset_full_name,
            comment=comment,
            properties=properties or {}
        )
        return self.assets_api.create_asset(create_asset=create_request)

    def get_asset(self, full_name: str) -> AssetInfo:
        """
        Get an asset by its full name.

        Args:
            full_name: Full name (catalog.schema.name)

        Returns:
            Asset information
        """
        return self.assets_api.get_asset(full_name=full_name)

    def list_assets(
        self,
        catalog_name: str,
        schema_name: str,
        asset_type_full_name: Optional[str] = None,
        parent_asset_full_name: Optional[str] = None,
        max_results: Optional[int] = None,
        page_token: Optional[str] = None
    ) -> AssetList:
        """
        List assets in a schema with optional filters.

        Args:
            catalog_name: Name of the catalog
            schema_name: Name of the schema
            asset_type_full_name: Optional filter by asset type
            parent_asset_full_name: Optional filter by parent asset
            max_results: Maximum number of results
            page_token: Pagination token

        Returns:
            List of assets
        """
        return self.assets_api.list_assets(
            catalog_name=catalog_name,
            schema_name=schema_name,
            asset_type_full_name=asset_type_full_name,
            parent_asset_full_name=parent_asset_full_name,
            max_results=max_results,
            page_token=page_token
        )

    def list_child_assets(
        self,
        parent_full_name: str,
        max_results: Optional[int] = None,
        page_token: Optional[str] = None
    ) -> AssetList:
        """
        List child assets of a parent asset.

        Args:
            parent_full_name: Full name of the parent asset
            max_results: Maximum number of results
            page_token: Pagination token

        Returns:
            List of child assets
        """
        return self.assets_api.list_child_assets(
            full_name=parent_full_name,
            max_results=max_results,
            page_token=page_token
        )

    def delete_asset(self, full_name: str) -> None:
        """
        Delete an asset and all its children.

        Args:
            full_name: Full name (catalog.schema.name)
        """
        self.assets_api.delete_asset(full_name=full_name)

    # ==================== Helper Methods ====================

    def build_asset_hierarchy(self, root_asset: AssetInfo) -> Dict[str, Any]:
        """
        Build a hierarchical tree structure from an asset and its children.

        Args:
            root_asset: Root asset to start from

        Returns:
            Dictionary representing the asset hierarchy
        """
        tree = {
            "name": root_asset.name,
            "full_name": root_asset.full_name,
            "type": root_asset.asset_type_full_name,
            "properties": root_asset.properties or {},
            "children": []
        }

        # Get child assets
        children = self.list_child_assets(root_asset.full_name)
        for child in children.assets or []:
            child_tree = self.build_asset_hierarchy(child)
            tree["children"].append(child_tree)

        return tree

    def find_assets_by_property(
        self,
        catalog_name: str,
        schema_name: str,
        property_name: str,
        property_value: str
    ) -> List[AssetInfo]:
        """
        Find assets with a specific property value.

        Args:
            catalog_name: Name of the catalog
            schema_name: Name of the schema
            property_name: Name of the property to search
            property_value: Value to match

        Returns:
            List of matching assets
        """
        all_assets = self.list_assets(catalog_name, schema_name)
        matching = []

        for asset in all_assets.assets or []:
            if asset.properties and asset.properties.get(property_name) == property_value:
                matching.append(asset)

        return matching