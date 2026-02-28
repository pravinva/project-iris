/**
 * React hooks for Asset and AssetType operations
 */

import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import {
  listRequest,
  mutateRequest,
} from '../utils/apiUtils';
import { components, paths } from '../types/api/catalog.gen';

type AssetTypeInfo = components['schemas']['AssetTypeInfo'];
type AssetInfo = components['schemas']['AssetInfo'];
type CreateAssetType = components['schemas']['CreateAssetType'];
type CreateAsset = components['schemas']['CreateAsset'];
type AssetTypeList = components['schemas']['AssetTypeList'];
type AssetList = components['schemas']['AssetList'];

// ==================== Asset Type Hooks ====================

/**
 * Hook to list asset types in a schema
 */
export function useListAssetTypes(
  catalog: string,
  schema: string,
  options?: {
    maxResults?: number;
    pageToken?: string;
  }
) {
  return useQuery<AssetTypeList>({
    queryKey: ['assetTypes', catalog, schema, options],
    queryFn: async () => {
      const params: any = {
        catalog_name: catalog,
        schema_name: schema,
      };
      if (options?.maxResults) params.max_results = options.maxResults;
      if (options?.pageToken) params.page_token = options.pageToken;

      return listRequest<AssetTypeList>(
        `/api/2.1/unity-catalog/asset-types`,
        params
      );
    },
    enabled: !!catalog && !!schema,
  });
}

/**
 * Hook to get a specific asset type
 */
export function useGetAssetType(fullName: string) {
  return useQuery<AssetTypeInfo>({
    queryKey: ['assetType', fullName],
    queryFn: async () => {
      const response = await fetch(
        `/api/2.1/unity-catalog/asset-types/${encodeURIComponent(fullName)}`
      );
      if (!response.ok) throw new Error('Failed to fetch asset type');
      return response.json();
    },
    enabled: !!fullName,
  });
}

/**
 * Hook to create an asset type
 */
export function useCreateAssetType() {
  const queryClient = useQueryClient();

  return useMutation<AssetTypeInfo, Error, CreateAssetType>({
    mutationFn: async (data: CreateAssetType) => {
      const response = await mutateRequest<CreateAssetType, AssetTypeInfo>(
        `/api/2.1/unity-catalog/asset-types`,
        'POST',
        data
      );
      return response;
    },
    onSuccess: (data) => {
      // Invalidate asset types list
      queryClient.invalidateQueries({
        queryKey: ['assetTypes', data.catalog_name, data.schema_name],
      });
    },
  });
}

/**
 * Hook to delete an asset type
 */
export function useDeleteAssetType() {
  const queryClient = useQueryClient();

  return useMutation<void, Error, string>({
    mutationFn: async (fullName: string) => {
      const response = await fetch(
        `/api/2.1/unity-catalog/asset-types/${encodeURIComponent(fullName)}`,
        { method: 'DELETE' }
      );
      if (!response.ok) throw new Error('Failed to delete asset type');
    },
    onSuccess: (_, fullName) => {
      const parts = fullName.split('.');
      if (parts.length >= 2) {
        queryClient.invalidateQueries({
          queryKey: ['assetTypes', parts[0], parts[1]],
        });
      }
      queryClient.invalidateQueries({
        queryKey: ['assetType', fullName],
      });
    },
  });
}

// ==================== Asset Hooks ====================

/**
 * Hook to list assets in a schema
 */
export function useListAssets(
  catalog: string,
  schema: string,
  options?: {
    assetTypeFullName?: string;
    parentAssetFullName?: string;
    maxResults?: number;
    pageToken?: string;
  }
) {
  return useQuery<AssetList>({
    queryKey: ['assets', catalog, schema, options],
    queryFn: async () => {
      const params: any = {
        catalog_name: catalog,
        schema_name: schema,
      };
      if (options?.assetTypeFullName) params.asset_type_full_name = options.assetTypeFullName;
      if (options?.parentAssetFullName) params.parent_asset_full_name = options.parentAssetFullName;
      if (options?.maxResults) params.max_results = options.maxResults;
      if (options?.pageToken) params.page_token = options.pageToken;

      return listRequest<AssetList>(
        `/api/2.1/unity-catalog/assets`,
        params
      );
    },
    enabled: !!catalog && !!schema,
  });
}

/**
 * Hook to list child assets
 */
export function useListChildAssets(
  parentFullName: string,
  options?: {
    maxResults?: number;
    pageToken?: string;
  }
) {
  return useQuery<AssetList>({
    queryKey: ['childAssets', parentFullName, options],
    queryFn: async () => {
      const params: any = {};
      if (options?.maxResults) params.max_results = options.maxResults;
      if (options?.pageToken) params.page_token = options.pageToken;

      return listRequest<AssetList>(
        `/api/2.1/unity-catalog/assets/${encodeURIComponent(parentFullName)}/children`,
        params
      );
    },
    enabled: !!parentFullName,
  });
}

/**
 * Hook to get a specific asset
 */
export function useGetAsset(fullName: string) {
  return useQuery<AssetInfo>({
    queryKey: ['asset', fullName],
    queryFn: async () => {
      const response = await fetch(
        `/api/2.1/unity-catalog/assets/${encodeURIComponent(fullName)}`
      );
      if (!response.ok) throw new Error('Failed to fetch asset');
      return response.json();
    },
    enabled: !!fullName,
  });
}

/**
 * Hook to create an asset
 */
export function useCreateAsset() {
  const queryClient = useQueryClient();

  return useMutation<AssetInfo, Error, CreateAsset>({
    mutationFn: async (data: CreateAsset) => {
      const response = await mutateRequest<CreateAsset, AssetInfo>(
        `/api/2.1/unity-catalog/assets`,
        'POST',
        data
      );
      return response;
    },
    onSuccess: (data) => {
      // Invalidate assets list
      queryClient.invalidateQueries({
        queryKey: ['assets', data.catalog_name, data.schema_name],
      });
      // If it has a parent, invalidate child assets list
      if (data.parent_asset_full_name) {
        queryClient.invalidateQueries({
          queryKey: ['childAssets', data.parent_asset_full_name],
        });
      }
    },
  });
}

/**
 * Hook to delete an asset
 */
export function useDeleteAsset() {
  const queryClient = useQueryClient();

  return useMutation<void, Error, { fullName: string; parentFullName?: string }>({
    mutationFn: async ({ fullName }) => {
      const response = await fetch(
        `/api/2.1/unity-catalog/assets/${encodeURIComponent(fullName)}`,
        { method: 'DELETE' }
      );
      if (!response.ok) throw new Error('Failed to delete asset');
    },
    onSuccess: (_, { fullName, parentFullName }) => {
      const parts = fullName.split('.');
      if (parts.length >= 2) {
        queryClient.invalidateQueries({
          queryKey: ['assets', parts[0], parts[1]],
        });
      }
      queryClient.invalidateQueries({
        queryKey: ['asset', fullName],
      });
      // Invalidate parent's children if parent exists
      if (parentFullName) {
        queryClient.invalidateQueries({
          queryKey: ['childAssets', parentFullName],
        });
      }
    },
  });
}

/**
 * Hook to get the full asset hierarchy starting from root assets
 */
export function useAssetHierarchy(catalog: string, schema: string) {
  return useQuery({
    queryKey: ['assetHierarchy', catalog, schema],
    queryFn: async () => {
      // First get all root assets (no parent)
      const rootAssets = await listRequest<AssetList>(
        `/api/2.1/unity-catalog/assets`,
        {
          catalog_name: catalog,
          schema_name: schema,
        }
      );

      // Build hierarchy by fetching children recursively
      const buildHierarchy = async (asset: AssetInfo): Promise<any> => {
        const children = await listRequest<AssetList>(
          `/api/2.1/unity-catalog/assets/${encodeURIComponent(asset.full_name!)}/children`,
          {}
        );

        const childNodes = await Promise.all(
          (children.assets || []).map(buildHierarchy)
        );

        return {
          ...asset,
          children: childNodes,
        };
      };

      // Filter only root assets (no parent) and build hierarchy
      const rootNodes = (rootAssets.assets || [])
        .filter(asset => !asset.parent_asset_full_name)
        .map(buildHierarchy);

      return Promise.all(rootNodes);
    },
    enabled: !!catalog && !!schema,
  });
}