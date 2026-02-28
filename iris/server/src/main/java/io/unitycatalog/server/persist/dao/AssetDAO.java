package io.unitycatalog.server.persist.dao;

import jakarta.persistence.CascadeType;
import jakarta.persistence.Column;
import jakarta.persistence.Entity;
import jakarta.persistence.FetchType;
import jakarta.persistence.Id;
import jakarta.persistence.Index;
import jakarta.persistence.JoinColumn;
import jakarta.persistence.ManyToOne;
import jakarta.persistence.OneToMany;
import jakarta.persistence.Table;
import jakarta.persistence.Temporal;
import jakarta.persistence.TemporalType;
import jakarta.persistence.Transient;
import jakarta.persistence.UniqueConstraint;
import java.util.Date;
import java.util.List;
import java.util.UUID;
import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.EqualsAndHashCode;
import lombok.Getter;
import lombok.NoArgsConstructor;
import lombok.Setter;

/**
 * Hibernate entity for Asset table Represents an instance of an AssetType with specific property
 * values and bindings
 */
@Entity
@Table(
    name = "uc_assets",
    uniqueConstraints = {@UniqueConstraint(columnNames = {"catalog_name", "schema_name", "name"})},
    indexes = {
      @Index(name = "idx_asset_type", columnList = "asset_type_id"),
      @Index(name = "idx_parent_asset", columnList = "parent_asset_id")
    })
@Getter
@Setter
@NoArgsConstructor
@AllArgsConstructor
@Builder
@EqualsAndHashCode(onlyExplicitlyIncluded = true)
public class AssetDAO {

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

  /** Reference to the asset type */
  @ManyToOne(fetch = FetchType.LAZY)
  @JoinColumn(name = "asset_type_id", referencedColumnName = "id", nullable = false)
  private AssetTypeDAO assetType;

  /** Self-referential foreign key for parent asset (enables hierarchy) */
  @ManyToOne(fetch = FetchType.LAZY)
  @JoinColumn(name = "parent_asset_id", referencedColumnName = "id")
  private AssetDAO parentAsset;

  /** Children assets (inverse of parentAsset relationship) */
  @OneToMany(mappedBy = "parentAsset", cascade = CascadeType.ALL, fetch = FetchType.LAZY)
  private List<AssetDAO> childAssets;

  @Column(name = "comment", columnDefinition = "TEXT")
  private String comment;

  /** JSON column storing key-value properties - simplified to String */
  @Column(name = "properties", columnDefinition = "TEXT")
  private String properties;

  /** JSON column storing array of AssetPropertyBinding objects - simplified to String */
  @Column(name = "property_bindings", columnDefinition = "TEXT")
  private String propertyBindings;

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

  /** Gets the full name of the asset (catalog.schema.name) */
  @Transient
  public String getFullName() {
    return String.format("%s.%s.%s", catalogName, schemaName, name);
  }

  /** Gets the full name of the asset type if available */
  @Transient
  public String getAssetTypeFullName() {
    if (assetType != null) {
      return assetType.getFullName();
    }
    return null;
  }

  /** Gets the full name of the parent asset if available */
  @Transient
  public String getParentAssetFullName() {
    if (parentAsset != null) {
      return parentAsset.getFullName();
    }
    return null;
  }

  public UUID getId() {
    if (id == null) {
      id = UUID.randomUUID();
    }
    return id;
  }
}
