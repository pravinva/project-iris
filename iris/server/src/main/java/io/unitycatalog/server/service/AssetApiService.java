package io.unitycatalog.server.service;

import com.linecorp.armeria.common.HttpResponse;
import com.linecorp.armeria.common.HttpStatus;
import com.linecorp.armeria.server.annotation.Delete;
import com.linecorp.armeria.server.annotation.ExceptionHandler;
import com.linecorp.armeria.server.annotation.Get;
import com.linecorp.armeria.server.annotation.Param;
import com.linecorp.armeria.server.annotation.Post;
import io.unitycatalog.server.exception.GlobalExceptionHandler;
import io.unitycatalog.server.model.AssetInfo;
import io.unitycatalog.server.model.AssetList;
import io.unitycatalog.server.model.AssetTypeInfo;
import io.unitycatalog.server.model.AssetTypeList;
import io.unitycatalog.server.model.CreateAsset;
import io.unitycatalog.server.model.CreateAssetType;
import java.util.Optional;

/** REST API implementation for Asset and AssetType operations */
@ExceptionHandler(GlobalExceptionHandler.class)
public class AssetApiService {

  private final AssetService assetService;

  public AssetApiService() {
    this.assetService = AssetService.getInstance();
  }

  // ==================== AssetType Endpoints ====================

  @Post("")
  public AssetTypeInfo createAssetType(CreateAssetType createAssetType) {
    return assetService.createAssetType(createAssetType);
  }

  @Get("/{full_name}")
  public AssetTypeInfo getAssetType(@Param("full_name") String fullName) {
    return assetService.getAssetType(fullName);
  }

  @Get("")
  public AssetTypeList listAssetTypes(
      @Param("catalog_name") String catalogName,
      @Param("schema_name") String schemaName,
      @Param("max_results") Optional<Integer> maxResults,
      @Param("page_token") Optional<String> pageToken) {
    return assetService.listAssetTypes(
        catalogName, schemaName, maxResults.orElse(null), pageToken.orElse(null));
  }

  @Delete("/{full_name}")
  public HttpResponse deleteAssetType(@Param("full_name") String fullName) {
    assetService.deleteAssetType(fullName);
    return HttpResponse.of(HttpStatus.NO_CONTENT);
  }

  // ==================== Asset Endpoints ====================

  @Post("")
  public AssetInfo createAsset(CreateAsset createAsset) {
    return assetService.createAsset(createAsset);
  }

  @Get("/{full_name}")
  public AssetInfo getAsset(@Param("full_name") String fullName) {
    return assetService.getAsset(fullName);
  }

  @Get("")
  public AssetList listAssets(
      @Param("catalog_name") String catalogName,
      @Param("schema_name") String schemaName,
      @Param("asset_type_full_name") Optional<String> assetTypeFullName,
      @Param("parent_asset_full_name") Optional<String> parentAssetFullName,
      @Param("max_results") Optional<Integer> maxResults,
      @Param("page_token") Optional<String> pageToken) {
    return assetService.listAssets(
        catalogName,
        schemaName,
        assetTypeFullName.orElse(null),
        parentAssetFullName.orElse(null),
        maxResults.orElse(null),
        pageToken.orElse(null));
  }

  @Get("/{full_name}/children")
  public AssetList listChildAssets(
      @Param("full_name") String fullName,
      @Param("max_results") Optional<Integer> maxResults,
      @Param("page_token") Optional<String> pageToken) {
    return assetService.listChildAssets(fullName, maxResults.orElse(null), pageToken.orElse(null));
  }

  @Delete("/{full_name}")
  public HttpResponse deleteAsset(@Param("full_name") String fullName) {
    assetService.deleteAsset(fullName);
    return HttpResponse.of(HttpStatus.NO_CONTENT);
  }
}
