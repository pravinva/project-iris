package io.unitycatalog.server.service;

import io.unitycatalog.server.exception.BaseException;
import io.unitycatalog.server.exception.ErrorCode;
import io.unitycatalog.server.model.AssetInfo;
import io.unitycatalog.server.model.AssetList;
import io.unitycatalog.server.model.AssetPropertyDef;
import io.unitycatalog.server.model.AssetTypeInfo;
import io.unitycatalog.server.model.AssetTypeList;
import io.unitycatalog.server.model.CreateAsset;
import io.unitycatalog.server.model.CreateAssetType;
import io.unitycatalog.server.persist.AssetRepository;
import io.unitycatalog.server.persist.AssetTypeRepository;
import io.unitycatalog.server.persist.Repositories;
import io.unitycatalog.server.persist.utils.HibernateConfigurator;
import io.unitycatalog.server.utils.ServerProperties;
import java.util.Optional;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

/**
 * Service layer for Asset and AssetType operations Handles business logic and validation for Asset
 * management
 */
public class AssetService {
  private static final Logger LOGGER = LoggerFactory.getLogger(AssetService.class);
  private static AssetService INSTANCE;

  private final AssetRepository assetRepository;
  private final AssetTypeRepository assetTypeRepository;

  private AssetService(Repositories repositories) {
    this.assetRepository = repositories.getAssetRepository();
    this.assetTypeRepository = repositories.getAssetTypeRepository();
  }

  public static synchronized AssetService getInstance() {
    if (INSTANCE == null) {
      // Initialize with default server properties and repositories
      ServerProperties serverProperties = new ServerProperties();
      HibernateConfigurator hibernateConfigurator = new HibernateConfigurator(serverProperties);
      Repositories repositories =
          new Repositories(hibernateConfigurator.getSessionFactory(), serverProperties);
      INSTANCE = new AssetService(repositories);
    }
    return INSTANCE;
  }

  // ==================== AssetType Operations ====================

  /** Create a new asset type */
  public AssetTypeInfo createAssetType(CreateAssetType createAssetType) {
    LOGGER.info(
        "Creating asset type: {}.{}.{}",
        createAssetType.getCatalogName(),
        createAssetType.getSchemaName(),
        createAssetType.getName());

    // Validate input
    validateAssetTypeName(createAssetType.getName());
    validateCatalogName(createAssetType.getCatalogName());
    validateSchemaName(createAssetType.getSchemaName());

    // Validate property definitions if provided
    if (createAssetType.getProperties() != null) {
      for (AssetPropertyDef prop : createAssetType.getProperties()) {
        validatePropertyDef(prop);
      }
    }

    return assetTypeRepository.createAssetType(createAssetType);
  }

  /** Get an asset type by full name */
  public AssetTypeInfo getAssetType(String fullName) {
    LOGGER.info("Getting asset type: {}", fullName);
    validateFullName(fullName);
    return assetTypeRepository.getAssetType(fullName);
  }

  /** List asset types in a schema */
  public AssetTypeList listAssetTypes(
      String catalogName, String schemaName, Integer maxResults, String pageToken) {
    LOGGER.info("Listing asset types in {}.{}", catalogName, schemaName);
    validateCatalogName(catalogName);
    validateSchemaName(schemaName);

    return assetTypeRepository.listAssetTypes(
        catalogName, schemaName, Optional.ofNullable(maxResults), Optional.ofNullable(pageToken));
  }

  /** Delete an asset type */
  public void deleteAssetType(String fullName) {
    LOGGER.info("Deleting asset type: {}", fullName);
    validateFullName(fullName);
    assetTypeRepository.deleteAssetType(fullName);
  }

  // ==================== Asset Operations ====================

  /** Create a new asset */
  public AssetInfo createAsset(CreateAsset createAsset) {
    LOGGER.info(
        "Creating asset: {}.{}.{}",
        createAsset.getCatalogName(),
        createAsset.getSchemaName(),
        createAsset.getName());

    // Validate input
    validateAssetName(createAsset.getName());
    validateCatalogName(createAsset.getCatalogName());
    validateSchemaName(createAsset.getSchemaName());
    validateFullName(createAsset.getAssetTypeFullName());

    // Validate parent asset if specified
    if (createAsset.getParentAssetFullName() != null) {
      validateFullName(createAsset.getParentAssetFullName());
    }

    return assetRepository.createAsset(createAsset);
  }

  /** Get an asset by full name */
  public AssetInfo getAsset(String fullName) {
    LOGGER.info("Getting asset: {}", fullName);
    validateFullName(fullName);
    return assetRepository.getAsset(fullName);
  }

  /** List assets in a schema */
  public AssetList listAssets(
      String catalogName,
      String schemaName,
      String assetTypeFullName,
      String parentAssetFullName,
      Integer maxResults,
      String pageToken) {
    LOGGER.info("Listing assets in {}.{}", catalogName, schemaName);
    validateCatalogName(catalogName);
    validateSchemaName(schemaName);

    if (assetTypeFullName != null) {
      validateFullName(assetTypeFullName);
    }
    if (parentAssetFullName != null) {
      validateFullName(parentAssetFullName);
    }

    return assetRepository.listAssets(
        catalogName,
        schemaName,
        Optional.ofNullable(assetTypeFullName),
        Optional.ofNullable(parentAssetFullName),
        Optional.ofNullable(maxResults),
        Optional.ofNullable(pageToken));
  }

  /** List child assets of a parent asset */
  public AssetList listChildAssets(String parentFullName, Integer maxResults, String pageToken) {
    LOGGER.info("Listing child assets of: {}", parentFullName);
    validateFullName(parentFullName);

    return assetRepository.listChildAssets(
        parentFullName, Optional.ofNullable(maxResults), Optional.ofNullable(pageToken));
  }

  /** Delete an asset */
  public void deleteAsset(String fullName) {
    LOGGER.info("Deleting asset: {}", fullName);
    validateFullName(fullName);
    assetRepository.deleteAsset(fullName);
  }

  // ==================== Validation Methods ====================

  private void validateAssetTypeName(String name) {
    if (name == null || name.isEmpty()) {
      throw new BaseException(ErrorCode.INVALID_ARGUMENT, "Asset type name cannot be empty");
    }
    if (!name.matches("^[a-zA-Z0-9_-]+$")) {
      throw new BaseException(
          ErrorCode.INVALID_ARGUMENT,
          "Asset type name must contain only alphanumeric characters, underscores, and hyphens");
    }
  }

  private void validateAssetName(String name) {
    if (name == null || name.isEmpty()) {
      throw new BaseException(ErrorCode.INVALID_ARGUMENT, "Asset name cannot be empty");
    }
    if (!name.matches("^[a-zA-Z0-9_-]+$")) {
      throw new BaseException(
          ErrorCode.INVALID_ARGUMENT,
          "Asset name must contain only alphanumeric characters, underscores, and hyphens");
    }
  }

  private void validateCatalogName(String name) {
    if (name == null || name.isEmpty()) {
      throw new BaseException(ErrorCode.INVALID_ARGUMENT, "Catalog name cannot be empty");
    }
  }

  private void validateSchemaName(String name) {
    if (name == null || name.isEmpty()) {
      throw new BaseException(ErrorCode.INVALID_ARGUMENT, "Schema name cannot be empty");
    }
  }

  private void validateFullName(String fullName) {
    if (fullName == null || fullName.isEmpty()) {
      throw new BaseException(ErrorCode.INVALID_ARGUMENT, "Full name cannot be empty");
    }
    String[] parts = fullName.split("\\.");
    if (parts.length != 3) {
      throw new BaseException(
          ErrorCode.INVALID_ARGUMENT, "Full name must be in the format: catalog.schema.name");
    }
  }

  private void validatePropertyDef(AssetPropertyDef propertyDef) {
    if (propertyDef.getName() == null || propertyDef.getName().isEmpty()) {
      throw new BaseException(ErrorCode.INVALID_ARGUMENT, "Property name cannot be empty");
    }
    if (propertyDef.getDataType() == null || propertyDef.getDataType().isEmpty()) {
      throw new BaseException(ErrorCode.INVALID_ARGUMENT, "Property data type cannot be empty");
    }
    // Validate data type is one of the supported types
    String dataType = propertyDef.getDataType().toUpperCase();
    if (!dataType.matches("^(STRING|INTEGER|FLOAT|DOUBLE|BOOLEAN|TIMESTAMP)$")) {
      throw new BaseException(
          ErrorCode.INVALID_ARGUMENT,
          "Property data type must be one of: STRING, INTEGER, FLOAT, DOUBLE, BOOLEAN, TIMESTAMP");
    }
  }
}
