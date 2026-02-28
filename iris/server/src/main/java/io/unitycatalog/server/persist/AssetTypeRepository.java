package io.unitycatalog.server.persist;

import com.fasterxml.jackson.core.JsonProcessingException;
import com.fasterxml.jackson.databind.ObjectMapper;
import io.unitycatalog.server.exception.BaseException;
import io.unitycatalog.server.exception.ErrorCode;
import io.unitycatalog.server.model.AssetPropertyDef;
import io.unitycatalog.server.model.AssetTypeInfo;
import io.unitycatalog.server.model.AssetTypeList;
import io.unitycatalog.server.model.CreateAssetType;
import io.unitycatalog.server.persist.dao.AssetTypeDAO;
import io.unitycatalog.server.utils.IdentityUtils;
import java.util.Date;
import java.util.List;
import java.util.Optional;
import java.util.UUID;
import java.util.stream.Collectors;
import org.hibernate.Session;
import org.hibernate.SessionFactory;
import org.hibernate.Transaction;
import org.hibernate.query.Query;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

/** Repository for AssetType CRUD operations */
public class AssetTypeRepository {
  private static final Logger LOGGER = LoggerFactory.getLogger(AssetTypeRepository.class);
  private static final ObjectMapper OBJECT_MAPPER = new ObjectMapper();

  private final Repositories repositories;
  private final SessionFactory sessionFactory;

  public AssetTypeRepository(Repositories repositories, SessionFactory sessionFactory) {
    this.repositories = repositories;
    this.sessionFactory = sessionFactory;
  }

  /** Create a new asset type */
  public AssetTypeInfo createAssetType(CreateAssetType createAssetType) {
    LOGGER.debug(
        "Creating asset type: {}.{}.{}",
        createAssetType.getCatalogName(),
        createAssetType.getSchemaName(),
        createAssetType.getName());

    Session session = sessionFactory.openSession();
    Transaction transaction = null;
    try {
      transaction = session.beginTransaction();

      // Check if catalog and schema exist
      repositories
          .getSchemaRepository()
          .getSchema(createAssetType.getCatalogName() + "." + createAssetType.getSchemaName());

      // Check if asset type already exists
      String fullName =
          String.format(
              "%s.%s.%s",
              createAssetType.getCatalogName(),
              createAssetType.getSchemaName(),
              createAssetType.getName());

      Query<AssetTypeDAO> query =
          session.createQuery(
              "FROM AssetTypeDAO WHERE catalogName = :catalog AND schemaName = :schema AND name = :name",
              AssetTypeDAO.class);
      query.setParameter("catalog", createAssetType.getCatalogName());
      query.setParameter("schema", createAssetType.getSchemaName());
      query.setParameter("name", createAssetType.getName());

      if (query.uniqueResult() != null) {
        throw new BaseException(ErrorCode.ALREADY_EXISTS, "Asset type already exists: " + fullName);
      }

      // Serialize properties to JSON string
      String propertiesJson = null;
      if (createAssetType.getProperties() != null) {
        try {
          propertiesJson = OBJECT_MAPPER.writeValueAsString(createAssetType.getProperties());
        } catch (JsonProcessingException e) {
          LOGGER.error("Failed to serialize properties", e);
        }
      }

      // Create new asset type
      AssetTypeDAO dao =
          AssetTypeDAO.builder()
              .id(UUID.randomUUID())
              .catalogName(createAssetType.getCatalogName())
              .schemaName(createAssetType.getSchemaName())
              .name(createAssetType.getName())
              .comment(createAssetType.getComment())
              .properties(propertiesJson)
              .createdAt(new Date())
              .createdBy(IdentityUtils.findPrincipalEmailAddress())
              .build();

      session.persist(dao);
      transaction.commit();

      return toAssetTypeInfo(dao);
    } catch (Exception e) {
      if (transaction != null) {
        transaction.rollback();
      }
      if (e instanceof BaseException) {
        throw (BaseException) e;
      }
      throw new BaseException(ErrorCode.INTERNAL, "Failed to create asset type", e);
    } finally {
      session.close();
    }
  }

  /** Get an asset type by full name */
  public AssetTypeInfo getAssetType(String fullName) {
    LOGGER.debug("Getting asset type: {}", fullName);

    String[] parts = fullName.split("\\.");
    if (parts.length != 3) {
      throw new BaseException(
          ErrorCode.INVALID_ARGUMENT,
          "Invalid asset type full name format. Expected: catalog.schema.name");
    }

    try (Session session = sessionFactory.openSession()) {
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

      return toAssetTypeInfo(dao);
    }
  }

  /** List asset types in a schema */
  public AssetTypeList listAssetTypes(
      String catalogName,
      String schemaName,
      Optional<Integer> maxResults,
      Optional<String> pageToken) {
    LOGGER.debug("Listing asset types in {}.{}", catalogName, schemaName);

    try (Session session = sessionFactory.openSession()) {
      // Validate catalog and schema exist
      repositories.getSchemaRepository().getSchema(catalogName + "." + schemaName);

      Query<AssetTypeDAO> query =
          session.createQuery(
              "FROM AssetTypeDAO WHERE catalogName = :catalog AND schemaName = :schema ORDER BY name",
              AssetTypeDAO.class);
      query.setParameter("catalog", catalogName);
      query.setParameter("schema", schemaName);

      // Apply pagination
      int limit = maxResults.orElse(100);
      if (pageToken.isPresent()) {
        query.setFirstResult(Integer.parseInt(pageToken.get()));
      }
      query.setMaxResults(limit);

      List<AssetTypeDAO> results = query.list();
      List<AssetTypeInfo> assetTypes =
          results.stream().map(this::toAssetTypeInfo).collect(Collectors.toList());

      String nextPageToken = null;
      if (results.size() == limit) {
        int nextOffset = pageToken.map(Integer::parseInt).orElse(0) + limit;
        nextPageToken = String.valueOf(nextOffset);
      }

      return new AssetTypeList().assetTypes(assetTypes).nextPageToken(nextPageToken);
    }
  }

  /** Delete an asset type */
  public void deleteAssetType(String fullName) {
    LOGGER.debug("Deleting asset type: {}", fullName);

    String[] parts = fullName.split("\\.");
    if (parts.length != 3) {
      throw new BaseException(
          ErrorCode.INVALID_ARGUMENT,
          "Invalid asset type full name format. Expected: catalog.schema.name");
    }

    Session session = sessionFactory.openSession();
    Transaction transaction = null;
    try {
      transaction = session.beginTransaction();

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

      // Check if there are any assets using this type
      Query<Long> assetCountQuery =
          session.createQuery(
              "SELECT COUNT(*) FROM AssetDAO WHERE assetType = :assetType", Long.class);
      assetCountQuery.setParameter("assetType", dao);
      Long assetCount = assetCountQuery.uniqueResult();

      if (assetCount != null && assetCount > 0) {
        throw new BaseException(
            ErrorCode.INVALID_ARGUMENT,
            "Cannot delete asset type. " + assetCount + " assets still reference this type.");
      }

      session.remove(dao);
      transaction.commit();
    } catch (Exception e) {
      if (transaction != null) {
        transaction.rollback();
      }
      if (e instanceof BaseException) {
        throw (BaseException) e;
      }
      throw new BaseException(ErrorCode.INTERNAL, "Failed to delete asset type", e);
    } finally {
      session.close();
    }
  }

  /** Convert DAO to model object */
  private AssetTypeInfo toAssetTypeInfo(AssetTypeDAO dao) {
    // Deserialize properties from JSON string
    List<AssetPropertyDef> properties = null;
    if (dao.getProperties() != null) {
      try {
        properties =
            OBJECT_MAPPER.readValue(
                dao.getProperties(),
                OBJECT_MAPPER
                    .getTypeFactory()
                    .constructCollectionType(List.class, AssetPropertyDef.class));
      } catch (JsonProcessingException e) {
        LOGGER.error("Failed to deserialize properties", e);
      }
    }

    return new AssetTypeInfo()
        .catalogName(dao.getCatalogName())
        .schemaName(dao.getSchemaName())
        .name(dao.getName())
        .fullName(dao.getFullName())
        .comment(dao.getComment())
        .properties(properties)
        .owner(dao.getOwner())
        .createdAt(dao.getCreatedAt() != null ? dao.getCreatedAt().getTime() : null)
        .createdBy(dao.getCreatedBy())
        .updatedAt(dao.getUpdatedAt() != null ? dao.getUpdatedAt().getTime() : null)
        .updatedBy(dao.getUpdatedBy());
  }
}
