/**
 * Asset Details Page
 *
 * Displays detailed information about a specific OT asset including
 * properties, hierarchy, and relationships.
 */

import React, { useState } from 'react';
import {
  Card,
  Descriptions,
  Space,
  Typography,
  Button,
  Tag,
  Table,
  Breadcrumb,
  Spin,
  Alert,
  Row,
  Col,
  Tabs,
  Empty,
  Tooltip,
  message,
  Modal,
} from 'antd';
import {
  ArrowLeftOutlined,
  EditOutlined,
  DeleteOutlined,
  SettingOutlined,
  ApiOutlined,
  InfoCircleOutlined,
  FolderOutlined,
  DownloadOutlined,
} from '@ant-design/icons';
import { useParams, useNavigate, Link } from 'react-router-dom';
import { useGetAsset, useDeleteAsset, useListChildAssets } from '../hooks/assets';
import AssetTreeBrowser from '../components/AssetTreeBrowser';

const { Title, Text, Paragraph } = Typography;
const { TabPane } = Tabs;

const AssetDetails: React.FC = () => {
  const { fullName } = useParams<{ fullName: string }>();
  const navigate = useNavigate();
  const [deleteModalVisible, setDeleteModalVisible] = useState(false);

  const decodedFullName = fullName ? decodeURIComponent(fullName) : '';
  const [catalog, schema, name] = decodedFullName.split('.');

  const { data: asset, isLoading, error } = useGetAsset(decodedFullName);
  const { data: children } = useListChildAssets(decodedFullName);
  const deleteAssetMutation = useDeleteAsset();

  const handleEdit = () => {
    navigate(`/assets/${fullName}/edit`);
  };

  const handleDelete = async () => {
    try {
      await deleteAssetMutation.mutateAsync({
        fullName: decodedFullName,
        parentFullName: asset?.parent_asset_full_name,
      });
      message.success('Asset deleted successfully');
      if (asset?.parent_asset_full_name) {
        navigate(`/assets/${encodeURIComponent(asset.parent_asset_full_name)}`);
      } else {
        navigate(`/data/${catalog}/${schema}`);
      }
    } catch (error) {
      message.error('Failed to delete asset');
      console.error('Delete error:', error);
    }
  };

  const exportAsset = () => {
    const exportData = {
      asset,
      children: children?.assets || [],
      exportedAt: new Date().toISOString(),
    };
    const blob = new Blob([JSON.stringify(exportData, null, 2)], {
      type: 'application/json',
    });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `${name}_asset.json`;
    a.click();
  };

  if (isLoading) {
    return (
      <div style={{ textAlign: 'center', padding: '50px' }}>
        <Spin size="large" />
      </div>
    );
  }

  if (error || !asset) {
    return (
      <Alert
        message="Asset Not Found"
        description={`The asset "${decodedFullName}" could not be found.`}
        type="error"
        showIcon
        action={
          <Button onClick={() => navigate(-1)}>Go Back</Button>
        }
      />
    );
  }

  // Build breadcrumb
  const breadcrumbItems = [
    { title: <Link to="/">Catalogs</Link> },
    { title: <Link to={`/data/${catalog}`}>{catalog}</Link> },
    { title: <Link to={`/data/${catalog}/${schema}`}>{schema}</Link> },
  ];

  // Add parent assets to breadcrumb if they exist
  if (asset.parent_asset_full_name) {
    const parentParts = asset.parent_asset_full_name.split('.');
    breadcrumbItems.push({
      title: (
        <Link to={`/assets/${encodeURIComponent(asset.parent_asset_full_name)}`}>
          {parentParts[parentParts.length - 1]}
        </Link>
      ),
    });
  }

  breadcrumbItems.push({ title: <>{name}</> });

  // Property columns for the table
  const propertyColumns = [
    {
      title: 'Property',
      dataIndex: 'key',
      key: 'key',
      render: (text: string) => <Text strong>{text}</Text>,
    },
    {
      title: 'Value',
      dataIndex: 'value',
      key: 'value',
      render: (value: any) => {
        if (typeof value === 'object') {
          return <Text code>{JSON.stringify(value)}</Text>;
        }
        return <Text>{value}</Text>;
      },
    },
  ];

  const propertyData = Object.entries(asset.properties || {}).map(([key, value]) => ({
    key,
    value,
  }));

  // Child assets columns
  const childColumns = [
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
  ];

  return (
    <>
      <div style={{ padding: '24px' }}>
        <Space direction="vertical" size="large" style={{ width: '100%' }}>
          {/* Header */}
          <div>
            <Button
              icon={<ArrowLeftOutlined />}
              onClick={() => navigate(-1)}
              style={{ marginBottom: '16px' }}
            >
              Back
            </Button>

            <Breadcrumb items={breadcrumbItems} />
          </div>

          {/* Asset Info Card */}
          <Card
            title={
              <Space style={{ width: '100%', justifyContent: 'space-between' }}>
                <Space>
                  <ApiOutlined style={{ fontSize: '24px' }} />
                  <Title level={3} style={{ margin: 0 }}>
                    {asset.name}
                  </Title>
                  <Tag color="blue">{asset.asset_type_full_name?.split('.').pop()}</Tag>
                </Space>
                <Space>
                  <Tooltip title="Export Asset">
                    <Button icon={<DownloadOutlined />} onClick={exportAsset}>
                      Export
                    </Button>
                  </Tooltip>
                  <Button icon={<EditOutlined />} onClick={handleEdit}>
                    Edit
                  </Button>
                  <Button
                    danger
                    icon={<DeleteOutlined />}
                    onClick={() => setDeleteModalVisible(true)}
                  >
                    Delete
                  </Button>
                </Space>
              </Space>
            }
          >
            <Tabs defaultActiveKey="overview">
              <TabPane tab="Overview" key="overview">
                <Descriptions column={2} bordered>
                  <Descriptions.Item label="Full Name" span={2}>
                    <Text code copyable>
                      {asset.full_name}
                    </Text>
                  </Descriptions.Item>

                  <Descriptions.Item label="Asset Type">
                    <Tag color="cyan">{asset.asset_type_full_name}</Tag>
                  </Descriptions.Item>

                  <Descriptions.Item label="Parent Asset">
                    {asset.parent_asset_full_name ? (
                      <Link to={`/assets/${encodeURIComponent(asset.parent_asset_full_name)}`}>
                        {asset.parent_asset_full_name}
                      </Link>
                    ) : (
                      <Text type="secondary">None (Root Asset)</Text>
                    )}
                  </Descriptions.Item>

                  <Descriptions.Item label="Created At">
                    {new Date(asset.created_at!).toLocaleString()}
                  </Descriptions.Item>

                  <Descriptions.Item label="Created By">
                    {asset.created_by || 'System'}
                  </Descriptions.Item>

                  {asset.comment && (
                    <Descriptions.Item label="Description" span={2}>
                      <Paragraph>{asset.comment}</Paragraph>
                    </Descriptions.Item>
                  )}

                  <Descriptions.Item label="Owner">
                    {asset.owner || 'Not specified'}
                  </Descriptions.Item>

                  <Descriptions.Item label="Child Assets">
                    {children?.assets?.length || 0} assets
                  </Descriptions.Item>
                </Descriptions>
              </TabPane>

              <TabPane tab={`Properties (${propertyData.length})`} key="properties">
                {propertyData.length > 0 ? (
                  <Table
                    dataSource={propertyData}
                    columns={propertyColumns}
                    pagination={false}
                    size="middle"
                  />
                ) : (
                  <Empty description="No properties defined for this asset" />
                )}
              </TabPane>

              <TabPane tab={`Children (${children?.assets?.length || 0})`} key="children">
                {children?.assets && children.assets.length > 0 ? (
                  <Table
                    dataSource={children.assets}
                    columns={childColumns}
                    rowKey="full_name"
                    pagination={false}
                    size="middle"
                  />
                ) : (
                  <Empty description="This asset has no child assets" />
                )}
              </TabPane>

              <TabPane tab="Hierarchy" key="hierarchy">
                <Row gutter={24}>
                  <Col span={24}>
                    <Card title="Asset Hierarchy View" size="small">
                      <AssetTreeBrowser
                        catalog={catalog}
                        schema={schema}
                        selectedAsset={asset.full_name}
                      />
                    </Card>
                  </Col>
                </Row>
              </TabPane>
            </Tabs>
          </Card>
        </Space>
      </div>

      {/* Delete Confirmation Modal */}
      <Modal
        title="Delete Asset"
        open={deleteModalVisible}
        onOk={handleDelete}
        onCancel={() => setDeleteModalVisible(false)}
        okText="Delete"
        okButtonProps={{ danger: true }}
        confirmLoading={deleteAssetMutation.isPending}
      >
        <Alert
          message="Warning"
          description={
            <>
              Are you sure you want to delete the asset <Text strong>{asset.name}</Text>?
              {children?.assets && children.assets.length > 0 && (
                <div style={{ marginTop: '8px' }}>
                  <Text type="danger">
                    This will also delete {children.assets.length} child asset(s).
                  </Text>
                </div>
              )}
              <div style={{ marginTop: '8px' }}>
                This action cannot be undone.
              </div>
            </>
          }
          type="warning"
          showIcon
        />
      </Modal>
    </>
  );
};

export default AssetDetails;