# Project IRIS — Phase 1 Context Engineering Specs
## Unity Catalog OT Extension

### Environment Constants
```
DATABRICKS_WAREHOUSE_ID = 4b9b953939869799
DATABRICKS_PROFILE      = DEFAULT
PIAF_CATALOG            = osipi
PIAF_SCHEMA             = bronze
UC_BASE_URL             = http://localhost:8080
IRIS_CATALOG            = iris_demo
IRIS_SCHEMA             = pilbara
UC_REPO                 = https://github.com/unitycatalog/unitycatalog
IRIS_BRANCH             = feature/ot-asset-extension
```

These constants are referenced by name throughout all workstream specs. Do not hardcode values inline.

---

## Workstream 1.1 — Repository Fork and Development Environment

### Intent
Produce a locally running Unity Catalog server forked from upstream, with a clean build, on a branch ready to receive the IRIS asset extension.

### Inputs
- Git configured with access to GitHub
- Java 17 installed, `JAVA_HOME` set to JDK 17
- Node.js ≥ 18 and Yarn installed
- `build/sbt` available on PATH
- No prior clone of the UC repository

### Outputs
- Fork exists at `iris-iot/iris` on GitHub
- Local clone of `iris-iot/iris` with upstream remote configured
- Branch `IRIS_BRANCH` created and pushed
- `bin/start-uc-server` starts without error
- `bin/uc table list --catalog unity --schema default` returns at least one table
- UI loads at `http://localhost:3000`
- Directory `docs/iris/` exists with empty `asset-model.md` and `api-reference.md`

### Constraints
1. Do not modify any existing UC source file in this workstream
2. Do not create any files outside the directories listed in Outputs
3. Java version must be exactly 17 — do not use 11 or 21
4. Do not use `sudo` for any build or install step
5. The upstream remote must be named `upstream` — not `origin2` or any other alias
6. All git operations must be on `IRIS_BRANCH` — never commit to `main`

### Spec
**Fork configuration:**
- Origin remote: `git@github.com:iris-iot/iris.git`
- Upstream remote: `https://github.com/unitycatalog/unitycatalog`
- Active branch: `IRIS_BRANCH`

**Build output:**
- `build/sbt clean package` exits with code 0
- No ERROR or WARN lines in sbt output relating to compilation

**Server:**
- Starts on port 8080
- Health check: `curl http://localhost:8080/api/1.0/unity-catalog/catalogs` returns HTTP 200

**UI:**
- Starts on port 3000
- `http://localhost:3000` returns HTTP 200

**docs/iris/asset-model.md** must contain at minimum:
```markdown
# IRIS Asset Model Design

## Object Types Added
- AssetType
- Asset
- AssetPropertyBinding

## Key Design Decisions
- Self-referential parent_asset_id enables unlimited hierarchy depth
- Typed bindings connect asset properties to any lakehouse data source
```

### Tasks
1. Fork `UC_REPO` to `iris-iot/iris` via GitHub UI or API
2. Clone the fork: `git clone git@github.com:iris-iot/iris.git`
3. Add upstream: `git remote add upstream https://github.com/unitycatalog/unitycatalog`
4. Create and push branch: `git checkout -b IRIS_BRANCH && git push -u origin IRIS_BRANCH`
5. Build: `build/sbt clean package`
6. Start server: `bin/start-uc-server` (background process)
7. Validate CLI: `bin/uc table list --catalog unity --schema default`
8. Start UI: `cd ui && yarn install && yarn start` (background process)
9. Validate UI: `curl -s -o /dev/null -w "%{http_code}" http://localhost:3000`
10. Create `docs/iris/` with the two markdown files per spec above

### Verification
```bash
# All of these must succeed (exit 0 and expected output)

git remote -v | grep upstream
# Expected: upstream https://github.com/unitycatalog/unitycatalog (fetch)

git branch --show-current
# Expected: feature/ot-asset-extension

build/sbt clean package 2>&1 | tail -5
# Expected: [success] Total time: ...

curl -s http://localhost:8080/api/1.0/unity-catalog/catalogs \
  | python3 -c "import sys,json; d=json.load(sys.stdin); assert len(d.get('catalogs',[])) > 0"
# Expected: exits 0

curl -s -o /dev/null -w "%{http_code}" http://localhost:3000
# Expected: 200

ls docs/iris/
# Expected: api-reference.md  asset-model.md
```

---

## Workstream 1.2 — OpenAPI Specification

### Intent
Extend `api/all.yaml` with AssetType, Asset, and AssetPropertyBinding schemas and REST endpoints, then regenerate server models and Python client stubs so the asset extension has a complete, compilable API surface.

### Inputs
- Workstream 1.1 complete: UC server builds and runs
- `api/all.yaml` in its original upstream state
- `build/sbt generate` command available

### Outputs
- `api/all.yaml` contains all schemas and paths defined in Spec below
- `build/sbt generate` completes without error
- `build/sbt clean compile` completes without error
- Generated Java model files exist at paths defined in Verification
- Generated Python type files exist at paths defined in Verification
- Zero pre-existing tests broken

### Constraints
1. Do not modify any existing schema or path in `api/all.yaml`
2. Only append to the `components/schemas` and `paths` sections — do not restructure the file
3. All new schema names must be prefixed with nothing — follow UC naming convention exactly (e.g. `AssetTypeInfo` not `IRISAssetTypeInfo`)
4. Required fields must match exactly what the Java service layer will enforce — do not mark optional fields as required
5. `binding_type` enum values must be uppercase with underscores exactly as listed in Spec
6. Do not add any field not listed in the Spec — extra fields will be rejected in code review
7. YAML must be valid — run `python3 -c "import yaml; yaml.safe_load(open('api/all.yaml'))"` before committing

### Spec

**Schemas to add under `components/schemas`:**

```yaml
AssetPropertyDef:
  type: object
  required: [name, data_type]
  properties:
    name:
      type: string
    data_type:
      type: string
      enum: [DOUBLE, STRING, INTEGER, BOOLEAN, TIMESTAMP]
    unit:
      type: string
    expression:
      type: string
    required:
      type: boolean
      default: false

AssetTypeInfo:
  type: object
  required: [name, catalog_name, schema_name]
  properties:
    name:
      type: string
    catalog_name:
      type: string
    schema_name:
      type: string
    full_name:
      type: string
    comment:
      type: string
    properties:
      type: array
      items:
        $ref: '#/components/schemas/AssetPropertyDef'
    isa95_object_type:
      type: string
      enum: [Enterprise, Site, Area, ProcessCell, Unit, Equipment, ControlModule]
    created_at:
      type: integer
      format: int64
    updated_at:
      type: integer
      format: int64
    asset_type_id:
      type: string

CreateAssetType:
  type: object
  required: [name, catalog_name, schema_name]
  properties:
    name:
      type: string
    catalog_name:
      type: string
    schema_name:
      type: string
    comment:
      type: string
    properties:
      type: array
      items:
        $ref: '#/components/schemas/AssetPropertyDef'
    isa95_object_type:
      type: string
      enum: [Enterprise, Site, Area, ProcessCell, Unit, Equipment, ControlModule]

AssetPropertyBinding:
  type: object
  required: [property_name, binding_type]
  properties:
    property_name:
      type: string
    binding_type:
      type: string
      enum: [TAG_REFERENCE, MAINTENANCE_REF, DOCUMENT_REF,
             LAB_REF, MODEL_REF, CALCULATED, STATIC]
    reference:
      type: string
    override_unit:
      type: string

AssetInfo:
  type: object
  required: [name, catalog_name, schema_name, asset_type_full_name]
  properties:
    name:
      type: string
    catalog_name:
      type: string
    schema_name:
      type: string
    full_name:
      type: string
    asset_type_full_name:
      type: string
    parent_asset_full_name:
      type: string
    comment:
      type: string
    bindings:
      type: array
      items:
        $ref: '#/components/schemas/AssetPropertyBinding'
    created_at:
      type: integer
      format: int64
    updated_at:
      type: integer
      format: int64
    asset_id:
      type: string

CreateAsset:
  type: object
  required: [name, catalog_name, schema_name, asset_type_full_name]
  properties:
    name:
      type: string
    catalog_name:
      type: string
    schema_name:
      type: string
    asset_type_full_name:
      type: string
    parent_asset_full_name:
      type: string
    comment:
      type: string
    bindings:
      type: array
      items:
        $ref: '#/components/schemas/AssetPropertyBinding'

AssetList:
  type: object
  properties:
    assets:
      type: array
      items:
        $ref: '#/components/schemas/AssetInfo'
    next_page_token:
      type: string

AssetTypeList:
  type: object
  properties:
    asset_types:
      type: array
      items:
        $ref: '#/components/schemas/AssetTypeInfo'
    next_page_token:
      type: string
```

**Paths to add under `paths`:**

```yaml
/unity-catalog/asset-types:
  get:
    operationId: listAssetTypes
    parameters:
      - {name: catalog_name, in: query, required: true, schema: {type: string}}
      - {name: schema_name,  in: query, required: true, schema: {type: string}}
      - {name: page_token,   in: query, schema: {type: string}}
      - {name: max_results,  in: query, schema: {type: integer}}
    responses:
      '200':
        content:
          application/json:
            schema: {$ref: '#/components/schemas/AssetTypeList'}
  post:
    operationId: createAssetType
    requestBody:
      required: true
      content:
        application/json:
          schema: {$ref: '#/components/schemas/CreateAssetType'}
    responses:
      '200':
        content:
          application/json:
            schema: {$ref: '#/components/schemas/AssetTypeInfo'}

/unity-catalog/asset-types/{full_name}:
  get:
    operationId: getAssetType
    parameters:
      - {name: full_name, in: path, required: true, schema: {type: string}}
    responses:
      '200':
        content:
          application/json:
            schema: {$ref: '#/components/schemas/AssetTypeInfo'}
  delete:
    operationId: deleteAssetType
    parameters:
      - {name: full_name, in: path, required: true, schema: {type: string}}
      - {name: force,     in: query, schema: {type: boolean}}
    responses:
      '200':
        content:
          application/json:
            schema: {type: object}

/unity-catalog/assets:
  get:
    operationId: listAssets
    parameters:
      - {name: catalog_name,          in: query, required: true, schema: {type: string}}
      - {name: schema_name,           in: query, required: true, schema: {type: string}}
      - {name: asset_type_full_name,  in: query, schema: {type: string}}
      - {name: parent_asset_full_name,in: query, schema: {type: string}}
      - {name: recursive,             in: query, schema: {type: boolean, default: false}}
      - {name: page_token,            in: query, schema: {type: string}}
      - {name: max_results,           in: query, schema: {type: integer}}
    responses:
      '200':
        content:
          application/json:
            schema: {$ref: '#/components/schemas/AssetList'}
  post:
    operationId: createAsset
    requestBody:
      required: true
      content:
        application/json:
          schema: {$ref: '#/components/schemas/CreateAsset'}
    responses:
      '200':
        content:
          application/json:
            schema: {$ref: '#/components/schemas/AssetInfo'}

/unity-catalog/assets/{full_name}:
  get:
    operationId: getAsset
    parameters:
      - {name: full_name, in: path, required: true, schema: {type: string}}
    responses:
      '200':
        content:
          application/json:
            schema: {$ref: '#/components/schemas/AssetInfo'}
  delete:
    operationId: deleteAsset
    parameters:
      - {name: full_name, in: path, required: true, schema: {type: string}}
      - {name: force,     in: query, schema: {type: boolean}}
    responses:
      '200':
        content:
          application/json:
            schema: {type: object}

/unity-catalog/assets/{full_name}/children:
  get:
    operationId: listChildAssets
    parameters:
      - {name: full_name, in: path,  required: true, schema: {type: string}}
      - {name: recursive, in: query, schema: {type: boolean, default: false}}
    responses:
      '200':
        content:
          application/json:
            schema: {$ref: '#/components/schemas/AssetList'}
```

### Tasks
1. Open `api/all.yaml`
2. Validate YAML is parseable before editing: `python3 -c "import yaml; yaml.safe_load(open('api/all.yaml'))"`
3. Append all schemas from Spec to the `components/schemas` section
4. Append all paths from Spec to the `paths` section
5. Validate YAML after editing: `python3 -c "import yaml; yaml.safe_load(open('api/all.yaml'))"`
6. Regenerate: `build/sbt generate`
7. Compile: `build/sbt clean compile`

### Verification
```bash
# YAML valid
python3 -c "import yaml; yaml.safe_load(open('api/all.yaml'))" && echo PASS

# Schemas present
python3 -c "
import yaml
spec = yaml.safe_load(open('api/all.yaml'))
schemas = spec['components']['schemas']
required = ['AssetTypeInfo','AssetInfo','AssetPropertyBinding',
            'CreateAssetType','CreateAsset','AssetList','AssetTypeList',
            'AssetPropertyDef']
missing = [s for s in required if s not in schemas]
assert not missing, f'Missing schemas: {missing}'
print('PASS: all schemas present')
"

# Paths present
python3 -c "
import yaml
spec = yaml.safe_load(open('api/all.yaml'))
paths = spec['paths']
required = ['/unity-catalog/asset-types',
            '/unity-catalog/asset-types/{full_name}',
            '/unity-catalog/assets',
            '/unity-catalog/assets/{full_name}',
            '/unity-catalog/assets/{full_name}/children']
missing = [p for p in required if p not in paths]
assert not missing, f'Missing paths: {missing}'
print('PASS: all paths present')
"

# Generated Java models exist
for f in AssetTypeInfo AssetInfo AssetPropertyBinding CreateAssetType CreateAsset; do
  ls server/src/main/java/io/unitycatalog/server/model/${f}.java && echo "PASS: ${f}.java"
done

# Generated Python types exist
for f in asset_type_info asset_info asset_property_binding; do
  ls clients/python/src/unitycatalog/types/${f}.py && echo "PASS: ${f}.py"
done

# Compile clean
build/sbt clean compile 2>&1 | grep -E "^\[error\]" | wc -l
# Expected: 0
```

---

## Workstream 1.3 — Java Server: Persistence and Service Layer

### Intent
Implement the database entities, repositories, services, and HTTP handlers for AssetType and Asset so the UC REST API fully supports asset CRUD and recursive hierarchy traversal.

### Inputs
- Workstream 1.2 complete: generated Java models exist, project compiles
- `server/src/main/java/io/unitycatalog/server/persist/dao/TableInfoDAO.java` — reference pattern for DAO
- `server/src/main/java/io/unitycatalog/server/service/TableService.java` — reference pattern for service
- H2 embedded database in use (supports `WITH RECURSIVE` CTE since version 2.x)

### Outputs
- `AssetTypeDAO.java` — Hibernate entity for `uc_asset_types` table
- `AssetDAO.java` — Hibernate entity for `uc_assets` table with self-referential `parent_asset_id`
- `AssetTypeRepository.java` — CRUD operations for AssetType
- `AssetRepository.java` — CRUD plus recursive hierarchy traversal for Asset
- `AssetTypeService.java` — business logic and validation for AssetType
- `AssetService.java` — business logic and validation for Asset
- `AssetTypeHandler.java` — HTTP request routing for AssetType endpoints
- `AssetHandler.java` — HTTP request routing for Asset endpoints
- Both handlers registered in the server bootstrap
- `build/sbt -J-Xmx2G clean test` passes with zero failures
- New integration tests added per Spec

### Constraints
1. Do not modify any existing DAO, service, or handler class
2. Follow Google Java style throughout — run `build/sbt javafmtAll` before committing
3. All database operations must use the existing Hibernate session factory — do not open JDBC connections directly
4. `parent_asset_id` must be nullable at the database level — root assets have no parent
5. Do not implement soft delete — delete is permanent
6. Do not implement update (PATCH) endpoints in Phase 1 — create and delete only
7. Serialise `properties_json` and `bindings_json` as JSON strings using Jackson `ObjectMapper` — do not add new dependencies
8. The recursive CTE must use `WITH RECURSIVE` SQL syntax — do not implement hierarchy traversal in Java application code
9. Error responses must follow the existing UC error response format — study `BaseException` and existing error handling before writing any error path
10. Do not add any endpoint not defined in the OpenAPI spec from Workstream 1.2

### Spec

**Database tables created on server startup:**
```sql
CREATE TABLE IF NOT EXISTS uc_asset_types (
  asset_type_id  VARCHAR(36)   NOT NULL PRIMARY KEY,
  name           VARCHAR(255)  NOT NULL,
  catalog_name   VARCHAR(255)  NOT NULL,
  schema_name    VARCHAR(255)  NOT NULL,
  comment        TEXT,
  isa95_object_type VARCHAR(64),
  properties_json TEXT,
  created_at     BIGINT,
  updated_at     BIGINT,
  UNIQUE (catalog_name, schema_name, name)
);

CREATE TABLE IF NOT EXISTS uc_assets (
  asset_id            VARCHAR(36)   NOT NULL PRIMARY KEY,
  name                VARCHAR(255)  NOT NULL,
  catalog_name        VARCHAR(255)  NOT NULL,
  schema_name         VARCHAR(255)  NOT NULL,
  asset_type_id       VARCHAR(36)   NOT NULL,
  parent_asset_id     VARCHAR(36),  -- NULL for root assets
  comment             TEXT,
  bindings_json       TEXT,
  created_at          BIGINT,
  updated_at          BIGINT,
  UNIQUE (catalog_name, schema_name, name),
  FOREIGN KEY (asset_type_id) REFERENCES uc_asset_types(asset_type_id),
  FOREIGN KEY (parent_asset_id) REFERENCES uc_assets(asset_id)
);
```

**Recursive CTE for `getChildren(assetId, recursive=true)`:**
```sql
WITH RECURSIVE asset_tree AS (
  SELECT * FROM uc_assets
  WHERE parent_asset_id = :assetId
  UNION ALL
  SELECT a.* FROM uc_assets a
  INNER JOIN asset_tree t ON a.parent_asset_id = a.asset_id
)
SELECT * FROM asset_tree
```

**Error behaviour:**

| Condition | HTTP Status | Message |
|---|---|---|
| Asset type name already exists in catalog.schema | 409 | AssetType {name} already exists in {catalog}.{schema} |
| Asset name already exists in catalog.schema | 409 | Asset {name} already exists in {catalog}.{schema} |
| Referenced asset_type_full_name not found | 404 | AssetType {full_name} not found |
| Referenced parent_asset_full_name not found | 404 | Parent asset {full_name} not found |
| Delete asset type with instances, force=false | 409 | AssetType {full_name} has {n} asset instances. Use force=true to delete. |
| Delete asset with children, force=false | 409 | Asset {full_name} has {n} child assets. Use force=true to delete. |
| Get/delete non-existent asset or type | 404 | {AssetType\|Asset} {full_name} not found |

**Integration tests to add in `integration-tests/`:**

```
T01  Create AssetType → GET returns same object
T02  Create AssetType duplicate name → 409
T03  Create Asset with valid asset_type_full_name → GET returns object
T04  Create Asset with invalid asset_type_full_name → 404
T05  Create Asset with valid parent → GET shows parent_asset_full_name
T06  Create Asset with invalid parent → 404
T07  Create 4-level hierarchy (Site→Area→Unit→Equipment)
       GET children of Site with recursive=false → returns Area only
       GET children of Site with recursive=true  → returns Area+Unit+Equipment
T08  Delete Asset with children, force=false → 409
T09  Delete Asset with children, force=true  → 200, children also deleted
T10  Delete AssetType with instances, force=false → 409
T11  Delete AssetType with instances, force=true  → 200, instances also deleted
T12  List assets with parent_asset_full_name filter → returns direct children only
T13  List assets with asset_type_full_name filter → returns matching type only
```

### Tasks
1. Study `TableInfoDAO.java`, `TableService.java`, `TableHandler.java` before writing any code
2. Create `AssetTypeDAO.java` per Spec schema
3. Create `AssetDAO.java` per Spec schema — `parent_asset_id` is nullable UUID
4. Register both entities in the Hibernate session factory configuration
5. Create `AssetTypeRepository.java` — CRUD, unique constraint validation, force-delete check
6. Create `AssetRepository.java` — CRUD, recursive CTE traversal, topological force-delete
7. Create `AssetTypeService.java` — validate inputs, call repository, map DAO↔model
8. Create `AssetService.java` — validate asset_type exists, validate parent exists, map DAO↔model
9. Create `AssetTypeHandler.java` — route HTTP to AssetTypeService, follow TableHandler pattern
10. Create `AssetHandler.java` — route HTTP to AssetService
11. Register both handlers in server bootstrap
12. Run `build/sbt javafmtAll`
13. Run `build/sbt -J-Xmx2G clean test`
14. Add integration tests T01–T13 per Spec

### Verification
```bash
# Tests pass
build/sbt -J-Xmx2G clean test 2>&1 | grep -E "error|failed|FAILED" | grep -v "//.*error"
# Expected: no output

# Server starts and asset endpoints respond
bin/start-uc-server &
sleep 3

# Create asset type
curl -s -X POST http://localhost:8080/api/1.0/unity-catalog/asset-types \
  -H "Content-Type: application/json" \
  -d '{"name":"TestMotor","catalog_name":"unity","schema_name":"default","isa95_object_type":"Equipment"}' \
  | python3 -c "import sys,json; d=json.load(sys.stdin); assert d['name']=='TestMotor'; print('PASS: createAssetType')"

# Get asset type
curl -s http://localhost:8080/api/1.0/unity-catalog/asset-types/unity.default.TestMotor \
  | python3 -c "import sys,json; d=json.load(sys.stdin); assert d['asset_type_id'] is not None; print('PASS: getAssetType')"

# Create root asset
curl -s -X POST http://localhost:8080/api/1.0/unity-catalog/assets \
  -H "Content-Type: application/json" \
  -d '{"name":"TestSite","catalog_name":"unity","schema_name":"default","asset_type_full_name":"unity.default.TestMotor"}' \
  | python3 -c "import sys,json; d=json.load(sys.stdin); assert d['parent_asset_full_name'] is None; print('PASS: createRootAsset')"

# Create child asset
curl -s -X POST http://localhost:8080/api/1.0/unity-catalog/assets \
  -H "Content-Type: application/json" \
  -d '{"name":"TestChild","catalog_name":"unity","schema_name":"default","asset_type_full_name":"unity.default.TestMotor","parent_asset_full_name":"unity.default.TestSite"}' \
  | python3 -c "import sys,json; d=json.load(sys.stdin); assert d['parent_asset_full_name']=='unity.default.TestSite'; print('PASS: createChildAsset')"

# Recursive children
curl -s "http://localhost:8080/api/1.0/unity-catalog/assets/unity.default.TestSite/children?recursive=true" \
  | python3 -c "import sys,json; d=json.load(sys.stdin); assert len(d['assets']) >= 1; print('PASS: listChildAssets')"

# Force=false delete with children → 409
STATUS=$(curl -s -o /dev/null -w "%{http_code}" \
  -X DELETE "http://localhost:8080/api/1.0/unity-catalog/assets/unity.default.TestSite?force=false")
[ "$STATUS" = "409" ] && echo "PASS: force=false returns 409" || echo "FAIL: expected 409 got $STATUS"
```

---

## Workstream 1.4 — Python SDK: Asset Client

### Intent
Deliver a high-level Python client for AssetType and Asset operations that is accessible as `uc.asset_types` and `uc.assets` on the existing UnityCatalog client, with a working end-to-end example script.

### Inputs
- Workstream 1.3 complete: UC server running, asset REST endpoints responding
- Generated Python stubs in `clients/python/src/unitycatalog/types/`
- Existing `TablesClient` in `clients/python/src/unitycatalog/` as reference pattern
- `UC_BASE_URL = http://localhost:8080`

### Outputs
- `clients/python/src/unitycatalog/assets.py` containing `AssetTypesClient` and `AssetsClient`
- `uc.asset_types` and `uc.assets` accessible on the `UnityCatalog` client class
- `examples/iris_asset_demo.py` runs end-to-end without error against a live UC server
- `clients/python/tests/test_assets.py` — all tests pass

### Constraints
1. Do not modify any existing client file except to register the two new clients on the `UnityCatalog` class
2. `get_hierarchy_path` must walk up via API calls — do not fetch all assets and traverse in memory
3. `list` methods must handle pagination transparently — callers receive an iterator, not a page
4. Do not add any dependency not already in `clients/python/requirements.txt`
5. All methods must accept `full_name` as a dotted string `catalog.schema.name` — do not require separate catalog/schema/name arguments on get/delete
6. `create` methods must accept `catalog_name`, `schema_name`, `name` as separate arguments — consistent with existing UC client patterns
7. Raise `ValueError` with a descriptive message on invalid `binding_type` — do not silently accept arbitrary strings
8. Do not implement retry logic — leave that to the caller

### Spec

**`AssetTypesClient` interface:**
```python
create(catalog_name, schema_name, name,
       properties=None, isa95_object_type=None,
       comment=None) -> AssetTypeInfo

get(full_name) -> AssetTypeInfo

list(catalog_name, schema_name) -> Iterator[AssetTypeInfo]
# Must handle pagination. Yields one item at a time.

delete(full_name, force=False) -> None
```

**`AssetsClient` interface:**
```python
create(catalog_name, schema_name, name,
       asset_type_full_name,
       parent_full_name=None,
       bindings=None,
       comment=None) -> AssetInfo

get(full_name) -> AssetInfo

list(catalog_name, schema_name,
     asset_type_full_name=None,
     parent_full_name=None,
     recursive=False) -> Iterator[AssetInfo]

get_children(full_name, recursive=True) -> Iterator[AssetInfo]

get_hierarchy_path(full_name) -> list[AssetInfo]
# Returns [root, ..., target] ordered from root to target.
# Example: [ScreeningPlant_A, CrusherCircuit_1, CrusherMotor_CM001]

bind(full_name, property_name, binding_type,
     reference, override_unit=None) -> AssetInfo
# Adds or replaces a single binding on an existing asset.
# Valid binding_type values: TAG_REFERENCE, MAINTENANCE_REF,
# DOCUMENT_REF, LAB_REF, MODEL_REF, CALCULATED, STATIC

delete(full_name, force=False) -> None
```

**`examples/iris_asset_demo.py` must demonstrate:**
1. Create a CrusherMotor AssetType with three properties
2. Create a 3-level hierarchy: Site → ProcessUnit → CrusherMotor instance
3. Add TAG_REFERENCE bindings on the motor
4. Call `get_children(recursive=True)` on the site and print count
5. Call `get_hierarchy_path` on the motor and print as ` → ` separated names
6. Call `get` on the motor and print its bindings

**Tests in `test_assets.py`:**

```
T01  create AssetType → get returns matching object
T02  list AssetTypes → yields created type
T03  create Asset with parent → get shows parent_asset_full_name
T04  get_children(recursive=True) on Site → returns all 3 descendant assets
T05  get_hierarchy_path on Equipment → returns [Site, ProcessUnit, Equipment]
T06  bind TAG_REFERENCE → get shows binding in bindings list
T07  invalid binding_type → raises ValueError
T08  delete AssetType → subsequent get raises exception
```

### Tasks
1. Study `TablesClient` pattern before writing any code
2. Create `clients/python/src/unitycatalog/assets.py` with both client classes per Spec
3. Register on `UnityCatalog` class: `self.asset_types = AssetTypesClient(self)` and `self.assets = AssetsClient(self)`
4. Create `examples/iris_asset_demo.py` per Spec
5. Create `clients/python/tests/test_assets.py` with T01–T08
6. Run tests: `cd clients/python && python -m pytest tests/test_assets.py -v`
7. Run demo: `python examples/iris_asset_demo.py`

### Verification
```bash
cd clients/python

# Tests
python -m pytest tests/test_assets.py -v 2>&1 | tail -20
# Expected: 8 passed

# Demo runs clean
python ../../examples/iris_asset_demo.py
# Expected: no exception, prints hierarchy path and bindings

# Client accessible
python3 -c "
from unitycatalog import UnityCatalog
uc = UnityCatalog(base_url='http://localhost:8080')
assert hasattr(uc, 'asset_types'), 'asset_types not on client'
assert hasattr(uc, 'assets'), 'assets not on client'
print('PASS: clients registered')
"

# Hierarchy path ordered correctly
python3 -c "
from unitycatalog import UnityCatalog
uc = UnityCatalog(base_url='http://localhost:8080')
path = uc.assets.get_hierarchy_path('unity.default.CrusherMotor_CM001')
names = [a.name for a in path]
assert names[0] != 'CrusherMotor_CM001', 'path must start at root, not target'
assert names[-1] == 'CrusherMotor_CM001', 'path must end at target'
print('PASS: hierarchy path correct:', ' → '.join(names))
"
```

---

## Workstream 1.5 — React UI: Asset Tree Browser

### Intent
Add an Assets section to the UC UI that renders the equipment hierarchy as a navigable tree with a detail panel showing type, properties, bindings, and breadcrumb — so the concept of a physical asset as a first-class UC object is visually immediate.

### Inputs
- Workstream 1.3 complete: asset REST endpoints live at `UC_BASE_URL`
- Workstream 1.4 complete: Python demo confirms correct API responses
- UC UI running at `http://localhost:3000`
- Existing Table browser components as reference for layout patterns

### Outputs
- Assets navigation item in left sidebar under each schema
- `AssetTreePanel` component rendering expandable hierarchy
- `AssetDetailPanel` component with Overview, Properties, Children sections
- `AssetTypeDetailPanel` component for AssetType inspection
- Breadcrumb navigation from root to current asset
- `ui/src/api/assetsApi.ts` with all API call functions
- Zero TypeScript compilation errors
- Zero browser console errors when navigating the asset tree

### Constraints
1. Do not modify any existing component — only add new files and extend the navigation registration
2. Use only libraries already present in `ui/package.json` — do not add dependencies
3. Children must load on demand (on click expand) — do not fetch all assets on page load
4. Do not implement create or delete in the UI in Phase 1 — read-only browsing only
5. Asset type name must display in brackets next to asset name in the tree — `CrusherMotor_CM001 [CrusherMotor]`
6. Breadcrumb must be clickable — each crumb navigates to that asset's detail panel
7. The tree must handle at least 4 levels of nesting without visual clipping or overflow
8. Do not use inline styles — use the existing CSS/styling system the UI already uses

### Spec

**Left navigation structure (per schema):**
```
Tables
Volumes
Models
Functions
Assets          ← new item
  Asset Types   ← sub-item
```

**Asset tree node display:**
```
▼ ScreeningPlant_A [Site]
    ▼ CrusherCircuit_1 [ProcessUnit]
        ► CrusherMotor_CM001 [CrusherMotor]
        ► CrusherMotor_CM002 [CrusherMotor]
        ► FeedConveyor_CV045 [FeedConveyor]
```
- `▼` = expanded, `►` = collapsed (has children), no arrow = leaf node
- Clicking a node with children toggles expand/collapse AND selects it for detail panel
- Clicking a leaf selects it for detail panel

**AssetDetailPanel sections:**

*Overview:*
- Full name (monospace)
- Asset type (link that navigates to AssetType detail)
- Parent (link that navigates to parent asset detail, or "Root asset" if none)
- Comment (if present)
- Created / Updated timestamps (human-readable)

*Hierarchy breadcrumb:*
```
ScreeningPlant_A > CrusherCircuit_1 > CrusherMotor_CM001
```
Each segment is a clickable link.

*Properties table:*

| Property | Type | Unit | Binding Type | Reference |
|---|---|---|---|---|
| BearingTemperature | DOUBLE | degC | TAG_REFERENCE | osipi.bronze.pi_tags:TI-4521 |
| VibrationRMS | DOUBLE | mm/s | TAG_REFERENCE | osipi.bronze.pi_tags:VI-4522 |

*Children:*
- If has children: "3 direct children" with Expand link
- If leaf: "No children"

**`ui/src/api/assetsApi.ts` functions:**
```typescript
listAssets(catalogName, schemaName, parentFullName?, recursive?): Promise<AssetInfo[]>
getAsset(fullName): Promise<AssetInfo>
getChildren(fullName, recursive?): Promise<AssetInfo[]>
listAssetTypes(catalogName, schemaName): Promise<AssetTypeInfo[]>
getAssetType(fullName): Promise<AssetTypeInfo>
```
All functions call `UC_BASE_URL/api/1.0/unity-catalog/...`. Handle HTTP errors by throwing with the response body message.

### Tasks
1. Create `ui/src/api/assetsApi.ts` per Spec
2. Create `ui/src/components/assets/AssetTreePanel.tsx`
3. Create `ui/src/components/assets/AssetDetailPanel.tsx`
4. Create `ui/src/components/assets/AssetTypeDetailPanel.tsx`
5. Add Assets and Asset Types to schema navigation
6. Register routes for asset and asset type detail views
7. Compile: `cd ui && yarn build`
8. Start: `yarn start`
9. Manual verify against the Rio Tinto seed data from Workstream 1.7

### Verification
```bash
# TypeScript compiles
cd ui && yarn build 2>&1 | grep -E "error TS" | wc -l
# Expected: 0

# UI starts
curl -s -o /dev/null -w "%{http_code}" http://localhost:3000
# Expected: 200
```

Manual verification checklist (run after seeding data from Workstream 1.7):
```
□ Assets item appears in left nav under pilbara schema
□ Clicking Assets shows tree with ScreeningPlant_A at root
□ Expanding ScreeningPlant_A shows CrusherCircuit_1
□ Expanding CrusherCircuit_1 shows CM001, CM002, CV045
□ Clicking CM001 shows detail panel
□ Detail panel shows asset type link: CrusherMotor
□ Detail panel shows properties table with 3 bindings
□ Breadcrumb shows: ScreeningPlant_A > CrusherCircuit_1 > CrusherMotor_CM001
□ Clicking ScreeningPlant_A in breadcrumb navigates to site detail
□ Zero errors in browser console
```

---

## Workstream 1.6 — PI AF Migration Tool

### Intent
Deliver a CLI tool that reads PI AF tables from `PIAF_CATALOG.PIAF_SCHEMA` in the Databricks field engineering workspace and creates the equivalent AssetType, Asset, and binding objects in a running IRIS UC server — producing a validation report confirming fidelity.

### Inputs
- Workstream 1.4 complete: Python SDK available
- Databricks field engineering workspace accessible via `DEFAULT` CLI profile
- `DATABRICKS_WAREHOUSE_ID = 4b9b953939869799`
- `PIAF_CATALOG = osipi`, `PIAF_SCHEMA = bronze`
- PI AF tables available in `osipi.bronze` — confirm by running:
  ```bash
  databricks --profile DEFAULT sql execute \
    --warehouse-id 4b9b953939869799 \
    --statement "SHOW TABLES IN osipi.bronze"
  ```
- IRIS UC server running at `UC_BASE_URL`

### Outputs
- `iris-migration/` Python project with structure defined in Spec
- `python migrate.py --mode validate` runs against `osipi.bronze` and prints a report
- `python migrate.py --mode migrate` creates AssetTypes, Assets, and bindings in IRIS UC
- `python migrate.py --mode sync` detects new/changed elements and updates without duplicating
- Validation report shows ≥ 95% match rate on sampled records

### Constraints
1. Use `databricks-sdk` Python package with `WorkspaceClient()` — it picks up `DEFAULT` profile automatically. Do not hardcode tokens or hostnames.
2. Always pass `warehouse_id=DATABRICKS_WAREHOUSE_ID` to SQL statement execution — do not use a different warehouse
3. Read from `PIAF_CATALOG.PIAF_SCHEMA` only — do not write anything back to Databricks
4. All writes go to IRIS UC via REST API only — do not write to Databricks
5. The tool must be idempotent — running migrate twice must produce the same result as running once. Use `get-or-create` semantics.
6. If an AF element has no matching template, create it under an AssetType named `Generic` — do not skip it
7. If an attribute formula cannot be parsed, log a warning and create the binding as `STATIC` with the raw formula string as reference — do not fail the migration
8. Do not use threads or async — sequential execution only
9. Progress must be printed to stdout during migration — one line per 100 assets created

### Spec

**Project structure:**
```
iris-migration/
  piaf_migrator/
    __init__.py
    reader.py      reads PI AF tables via Databricks SQL
    mapper.py      maps PI AF objects to IRIS API payloads
    writer.py      calls IRIS UC REST API
    validator.py   post-migration fidelity check
    sync.py        incremental sync
  migrate.py       CLI entrypoint
  requirements.txt
```

**PI AF table mappings:**

| Source Table | Source Field | Target Object | Target Field |
|---|---|---|---|
| `AF_ElementTemplate` | `Name` | `AssetType` | `name` |
| `AF_AttributeTemplate` | `Name`, `TypeName` | `AssetPropertyDef` | `name`, `data_type` |
| `AF_AttributeTemplate` | `EngineeringUnit` | `AssetPropertyDef` | `unit` |
| `AF_Element` | `Name` | `Asset` | `name` |
| `AF_Element` | `TemplateID` | `Asset` | `asset_type_full_name` |
| `AF_ElementToElementLink` | `ParentID`, `ChildID` | `Asset` | `parent_asset_full_name` |
| `AF_Attribute` | `PIPointName` | `AssetPropertyBinding` | `reference` (TAG_REFERENCE) |
| `AF_Attribute` | `Formula` | `AssetPropertyBinding` | `reference` (CALCULATED) |

**Data type mapping (AF TypeName → IRIS data_type):**
```
Float32, Float64, Double → DOUBLE
Int16, Int32, Int64      → INTEGER
String                   → STRING
Boolean                  → BOOLEAN
DateTime, Timestamp      → TIMESTAMP
(anything else)          → STRING with warning logged
```

**CLI interface:**
```bash
python migrate.py \
  --uc-url http://localhost:8080 \
  --iris-catalog iris_demo \
  --iris-schema pilbara \
  --mode [migrate|validate|sync] \
  [--since ISO8601_DATETIME]   # sync mode only
  [--dry-run]                  # print what would be created, no writes
```

**Validation report format:**
```
IRIS Migration Validation Report
=================================
Source: osipi.bronze (warehouse: 4b9b953939869799)
Target: iris_demo.pilbara (http://localhost:8080)

AssetTypes:    [n_created] / [n_templates]  [PASS|FAIL]
Assets:        [n_created] / [n_elements]   [PASS|FAIL]
Bindings:      [n_created] / [n_attrs]      [PASS|FAIL]

Hierarchy sample (50 random assets):  [n_match]/50  [PASS|FAIL]
Binding sample  (100 random attrs):   [n_match]/100 [PASS|FAIL]

Warnings ([n_warnings]):
  - [n] attributes with unsupported formula syntax → created as STATIC
  - [n] elements with no template → created under Generic AssetType
  - [n] attributes with no PIPointName and no formula → skipped

RESULT: [PASS|FAIL]
Elapsed: [n]m [n]s
```
PASS requires ≥ 95% on all counts and both samples.

### Tasks
1. Confirm `osipi.bronze` tables are accessible:
   ```bash
   databricks --profile DEFAULT sql execute \
     --warehouse-id 4b9b953939869799 \
     --statement "SHOW TABLES IN osipi.bronze" \
     --output-format JSON
   ```
2. Inspect key tables to understand actual schema:
   ```bash
   databricks --profile DEFAULT sql execute \
     --warehouse-id 4b9b953939869799 \
     --statement "DESCRIBE osipi.bronze.AF_ElementTemplate" \
     --output-format JSON
   ```
   Repeat for `AF_Element`, `AF_Attribute`, `AF_ElementToElementLink`, `AF_AttributeTemplate`
3. Implement `reader.py` using actual column names from step 2
4. Implement `mapper.py` per Spec mappings
5. Implement `writer.py` with idempotent get-or-create semantics
6. Implement `validator.py` per report format in Spec
7. Implement `sync.py` using `updated_at` or equivalent change-tracking field
8. Implement `migrate.py` CLI per Spec interface
9. Run validate: `python migrate.py --uc-url http://localhost:8080 --iris-catalog iris_demo --iris-schema pilbara --mode validate`
10. Run migrate: `python migrate.py --uc-url http://localhost:8080 --iris-catalog iris_demo --iris-schema pilbara --mode migrate`
11. Run validate again to confirm ≥ 95%

### Verification
```bash
# Tables accessible in field eng workspace
databricks --profile DEFAULT sql execute \
  --warehouse-id 4b9b953939869799 \
  --statement "SELECT COUNT(*) as cnt FROM osipi.bronze.AF_ElementTemplate" \
  --output-format JSON
# Expected: cnt > 0

# Dry run produces output without errors
python migrate.py \
  --uc-url http://localhost:8080 \
  --iris-catalog iris_demo \
  --iris-schema pilbara \
  --mode migrate \
  --dry-run
# Expected: prints intended operations, exits 0

# Migration idempotent
python migrate.py --uc-url http://localhost:8080 \
  --iris-catalog iris_demo --iris-schema pilbara --mode migrate
python migrate.py --uc-url http://localhost:8080 \
  --iris-catalog iris_demo --iris-schema pilbara --mode migrate
# Expected: second run shows 0 created, same count as first run

# Validation passes
python migrate.py --uc-url http://localhost:8080 \
  --iris-catalog iris_demo --iris-schema pilbara --mode validate
# Expected: RESULT: PASS in final line
```

---

## Workstream 1.7 — End-to-End Demo: Rio Tinto Crusher Circuit

### Intent
Produce a single runnable demo script that starts from a fresh UC server, seeds the Rio Tinto crusher circuit dataset, and validates the complete Phase 1 system — suitable for showing to the UC product team and Databricks field leadership.

### Inputs
- All of Workstreams 1.1–1.5 complete
- `examples/iris_asset_demo.py` from Workstream 1.4 working
- UC server not running (demo starts it)
- `demo/` directory created in repo root

### Outputs
- `demo/seed_rio_tinto.py` — seeds the crusher circuit dataset
- `demo/run_demo.sh` — orchestrates the full demo sequence
- `demo/README.md` — how to run the demo from scratch
- Running the demo produces zero errors and all checks print PASS

### Constraints
1. `demo/run_demo.sh` must be runnable by someone with no prior knowledge of the codebase — only `README.md` as guidance
2. The demo must start from a clean UC server state — no dependency on prior manual setup
3. All asset names, tag references, and property values must be realistic for an iron ore processing plant — do not use placeholder values like `foo` or `test`
4. The demo must complete in under 5 minutes on a standard laptop
5. Do not require a live Databricks connection for the demo — it runs entirely against the local UC server
6. All checks must print either `PASS: [description]` or `FAIL: [description]` — no ambiguous output

### Spec

**Dataset — AssetTypes:**
```python
[
  {
    "name": "Site",
    "isa95_object_type": "Site",
    "properties": []
  },
  {
    "name": "ProcessUnit",
    "isa95_object_type": "ProcessCell",
    "properties": []
  },
  {
    "name": "CrusherMotor",
    "isa95_object_type": "Equipment",
    "properties": [
      {"name": "BearingTemperature", "data_type": "DOUBLE", "unit": "degC",  "required": True},
      {"name": "VibrationRMS",       "data_type": "DOUBLE", "unit": "mm/s",  "required": True},
      {"name": "MotorCurrent",       "data_type": "DOUBLE", "unit": "A",     "required": True},
    ]
  },
  {
    "name": "FeedConveyor",
    "isa95_object_type": "Equipment",
    "properties": [
      {"name": "BeltSpeed",   "data_type": "DOUBLE", "unit": "m/s", "required": True},
      {"name": "BeltTension", "data_type": "DOUBLE", "unit": "kN",  "required": True},
      {"name": "LoadRate",    "data_type": "DOUBLE", "unit": "t/h", "required": False},
    ]
  }
]
```

**Dataset — Asset hierarchy and bindings:**
```
iris_demo.pilbara.ScreeningPlant_A    [Site]
  └── CrusherCircuit_1               [ProcessUnit]
        ├── CrusherMotor_CM001        [CrusherMotor]
        │     BearingTemperature → TAG_REFERENCE: osipi.bronze.pi_tags:TI-4521
        │     VibrationRMS       → TAG_REFERENCE: osipi.bronze.pi_tags:VI-4522
        │     MotorCurrent       → TAG_REFERENCE: osipi.bronze.pi_tags:AI-4523
        ├── CrusherMotor_CM002        [CrusherMotor]
        │     BearingTemperature → TAG_REFERENCE: osipi.bronze.pi_tags:TI-4531
        │     VibrationRMS       → TAG_REFERENCE: osipi.bronze.pi_tags:VI-4532
        │     MotorCurrent       → TAG_REFERENCE: osipi.bronze.pi_tags:AI-4533
        └── FeedConveyor_CV045        [FeedConveyor]
              BeltSpeed   → TAG_REFERENCE: osipi.bronze.pi_tags:SI-4541
              BeltTension → TAG_REFERENCE: osipi.bronze.pi_tags:FI-4542
```

**Checks `run_demo.sh` must execute and print PASS/FAIL for:**

```
C01  AssetType CrusherMotor exists and has 3 properties
C02  Asset CrusherMotor_CM001 exists with correct parent CrusherCircuit_1
C03  Asset CrusherMotor_CM001 has 3 bindings all of type TAG_REFERENCE
C04  get_children(ScreeningPlant_A, recursive=True) returns exactly 4 assets
C05  get_hierarchy_path(CrusherMotor_CM001) returns list of length 3
C06  get_hierarchy_path(CrusherMotor_CM001)[0].name == ScreeningPlant_A
C07  get_hierarchy_path(CrusherMotor_CM001)[2].name == CrusherMotor_CM001
C08  list(asset_type_full_name=CrusherMotor) returns exactly 2 assets
C09  UC API: GET /assets/iris_demo.pilbara.CrusherMotor_CM001 returns HTTP 200
C10  UC API: DELETE /assets/iris_demo.pilbara.ScreeningPlant_A?force=false returns HTTP 409
```

**`demo/README.md` must include:**
- Prerequisites list (Java 17, Node, Yarn, Python 3.9+)
- Exact commands to run: `bash demo/run_demo.sh`
- Expected output: all 10 checks print PASS
- How to open the UI to browse the asset tree

### Tasks
1. Create `demo/seed_rio_tinto.py` — creates all AssetTypes and Assets per dataset Spec using Python SDK
2. Create `demo/run_demo.sh`:
   - Kill any running UC server on port 8080
   - Start fresh UC server
   - Wait for server health check to pass
   - Run `seed_rio_tinto.py`
   - Execute checks C01–C10 and print PASS/FAIL for each
   - Print final summary: `n/10 checks passed`
3. Create `demo/README.md` per Spec
4. Run `demo/run_demo.sh` from scratch and confirm 10/10 PASS

### Verification
```bash
# Clean run from scratch
pkill -f start-uc-server 2>/dev/null; sleep 2
bash demo/run_demo.sh

# Expected final lines:
# PASS: C01 AssetType CrusherMotor exists with 3 properties
# PASS: C02 CrusherMotor_CM001 has correct parent
# PASS: C03 CrusherMotor_CM001 has 3 TAG_REFERENCE bindings
# PASS: C04 recursive children of ScreeningPlant_A = 4
# PASS: C05 hierarchy path length = 3
# PASS: C06 hierarchy path root = ScreeningPlant_A
# PASS: C07 hierarchy path leaf = CrusherMotor_CM001
# PASS: C08 list by CrusherMotor type = 2 assets
# PASS: C09 GET asset returns 200
# PASS: C10 DELETE without force returns 409
# 10/10 checks passed
```
