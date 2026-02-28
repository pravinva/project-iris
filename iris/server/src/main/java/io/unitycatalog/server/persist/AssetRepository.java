package io.unitycatalog.server.persist;

import com.fasterxml.jackson.core.JsonProcessingException;
import com.fasterxml.jackson.core.type.TypeReference;
import com.fasterxml.jackson.databind.ObjectMapper;
import io.unitycatalog.server.exception.BaseException;
import io.unitycatalog.server.exception.ErrorCode;
import io.unitycatalog.server.model.AssetInfo;
import io.unitycatalog.server.model.AssetList;
import io.unitycatalog.server.model.AssetPropertyBinding;
import io.unitycatalog.server.model.CreateAsset;
import io.unitycatalog.server.persist.dao.AssetDAO;
import io.unitycatalog.server.persist.dao.AssetTypeDAO;
import io.unitycatalog.server.utils.IdentityUtils;
import java.util.ArrayList;
import java.util.Date;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.Optional;
import java.util.UUID;
import java.util.stream.Collectors;
import org.hibernate.Session;
import org.hibernate.SessionFactory;
import org.hibernate.Transaction;
import org.hibernate.query.Query;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

/** Repository for Asset CRUD operations */
public class AssetRepository {
  private static final Logger LOGGER = LoggerFactory.getLogger(AssetRepository.class);
  private static final ObjectMapper OBJECT_MAPPER = new ObjectMapper();

  private final Repositories repositories;
  private final SessionFactory sessionFactory;

  public AssetRepository(Repositories repositories, SessionFactory sessionFactory) {
    this.repositories = repositories;
    this.sessionFactory = sessionFactory;
  }

  /** Create a new asset */
  public AssetInfo createAsset(CreateAsset createAsset) {
    LOGGER.debug(
        "Creating asset: {}.{}.{}",
        createAsset.getCatalogName(),
        createAsset.getSchemaName(),
        createAsset.getName());

    Session session = sessionFactory.openSession();
    Transaction transaction = null;
    try {
      transaction = session.beginTransaction();

      // Check if catalog and schema exist
      repositories
          .getSchemaRepository()
          .getSchema(createAsset.getCatalogName() + "." + createAsset.getSchemaName());

      // Check if asset already exists
      String fullName =
          String.format(
              "%s.%s.%s",
              createAsset.getCatalogName(), createAsset.getSchemaName(), createAsset.getName());

      Query<AssetDAO> query =
          session.createQuery(
              "FROM AssetDAO WHERE catalogName = :catalog AND schemaName = :schema AND name = :name",
              AssetDAO.class);
      query.setParameter("catalog", createAsset.getCatalogName());
      query.setParameter("schema", createAsset.getSchemaName());
      query.setParameter("name", createAsset.getName());

      if (query.uniqueResult() != null) {
        throw new BaseException(ErrorCode.ALREADY_EXISTS, "Asset already exists: " + fullName);
      }

      // Get the asset type
      AssetTypeDAO assetType = getAssetTypeDAO(session, createAsset.getAssetTypeFullName());

      // Get parent asset if specified
      AssetDAO parentAsset = null;
      if (createAsset.getParentAssetFullName() != null) {
        parentAsset = getAssetDAO(session, createAsset.getParentAssetFullName());

        // Validate parent asset is of same or compatible type
        if (!parentAsset.getAssetType().getId().equals(assetType.getId())) {
          LOGGER.warn(
              "Parent asset type {} differs from child asset type {}",
              parentAsset.getAssetTypeFullName(),
              assetType.getFullName());
        }
      }

      // Serialize properties to JSON
      String propertiesJson = null;
      if (createAsset.getProperties() != null) {
        try {
          propertiesJson = OBJECT_MAPPER.writeValueAsString(createAsset.getProperties());
        } catch (JsonProcessingException e) {
          LOGGER.error("Failed to serialize properties", e);
        }
      }

      // Property bindings will be null for now (not in CreateAsset model yet)
      String bindingsJson = null;

      // Create new asset
      AssetDAO dao =
          AssetDAO.builder()
              .id(UUID.randomUUID())
              .catalogName(createAsset.getCatalogName())
              .schemaName(createAsset.getSchemaName())
              .name(createAsset.getName())
              .assetType(assetType)
              .parentAsset(parentAsset)
              .comment(createAsset.getComment())
              .properties(propertiesJson)
              .propertyBindings(bindingsJson)
              .createdAt(new Date())
              .createdBy(IdentityUtils.findPrincipalEmailAddress())
              .build();

      session.persist(dao);
      transaction.commit();

      return toAssetInfo(dao);
    } catch (Exception e) {
      if (transaction != null) {
        transaction.rollback();
      }
      if (e instanceof BaseException) {
        throw (BaseException) e;
      }
      throw new BaseException(ErrorCode.INTERNAL, "Failed to create asset", e);
    } finally {
      session.close();
    }
  }

  /** Get an asset by full name */
  public AssetInfo getAsset(String fullName) {
    LOGGER.debug("Getting asset: {}", fullName);

    try (Session session = sessionFactory.openSession()) {
      AssetDAO dao = getAssetDAO(session, fullName);
      return toAssetInfo(dao);
    }
  }

  /** List assets in a schema with optional filters */
  public AssetList listAssets(
      String catalogName,
      String schemaName,
      Optional<String> assetTypeFullName,
      Optional<String> parentAssetFullName,
      Optional<Integer> maxResults,
      Optional<String> pageToken) {
    LOGGER.debug("Listing assets in {}.{}", catalogName, schemaName);

    try (Session session = sessionFactory.openSession()) {
      // Validate catalog and schema exist
      repositories.getSchemaRepository().getSchema(catalogName + "." + schemaName);

      // Build query with filters
      StringBuilder hql =
          new StringBuilder("FROM AssetDAO WHERE catalogName = :catalog AND schemaName = :schema");

      Map<String, Object> params = new HashMap<>();
      params.put("catalog", catalogName);
      params.put("schema", schemaName);

      if (assetTypeFullName.isPresent()) {
        AssetTypeDAO assetType = getAssetTypeDAO(session, assetTypeFullName.get());
        hql.append(" AND assetType = :assetType");
        params.put("assetType", assetType);
      }

      if (parentAssetFullName.isPresent()) {
        AssetDAO parentAsset = getAssetDAO(session, parentAssetFullName.get());
        hql.append(" AND parentAsset = :parentAsset");
        params.put("parentAsset", parentAsset);
      }

      hql.append(" ORDER BY name");

      Query<AssetDAO> query = session.createQuery(hql.toString(), AssetDAO.class);
      params.forEach(query::setParameter);

      // Apply pagination
      int limit = maxResults.orElse(100);
      if (pageToken.isPresent()) {
        query.setFirstResult(Integer.parseInt(pageToken.get()));
      }
      query.setMaxResults(limit);

      List<AssetDAO> results = query.list();
      List<AssetInfo> assets = results.stream().map(this::toAssetInfo).collect(Collectors.toList());

      String nextPageToken = null;
      if (results.size() == limit) {
        int nextOffset = pageToken.map(Integer::parseInt).orElse(0) + limit;
        nextPageToken = String.valueOf(nextOffset);
      }

      return new AssetList().assets(assets).nextPageToken(nextPageToken);
    }
  }

  /** List child assets of a parent asset */
  public AssetList listChildAssets(
      String parentFullName, Optional<Integer> maxResults, Optional<String> pageToken) {
    LOGGER.debug("Listing child assets of: {}", parentFullName);

    try (Session session = sessionFactory.openSession()) {
      AssetDAO parentAsset = getAssetDAO(session, parentFullName);

      Query<AssetDAO> query =
          session.createQuery(
              "FROM AssetDAO WHERE parentAsset = :parent ORDER BY name", AssetDAO.class);
      query.setParameter("parent", parentAsset);

      // Apply pagination
      int limit = maxResults.orElse(100);
      if (pageToken.isPresent()) {
        query.setFirstResult(Integer.parseInt(pageToken.get()));
      }
      query.setMaxResults(limit);

      List<AssetDAO> results = query.list();
      List<AssetInfo> assets = results.stream().map(this::toAssetInfo).collect(Collectors.toList());

      String nextPageToken = null;
      if (results.size() == limit) {
        int nextOffset = pageToken.map(Integer::parseInt).orElse(0) + limit;
        nextPageToken = String.valueOf(nextOffset);
      }

      return new AssetList().assets(assets).nextPageToken(nextPageToken);
    }
  }

  /** Delete an asset and all its children */
  public void deleteAsset(String fullName) {
    LOGGER.debug("Deleting asset: {}", fullName);

    Session session = sessionFactory.openSession();
    Transaction transaction = null;
    try {
      transaction = session.beginTransaction();

      AssetDAO dao = getAssetDAO(session, fullName);

      // Recursively delete all children first
      deleteAssetAndChildren(session, dao);

      transaction.commit();
    } catch (Exception e) {
      if (transaction != null) {
        transaction.rollback();
      }
      if (e instanceof BaseException) {
        throw (BaseException) e;
      }
      throw new BaseException(ErrorCode.INTERNAL, "Failed to delete asset", e);
    } finally {
      session.close();
    }
  }

  /** Recursively delete an asset and all its children */
  private void deleteAssetAndChildren(Session session, AssetDAO asset) {
    // First delete all children recursively
    if (asset.getChildAssets() != null && !asset.getChildAssets().isEmpty()) {
      for (AssetDAO child : new ArrayList<>(asset.getChildAssets())) {
        deleteAssetAndChildren(session, child);
      }
    }

    // Then delete the asset itself
    session.remove(asset);
  }

  /** Get asset DAO by full name */
  private AssetDAO getAssetDAO(Session session, String fullName) {
    String[] parts = fullName.split("\\.");
    if (parts.length != 3) {
      throw new BaseException(
          ErrorCode.INVALID_ARGUMENT,
          "Invalid asset full name format. Expected: catalog.schema.name");
    }

    Query<AssetDAO> query =
        session.createQuery(
            "FROM AssetDAO WHERE catalogName = :catalog AND schemaName = :schema AND name = :name",
            AssetDAO.class);
    query.setParameter("catalog", parts[0]);
    query.setParameter("schema", parts[1]);
    query.setParameter("name", parts[2]);

    AssetDAO dao = query.uniqueResult();
    if (dao == null) {
      throw new BaseException(ErrorCode.NOT_FOUND, "Asset not found: " + fullName);
    }

    return dao;
  }

  /** Get asset type DAO by full name */
  private AssetTypeDAO getAssetTypeDAO(Session session, String fullName) {
    String[] parts = fullName.split("\\.");
    if (parts.length != 3) {
      throw new BaseException(
          ErrorCode.INVALID_ARGUMENT,
          "Invalid asset type full name format. Expected: catalog.schema.name");
    }

    Query<AssetTypeDAO> query =
        session.createQuery(
            "FROM AssetTypeDAO WHERE catalogName = :catalog AND schemaName = :schema AND name = :name",
            AssetTypeDAO.class);
    query.setParameter("catalog", parts[0]);
    query.setParameter("schema", parts[1]);
    query.setParameter("name", parts[2]);

    AssetTypeDAO dao = query.uniqueResult();
    if (dao == null) {
      throw new BaseException(ErrorCode.NOT_FOUND, "Asset type not found: " + fullName);
    }

    return dao;
  }

  /** Convert DAO to model object */
  private AssetInfo toAssetInfo(AssetDAO dao) {
    // Deserialize properties from JSON string
    Map<String, String> properties = null;
    if (dao.getProperties() != null) {
      try {
        properties =
            OBJECT_MAPPER.readValue(
                dao.getProperties(), new TypeReference<Map<String, String>>() {});
      } catch (JsonProcessingException e) {
        LOGGER.error("Failed to deserialize properties", e);
      }
    }

    // Deserialize property bindings from JSON string
    List<AssetPropertyBinding> propertyBindings = null;
    if (dao.getPropertyBindings() != null) {
      try {
        propertyBindings =
            OBJECT_MAPPER.readValue(
                dao.getPropertyBindings(),
                OBJECT_MAPPER
                    .getTypeFactory()
                    .constructCollectionType(List.class, AssetPropertyBinding.class));
      } catch (JsonProcessingException e) {
        LOGGER.error("Failed to deserialize property bindings", e);
      }
    }

    return new AssetInfo()
        .catalogName(dao.getCatalogName())
        .schemaName(dao.getSchemaName())
        .name(dao.getName())
        .fullName(dao.getFullName())
        .assetTypeFullName(dao.getAssetTypeFullName())
        .parentAssetFullName(dao.getParentAssetFullName())
        .comment(dao.getComment())
        .properties(properties)
        .propertyBindings(propertyBindings)
        .owner(dao.getOwner())
        .createdAt(dao.getCreatedAt() != null ? dao.getCreatedAt().getTime() : null)
        .createdBy(dao.getCreatedBy())
        .updatedAt(dao.getUpdatedAt() != null ? dao.getUpdatedAt().getTime() : null)
        .updatedBy(dao.getUpdatedBy());
  }
}
