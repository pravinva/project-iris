# Unity Catalog Asset Tree Browser

## Overview

The Asset Tree Browser is a React-based web interface for managing and visualizing OT (Operational Technology) assets in Unity Catalog. It follows ISA-95 industrial standards and provides an intuitive hierarchical view of enterprise assets.

## Features

### 1. Asset Tree Visualization
- **Hierarchical Tree View**: Display assets in a collapsible tree structure
- **Lazy Loading**: Load child assets on-demand for optimal performance
- **Icon System**: Visual indicators for different asset types (Enterprise, Site, Motor, Pump, Sensor, etc.)
- **Search Functionality**: Filter assets by name or description
- **Real-time Updates**: Automatic refresh and React Query caching

### 2. Asset Management
- **Create Assets**: Add new assets with type selection and property configuration
- **Edit Assets**: Modify asset properties and relationships
- **Delete Assets**: Remove assets with cascade deletion for children
- **Export/Import**: JSON-based asset hierarchy export and import

### 3. Views and Navigation
- **Tree View**: Hierarchical visualization with expand/collapse
- **Table View**: Flat list with sorting and filtering
- **Asset Details**: Comprehensive view with properties, children, and hierarchy
- **Breadcrumb Navigation**: Easy navigation through asset hierarchy

## Architecture

### Components Structure

```
ui/src/
├── hooks/
│   └── assets.tsx                 # React Query hooks for API calls
├── components/
│   └── AssetTreeBrowser.tsx       # Main tree browser component
├── pages/
│   ├── AssetsList.tsx             # Assets list page with tree/table views
│   └── AssetDetails.tsx           # Individual asset details page
└── App.tsx                        # Route configuration and navigation
```

### Key Components

#### AssetTreeBrowser.tsx
The main tree visualization component with:
- Ant Design Tree component for hierarchical display
- Lazy loading of child nodes
- Search and filter capabilities
- Icon system for asset type visualization
- Integration with React Router for navigation

#### AssetsList.tsx
The assets list page featuring:
- Dual view modes (Tree and Table)
- Asset type filtering
- Batch operations (export/import)
- Quick statistics by asset type
- Integration with schema navigation

#### AssetDetails.tsx
The asset details page providing:
- Complete asset information display
- Properties table
- Child assets list
- Hierarchical position visualization
- CRUD operations (Edit/Delete)

#### assets.tsx (Hooks)
React Query hooks for API operations:
- `useListAssets`: List assets with filters
- `useGetAsset`: Fetch single asset details
- `useCreateAsset`: Create new asset
- `useDeleteAsset`: Delete asset
- `useListChildAssets`: Get child assets
- `useAssetHierarchy`: Build full hierarchy

## API Integration

The UI integrates with Unity Catalog REST API endpoints:

### Asset Endpoints
- `GET /api/2.1/unity-catalog/assets` - List assets
- `POST /api/2.1/unity-catalog/assets` - Create asset
- `GET /api/2.1/unity-catalog/assets/{full_name}` - Get asset
- `DELETE /api/2.1/unity-catalog/assets/{full_name}` - Delete asset
- `GET /api/2.1/unity-catalog/assets/{full_name}/children` - List children

### Asset Type Endpoints
- `GET /api/2.1/unity-catalog/asset-types` - List asset types
- `POST /api/2.1/unity-catalog/asset-types` - Create asset type
- `GET /api/2.1/unity-catalog/asset-types/{full_name}` - Get asset type
- `DELETE /api/2.1/unity-catalog/asset-types/{full_name}` - Delete asset type

## Usage

### Accessing Assets
1. Navigate to any schema in Unity Catalog UI
2. Click on the "Assets" tab or use the "OT Assets" menu item
3. Browse the hierarchical tree or switch to table view
4. Click on any asset to view details

### Creating Assets
1. Click "New Asset" button
2. Select asset type from dropdown
3. Choose parent asset (optional for hierarchy)
4. Define property values
5. Submit to create

### Managing Hierarchy
- **Expand/Collapse**: Click tree node arrows
- **Navigate**: Click asset names to view details
- **Search**: Use search bar to filter assets
- **Filter by Type**: Select asset type from dropdown

## ISA-95 Hierarchy Example

The browser supports standard ISA-95 levels:

```
Enterprise (Level 4)
├── Site/Plant (Level 3)
│   ├── Area (Level 2)
│   │   ├── Work Center (Level 1)
│   │   │   ├── Equipment Module (Level 0)
│   │   │   │   └── Control Module
```

Example with Rio Tinto mining:
```
RioTinto (Enterprise)
├── PilbaraIronOreMine (Site)
│   ├── CrushingPlant (Area)
│   │   ├── CrusherMotor01 (Motor)
│   │   │   ├── TempSensor01 (Sensor)
│   │   │   └── VibSensor01 (Sensor)
│   │   └── ConveyorMotor01 (Motor)
│   └── ProcessingPlant (Area)
│       └── SlurryPump01 (Pump)
│           └── FlowSensor01 (Sensor)
```

## Configuration

### Environment Variables
```env
REACT_APP_API_URL=http://localhost:8080
REACT_APP_GOOGLE_AUTH_ENABLED=false
```

### Theme Customization
The UI uses Ant Design with customizable theme:
- Primary color: #1890ff (blue)
- Success color: #52c41a (green)
- Warning color: #faad14 (orange)
- Error color: #f5222d (red)

## Development

### Running the UI
```bash
cd ui
npm install
npm start
```

### Building for Production
```bash
npm run build
```

### Generating TypeScript Types
```bash
npm run generate:catalog
```

## Future Enhancements

1. **Drag-and-Drop**: Rearrange asset hierarchy
2. **Bulk Operations**: Multi-select for batch updates
3. **Real-time Updates**: WebSocket integration for live updates
4. **Advanced Filtering**: Complex query builder
5. **Visualization**: D3.js-based network graphs
6. **Property Bindings**: Visual editor for lakehouse data bindings
7. **Asset Templates**: Save and reuse asset configurations
8. **Audit Trail**: Track all asset modifications

## Testing

The UI components are designed for testing with:
- React Testing Library for component tests
- Jest for unit tests
- Cypress for end-to-end tests

Example test structure:
```typescript
describe('AssetTreeBrowser', () => {
  it('should display root assets', () => {
    // Test implementation
  });

  it('should load children on expand', () => {
    // Test implementation
  });
});
```

## Troubleshooting

### Common Issues

1. **Assets not loading**: Check server is running on port 8080
2. **CORS errors**: Ensure proxy configuration in package.json
3. **Type errors**: Regenerate types with `npm run generate:catalog`
4. **Tree not expanding**: Verify child_count property in API response

## License

This extension to Unity Catalog follows the same Apache 2.0 license.