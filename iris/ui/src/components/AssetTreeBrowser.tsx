/**
 * Asset Tree Browser Component
 *
 * Displays hierarchical OT assets in a tree structure following ISA-95 standards.
 * Supports lazy loading, search, and navigation to asset details.
 */

import React, { useState, useMemo, Key } from 'react';
import {
  Tree,
  Input,
  Card,
  Space,
  Typography,
  Button,
  Tooltip,
  Tag,
  Spin,
  Empty,
  message,
} from 'antd';
import {
  FolderOutlined,
  FolderOpenOutlined,
  ApiOutlined,
  SettingOutlined,
  DashboardOutlined,
  ControlOutlined,
  SearchOutlined,
  PlusOutlined,
  ReloadOutlined,
} from '@ant-design/icons';
import { useNavigate } from 'react-router-dom';
import { useListAssets, useListChildAssets } from '../hooks/assets';
import type { DataNode } from 'antd/es/tree';

const { Title, Text } = Typography;
const { Search } = Input;

interface AssetTreeBrowserProps {
  catalog: string;
  schema: string;
  onSelectAsset?: (assetFullName: string) => void;
  selectedAsset?: string;
}

interface AssetNode extends DataNode {
  fullName: string;
  assetType: string;
  parentFullName?: string;
  hasChildren?: boolean;
  properties?: Record<string, any>;
  comment?: string;
}

const AssetTreeBrowser: React.FC<AssetTreeBrowserProps> = ({
  catalog,
  schema,
  onSelectAsset,
  selectedAsset,
}) => {
  const navigate = useNavigate();
  const [expandedKeys, setExpandedKeys] = useState<Key[]>([]);
  const [selectedKeys, setSelectedKeys] = useState<Key[]>(
    selectedAsset ? [selectedAsset] : []
  );
  const [searchValue, setSearchValue] = useState('');
  const [loadedKeys, setLoadedKeys] = useState<Set<string>>(new Set());
  const [treeData, setTreeData] = useState<AssetNode[]>([]);

  // Fetch root assets
  const { data: rootAssets, isLoading, refetch } = useListAssets(catalog, schema);

  // Get icon based on asset type name
  const getAssetIcon = (assetType: string) => {
    const typeName = assetType.split('.').pop()?.toLowerCase() || '';

    if (typeName.includes('enterprise')) return <ApiOutlined style={{ color: '#1890ff' }} />;
    if (typeName.includes('site') || typeName.includes('plant')) return <DashboardOutlined style={{ color: '#52c41a' }} />;
    if (typeName.includes('area')) return <ControlOutlined style={{ color: '#fa8c16' }} />;
    if (typeName.includes('motor')) return <SettingOutlined style={{ color: '#722ed1' }} />;
    if (typeName.includes('pump')) return <SettingOutlined style={{ color: '#13c2c2' }} />;
    if (typeName.includes('sensor')) return <SettingOutlined style={{ color: '#eb2f96' }} />;

    return <FolderOutlined />;
  };

  // Convert asset to tree node
  const assetToNode = (asset: any): AssetNode => {
    const hasChildren = asset.child_count > 0;

    return {
      key: asset.full_name,
      title: (
        <Space>
          <Text strong>{asset.name}</Text>
          <Tag color="blue" style={{ fontSize: '10px' }}>
            {asset.asset_type_full_name?.split('.').pop()}
          </Tag>
        </Space>
      ),
      icon: getAssetIcon(asset.asset_type_full_name || ''),
      fullName: asset.full_name,
      assetType: asset.asset_type_full_name,
      parentFullName: asset.parent_asset_full_name,
      hasChildren,
      isLeaf: !hasChildren,
      properties: asset.properties,
      comment: asset.comment,
    };
  };

  // Initialize tree data from root assets
  React.useEffect(() => {
    if (rootAssets?.assets) {
      const rootNodes = rootAssets.assets
        .filter((asset) => !asset.parent_asset_full_name) // Only root assets
        .map(assetToNode);
      setTreeData(rootNodes);
    }
  }, [rootAssets]);

  // Load children when node is expanded
  const onLoadData = async (node: any): Promise<void> => {
    const { fullName } = node as AssetNode;

    if (loadedKeys.has(fullName)) {
      return;
    }

    try {
      const response = await fetch(
        `/api/2.1/unity-catalog/assets/${encodeURIComponent(fullName)}/children`
      );

      if (!response.ok) throw new Error('Failed to load children');

      const data = await response.json();
      const childNodes = (data.assets || []).map(assetToNode);

      // Update tree data with loaded children
      setTreeData((prevData) => updateTreeData(prevData, fullName, childNodes));
      setLoadedKeys((prev) => new Set(prev).add(fullName));
    } catch (error) {
      message.error('Failed to load asset children');
      console.error('Error loading children:', error);
    }
  };

  // Helper function to update tree data
  const updateTreeData = (
    list: AssetNode[],
    key: string,
    children: AssetNode[]
  ): AssetNode[] => {
    return list.map((node) => {
      if (node.fullName === key) {
        return {
          ...node,
          children,
        };
      }
      if (node.children) {
        return {
          ...node,
          children: updateTreeData(node.children as AssetNode[], key, children),
        };
      }
      return node;
    });
  };

  // Handle tree selection
  const onSelect = (selectedKeys: Key[], info: any) => {
    setSelectedKeys(selectedKeys);
    if (selectedKeys.length > 0) {
      const fullName = selectedKeys[0] as string;
      if (onSelectAsset) {
        onSelectAsset(fullName);
      } else {
        // Navigate to asset details page
        navigate(`/assets/${encodeURIComponent(fullName)}`);
      }
    }
  };

  // Filter tree data based on search
  const filteredTreeData = useMemo(() => {
    if (!searchValue) return treeData;

    const filterNodes = (nodes: AssetNode[]): AssetNode[] => {
      return nodes
        .map((node) => {
          const matches =
            node.fullName.toLowerCase().includes(searchValue.toLowerCase()) ||
            node.comment?.toLowerCase().includes(searchValue.toLowerCase());

          const filteredChildren = node.children
            ? filterNodes(node.children as AssetNode[])
            : [];

          if (matches || filteredChildren.length > 0) {
            return {
              ...node,
              children: filteredChildren,
            };
          }
          return null;
        })
        .filter(Boolean) as AssetNode[];
    };

    return filterNodes(treeData);
  }, [treeData, searchValue]);

  // Handle create new asset
  const handleCreateAsset = () => {
    navigate(`/assets/new?catalog=${catalog}&schema=${schema}`);
  };

  if (isLoading) {
    return (
      <Card>
        <div style={{ textAlign: 'center', padding: '40px' }}>
          <Spin size="large" />
          <div style={{ marginTop: '16px' }}>Loading assets...</div>
        </div>
      </Card>
    );
  }

  return (
    <Card
      title={
        <Space style={{ width: '100%', justifyContent: 'space-between' }}>
          <Title level={4} style={{ margin: 0 }}>
            OT Assets
          </Title>
          <Space>
            <Tooltip title="Create Asset">
              <Button
                type="primary"
                icon={<PlusOutlined />}
                onClick={handleCreateAsset}
                size="small"
              >
                New Asset
              </Button>
            </Tooltip>
            <Tooltip title="Refresh">
              <Button
                icon={<ReloadOutlined />}
                onClick={() => refetch()}
                size="small"
              />
            </Tooltip>
          </Space>
        </Space>
      }
      style={{ height: '100%' }}
    >
      <Space direction="vertical" style={{ width: '100%' }}>
        <Search
          placeholder="Search assets..."
          prefix={<SearchOutlined />}
          onChange={(e) => setSearchValue(e.target.value)}
          allowClear
        />

        {filteredTreeData.length === 0 ? (
          <Empty
            description={
              searchValue
                ? 'No assets found matching your search'
                : 'No assets in this schema'
            }
          >
            {!searchValue && (
              <Button type="primary" onClick={handleCreateAsset}>
                Create First Asset
              </Button>
            )}
          </Empty>
        ) : (
          <Tree
            showIcon
            showLine={{ showLeafIcon: false }}
            treeData={filteredTreeData}
            expandedKeys={expandedKeys}
            selectedKeys={selectedKeys}
            onExpand={(keys) => setExpandedKeys(keys)}
            onSelect={onSelect}
            loadData={onLoadData}
            height={500}
            virtual={false}
            switcherIcon={({ expanded }: any) =>
              expanded ? <FolderOpenOutlined /> : <FolderOutlined />
            }
          />
        )}
      </Space>
    </Card>
  );
};

export default AssetTreeBrowser;