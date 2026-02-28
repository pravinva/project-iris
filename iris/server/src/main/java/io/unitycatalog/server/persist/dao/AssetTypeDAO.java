package io.unitycatalog.server.persist.dao;

import jakarta.persistence.Column;
import jakarta.persistence.Entity;
import jakarta.persistence.Id;
import jakarta.persistence.Table;
import jakarta.persistence.Temporal;
import jakarta.persistence.TemporalType;
import jakarta.persistence.Transient;
import jakarta.persistence.UniqueConstraint;
import java.util.Date;
import java.util.UUID;
import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.EqualsAndHashCode;
import lombok.Getter;
import lombok.NoArgsConstructor;
import lombok.Setter;

/**
 * Hibernate entity for AssetType table Represents a type/template for assets with predefined
 * property definitions
 */
@Entity
@Table(
    name = "uc_asset_types",
    uniqueConstraints = {@UniqueConstraint(columnNames = {"catalog_name", "schema_name", "name"})})
@Getter
@Setter
@NoArgsConstructor
@AllArgsConstructor
@Builder
@EqualsAndHashCode(onlyExplicitlyIncluded = true)
public class AssetTypeDAO {

  @Id
  @Column(name = "id", nullable = false)
  @EqualsAndHashCode.Include
  private UUID id;

  @Column(name = "catalog_name", nullable = false)
  private String catalogName;

  @Column(name = "schema_name", nullable = false)
  private String schemaName;

  @Column(name = "name", nullable = false)
  private String name;

  @Column(name = "comment", columnDefinition = "TEXT")
  private String comment;

  /** JSON column storing array of AssetPropertyDef objects */
  @Column(name = "properties", columnDefinition = "TEXT")
  private String properties; // Store as JSON string for simplicity

  @Column(name = "owner")
  private String owner;

  @Column(name = "created_at")
  @Temporal(TemporalType.TIMESTAMP)
  private Date createdAt;

  @Column(name = "created_by")
  private String createdBy;

  @Column(name = "updated_at")
  @Temporal(TemporalType.TIMESTAMP)
  private Date updatedAt;

  @Column(name = "updated_by")
  private String updatedBy;

  /** Gets the full name of the asset type (catalog.schema.name) */
  @Transient
  public String getFullName() {
    return String.format("%s.%s.%s", catalogName, schemaName, name);
  }

  public UUID getId() {
    if (id == null) {
      id = UUID.randomUUID();
    }
    return id;
  }
}
