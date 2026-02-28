# AssetsApi

All URIs are relative to *http://localhost:8080/api/2.1/unity-catalog*

| Method | HTTP request | Description |
|------------- | ------------- | -------------|
| [**createAsset**](AssetsApi.md#createAsset) | **POST** /unity-catalog/assets | Create an asset |
| [**createAssetType**](AssetsApi.md#createAssetType) | **POST** /unity-catalog/asset-types | Create an asset type |
| [**deleteAsset**](AssetsApi.md#deleteAsset) | **DELETE** /unity-catalog/assets/{full_name} | Delete an asset |
| [**deleteAssetType**](AssetsApi.md#deleteAssetType) | **DELETE** /unity-catalog/asset-types/{full_name} | Delete an asset type |
| [**getAsset**](AssetsApi.md#getAsset) | **GET** /unity-catalog/assets/{full_name} | Get an asset |
| [**getAssetType**](AssetsApi.md#getAssetType) | **GET** /unity-catalog/asset-types/{full_name} | Get an asset type |
| [**listAssetTypes**](AssetsApi.md#listAssetTypes) | **GET** /unity-catalog/asset-types | List asset types |
| [**listAssets**](AssetsApi.md#listAssets) | **GET** /unity-catalog/assets | List assets |
| [**listChildAssets**](AssetsApi.md#listChildAssets) | **GET** /unity-catalog/assets/{full_name}/children | List child assets |


<a name="createAsset"></a>
# **createAsset**
> AssetInfo createAsset(CreateAsset)

Create an asset

    Creates a new asset

### Parameters

|Name | Type | Description  | Notes |
|------------- | ------------- | ------------- | -------------|
| **CreateAsset** | [**CreateAsset**](../Models/CreateAsset.md)|  | |

### Return type

[**AssetInfo**](../Models/AssetInfo.md)

### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: application/json
- **Accept**: application/json

<a name="createAssetType"></a>
# **createAssetType**
> AssetTypeInfo createAssetType(CreateAssetType)

Create an asset type

    Creates a new asset type.

### Parameters

|Name | Type | Description  | Notes |
|------------- | ------------- | ------------- | -------------|
| **CreateAssetType** | [**CreateAssetType**](../Models/CreateAssetType.md)|  | |

### Return type

[**AssetTypeInfo**](../Models/AssetTypeInfo.md)

### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: application/json
- **Accept**: application/json

<a name="deleteAsset"></a>
# **deleteAsset**
> deleteAsset(full\_name)

Delete an asset

    Deletes an asset by its full name

### Parameters

|Name | Type | Description  | Notes |
|------------- | ------------- | ------------- | -------------|
| **full\_name** | **String**| Full name of the asset | [default to null] |

### Return type

null (empty response body)

### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: Not defined

<a name="deleteAssetType"></a>
# **deleteAssetType**
> deleteAssetType(full\_name)

Delete an asset type

    Deletes an asset type by its full name

### Parameters

|Name | Type | Description  | Notes |
|------------- | ------------- | ------------- | -------------|
| **full\_name** | **String**| Full name of the asset type | [default to null] |

### Return type

null (empty response body)

### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: Not defined

<a name="getAsset"></a>
# **getAsset**
> AssetInfo getAsset(full\_name)

Get an asset

    Gets an asset by its full name

### Parameters

|Name | Type | Description  | Notes |
|------------- | ------------- | ------------- | -------------|
| **full\_name** | **String**| Full name of the asset | [default to null] |

### Return type

[**AssetInfo**](../Models/AssetInfo.md)

### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json

<a name="getAssetType"></a>
# **getAssetType**
> AssetTypeInfo getAssetType(full\_name)

Get an asset type

    Gets an asset type by its full name

### Parameters

|Name | Type | Description  | Notes |
|------------- | ------------- | ------------- | -------------|
| **full\_name** | **String**| Full name of the asset type | [default to null] |

### Return type

[**AssetTypeInfo**](../Models/AssetTypeInfo.md)

### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json

<a name="listAssetTypes"></a>
# **listAssetTypes**
> AssetTypeList listAssetTypes(catalog\_name, schema\_name, max\_results, page\_token)

List asset types

    Gets an array of asset types in the given parent catalog and schema.

### Parameters

|Name | Type | Description  | Notes |
|------------- | ------------- | ------------- | -------------|
| **catalog\_name** | **String**| The name of the catalog | [default to null] |
| **schema\_name** | **String**| The name of the schema | [default to null] |
| **max\_results** | **Integer**| Maximum number of asset types to return | [optional] [default to null] |
| **page\_token** | **String**| Opaque pagination token to go to next page | [optional] [default to null] |

### Return type

[**AssetTypeList**](../Models/AssetTypeList.md)

### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json

<a name="listAssets"></a>
# **listAssets**
> AssetList listAssets(catalog\_name, schema\_name, asset\_type\_full\_name, parent\_asset\_full\_name, max\_results, page\_token)

List assets

    Gets an array of assets

### Parameters

|Name | Type | Description  | Notes |
|------------- | ------------- | ------------- | -------------|
| **catalog\_name** | **String**| The name of the catalog | [default to null] |
| **schema\_name** | **String**| The name of the schema | [default to null] |
| **asset\_type\_full\_name** | **String**| Filter by asset type full name | [optional] [default to null] |
| **parent\_asset\_full\_name** | **String**| Filter by parent asset full name (for children) | [optional] [default to null] |
| **max\_results** | **Integer**| Maximum number of assets to return | [optional] [default to null] |
| **page\_token** | **String**| Opaque pagination token to go to next page | [optional] [default to null] |

### Return type

[**AssetList**](../Models/AssetList.md)

### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json

<a name="listChildAssets"></a>
# **listChildAssets**
> AssetList listChildAssets(full\_name, max\_results, page\_token)

List child assets

    Lists all child assets of a given parent asset

### Parameters

|Name | Type | Description  | Notes |
|------------- | ------------- | ------------- | -------------|
| **full\_name** | **String**| Full name of the parent asset | [default to null] |
| **max\_results** | **Integer**| Maximum number of child assets to return | [optional] [default to null] |
| **page\_token** | **String**| Opaque pagination token to go to next page | [optional] [default to null] |

### Return type

[**AssetList**](../Models/AssetList.md)

### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json

