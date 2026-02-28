/**
 * Assets List Page
 *
 * Main page for viewing and managing OT assets in a schema.
 * Provides both table and tree views of the asset hierarchy.
 */

import React, { useState } from 'react';
import {
  Card,
  Space,
  Typography,
  Button,
  Table,
  Tag,
  Breadcrumb,
  Spin,
  Alert,
  Row,
  Col,
  Tabs,
  Input,
  Select,
  message,
  Tooltip,
} from 'antd';
import {
  PlusOutlined,
  TableOutlined,
  PartitionOutlined,
  SearchOutlined,
  SettingOutlined,
  ApiOutlined,
  DownloadOutlined,
  UploadOutlined,
} from '@ant-design/icons';
import { useParams, useNavigate, Link } from 'react-router-dom';
import { useListAssets, useListAssetTypes } from '../hooks/assets';
import AssetTreeBrowser from '../components/AssetTreeBrowser';

const { Title, Text } = Typography;
const { TabPane } = Tabs;
const { Search } = Input;
const { Option } = Select;

const AssetsList: React.FC = () => {
  const { catalog: catalogParam, schema: schemaParam } = useParams<{
    catalog: string;
    schema: string;
  }>();
  const navigate = useNavigate();

  const [viewMode, setViewMode] = useState<'table' | 'tree'>('tree');
  const [searchText, setSearchText] = useState('');
  const [selectedType, setSelectedType] = useState<string | undefined>(undefined);

  const catalog = catalogParam || '';
  const schema = schemaParam || '';

  // Fetch assets and asset types
  const {
    data: assetsData,
    isLoading: assetsLoading,
    error: assetsError,
  } = useListAssets(catalog, schema, {
    assetTypeFullName: selectedType,
  });

  const { data: typesData } = useListAssetTypes(catalog, schema);

  const handleCreateAsset = () => {
    navigate(`/assets/new?catalog=${catalog}&schema=${schema}`);
  };

  const handleCreateAssetType = () => {
    navigate(`/asset-types/new?catalog=${catalog}&schema=${schema}`);
  };

  const handleImport = () => {
    message.info('Import functionality coming soon');
  };

  const handleExport = () => {
    const exportData = {
      catalog,
      schema,
      assets: assetsData?.assets || [],
      assetTypes: typesData?.asset_types || [],
      exportedAt: new Date().toISOString(),
    };
    const blob = new Blob([JSON.stringify(exportData, null, 2)], {
      type: 'application/json',
    });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `${catalog}_${schema}_assets.json`;
    a.click();
  };

  // Filter assets based on search
  const filteredAssets = (assetsData?.assets || []).filter((asset) => {
    if (!searchText) return true;
    const searchLower = searchText.toLowerCase();
    return (
      asset.name?.toLowerCase().includes(searchLower) ||
      asset.full_name?.toLowerCase().includes(searchLower) ||
      asset.comment?.toLowerCase().includes(searchLower)
    );
  });

  // Table columns
  const columns = [
    {
      title: 'Name',
      dataIndex: 'name',
      key: 'name',
      render: (text: string, record: any) => (
        <Link to={`/assets/${encodeURIComponent(record.full_name)}`}>
          <Space>
            <SettingOutlined />
            <Text strong>{text}</Text>
          </Space>
        </Link>
      ),
    },
    {
      title: 'Type',
      dataIndex: 'asset_type_full_name',
      key: 'type',
      render: (type: string) => (
        <Tag color="blue">{type?.split('.').pop()}</Tag>
      ),
      filters: typesData?.asset_types?.map((t) => ({
        text: t.name!,
        value: t.full_name!,
      })),
      onFilter: (value: any, record: any) => record.asset_type_full_name === value,
    },
    {
      title: 'Parent',
      dataIndex: 'parent_asset_full_name',
      key: 'parent',
      render: (parent: string) =>
        parent ? (
          <Link to={`/assets/${encodeURIComponent(parent)}`}>
            {parent.split('.').pop()}
          </Link>
        ) : (
          <Text type="secondary">Root</Text>
        ),
    },
    {
      title: 'Properties',
      dataIndex: 'properties',
      key: 'properties',
      render: (props: any) => {
        const count = Object.keys(props || {}).length;
        return <Text type="secondary">{count} properties</Text>;
      },
    },
    {
      title: 'Comment',
      dataIndex: 'comment',
      key: 'comment',
      ellipsis: true,
    },
    {
      title: 'Created',
      dataIndex: 'created_at',
      key: 'created_at',
      render: (date: number) => new Date(date).toLocaleDateString(),
      sorter: (a: any, b: any) => a.created_at - b.created_at,
    },
  ];

  if (assetsLoading) {
    return (
      <div style={{ textAlign: 'center', padding: '50px' }}>
        <Spin size="large" />
      </div>
    );
  }

  if (assetsError) {
    return (
      <Alert
        message="Error Loading Assets"
        description="Failed to load assets. Please try again later."
        type="error"
        showIcon
      />
    );
  }

  const breadcrumbItems = [
    { title: <Link to="/">Catalogs</Link> },
    { title: <Link to={`/data/${catalog}`}>{catalog}</Link> },
    { title: <Link to={`/data/${catalog}/${schema}`}>{schema}</Link> },
    { title: 'Assets' },
  ];

  return (
    <div style={{ padding: '24px' }}>
      <Space direction="vertical" size="large" style={{ width: '100%' }}>
        {/* Header */}
        <div>
          <Breadcrumb items={breadcrumbItems} />

          <Row justify="space-between" align="middle" style={{ marginTop: '16px' }}>
            <Col>
              <Title level={2} style={{ margin: 0 }}>
                OT Assets
              </Title>
              <Text type="secondary">
                {catalog}.{schema} - {filteredAssets.length} assets
              </Text>
            </Col>
            <Col>
              <Space>
                <Tooltip title="Import Assets">
                  <Button icon={<UploadOutlined />} onClick={handleImport}>
                    Import
                  </Button>
                </Tooltip>
                <Tooltip title="Export Assets">
                  <Button icon={<DownloadOutlined />} onClick={handleExport}>
                    Export
                  </Button>
                </Tooltip>
                <Button onClick={handleCreateAssetType}>
                  New Asset Type
                </Button>
                <Button type="primary" icon={<PlusOutlined />} onClick={handleCreateAsset}>
                  New Asset
                </Button>
              </Space>
            </Col>
          </Row>
        </div>

        {/* Main Content */}
        <Card>
          <Tabs
            defaultActiveKey="tree"
            activeKey={viewMode}
            onChange={(key) => setViewMode(key as 'table' | 'tree')}
            tabBarExtraContent={
              <Space>
                <Search
                  placeholder="Search assets..."
                  prefix={<SearchOutlined />}
                  onChange={(e) => setSearchText(e.target.value)}
                  style={{ width: 200 }}
                  allowClear
                />
                <Select
                  placeholder="Filter by type"
                  allowClear
                  style={{ width: 200 }}
                  onChange={setSelectedType}
                >
                  {typesData?.asset_types?.map((type) => (
                    <Option key={type.full_name} value={type.full_name}>
                      {type.name}
                    </Option>
                  ))}
                </Select>
              </Space>
            }
          >
            <TabPane
              tab={
                <span>
                  <PartitionOutlined /> Tree View
                </span>
              }
              key="tree"
            >
              <AssetTreeBrowser catalog={catalog} schema={schema} />
            </TabPane>

            <TabPane
              tab={
                <span>
                  <TableOutlined /> Table View
                </span>
              }
              key="table"
            >
              <Table
                dataSource={filteredAssets}
                columns={columns}
                rowKey="full_name"
                pagination={{
                  pageSize: 20,
                  showSizeChanger: true,
                  showTotal: (total) => `Total ${total} assets`,
                }}
              />
            </TabPane>
          </Tabs>
        </Card>

        {/* Asset Types Summary */}
        <Card title="Asset Types" size="small">
          <Row gutter={16}>
            {typesData?.asset_types?.map((type) => {
              const count = filteredAssets.filter(
                (a) => a.asset_type_full_name === type.full_name
              ).length;
              return (
                <Col span={6} key={type.full_name}>
                  <Card size="small">
                    <Space direction="vertical">
                      <Space>
                        <ApiOutlined />
                        <Text strong>{type.name}</Text>
                      </Space>
                      <Text type="secondary">{count} assets</Text>
                      {type.comment && (
                        <Text type="secondary" ellipsis style={{ fontSize: '12px' }}>
                          {type.comment}
                        </Text>
                      )}
                    </Space>
                  </Card>
                </Col>
              );
            })}
          </Row>
        </Card>
      </Space>
    </div>
  );
};

export default AssetsList;