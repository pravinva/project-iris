# AssetInfo
## Properties

| Name | Type | Description | Notes |
|------------ | ------------- | ------------- | -------------|
| **catalog\_name** | **String** | The name of the catalog where the asset is | [default to null] |
| **schema\_name** | **String** | The name of the schema where the asset is | [default to null] |
| **name** | **String** | The name of the asset | [default to null] |
| **full\_name** | **String** | Full name of the asset (catalog.schema.name) | [default to null] |
| **asset\_type\_full\_name** | **String** | Full name of the asset type this asset belongs to | [default to null] |
| **parent\_asset\_full\_name** | **String** | Full name of the parent asset (if this is a child asset) | [optional] [default to null] |
| **comment** | **String** | The comment attached to the asset | [optional] [default to null] |
| **properties** | **Map** | Key-value properties of the asset | [optional] [default to null] |
| **property\_bindings** | [**List**](AssetPropertyBinding.md) | List of property bindings for this asset | [optional] [default to null] |
| **created\_at** | **Long** | Time at which this asset was created, in epoch milliseconds | [optional] [default to null] |
| **created\_by** | **String** | The identifier of the user who created the asset | [optional] [default to null] |
| **updated\_at** | **Long** | Time at which this asset was last modified, in epoch milliseconds | [optional] [default to null] |
| **updated\_by** | **String** | The identifier of the user who updated the asset last time | [optional] [default to null] |
| **owner** | **String** | The identifier of the user who owns the asset | [optional] [default to null] |

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)

