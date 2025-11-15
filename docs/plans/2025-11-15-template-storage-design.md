# Template Storage System Design

**Date:** 2025-11-15
**Status:** Approved

## Overview

Add template storage functionality to allow users to save, list, load, and delete grammatical templates. This includes:
- New database table for templates
- Reorganized API routes split by resource type
- Client UI for managing saved templates

## Requirements

### Functional Requirements
- Save templates with automatic duplicate prevention
- List all saved templates
- Load specific template by ID
- Delete templates by ID
- Templates are globally accessible (no user auth)

### Non-Functional Requirements
- Template string must be unique (prevent duplicates)
- Maintain existing API endpoint compatibility
- Clean route organization by resource type

## Database Design

### New Table: `templates`

```sql
CREATE TABLE IF NOT EXISTS templates (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    template TEXT NOT NULL UNIQUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
```

**Fields:**
- `id`: Auto-incrementing primary key
- `template`: Template string (e.g., "noun(case=nominative,gender=masculine)")
- `created_at`: Automatic timestamp for sorting/display

**Constraints:**
- `UNIQUE(template)` prevents duplicate templates

### Database Module Reorganization

**New Structure:**
```
syntaxis/lib/database/
├── __init__.py          # Exports Database class and template functions
├── schema.py            # All CREATE TABLE statements (add templates table)
├── api.py               # Database class (connection & initialization)
├── templates.py         # NEW - Template CRUD functions
└── seeds/               # Existing seed data
```

**Database Class Responsibilities:**
- Connection management (`_conn` property)
- Schema initialization (calls `schema.create_schema()`)
- Existing word/lexical operations

**New `templates.py` Module:**
```python
def save_template(conn, template: str) -> dict
def list_templates(conn) -> list[dict]
def get_template(conn, template_id: int) -> dict | None
def delete_template(conn, template_id: int) -> bool
```

All functions accept `sqlite3.Connection` as first parameter for consistency with existing patterns.

## API Design

### Route Reorganization

**Current:**
```
syntaxis/service/api/
└── routes.py  # All endpoints
```

**New:**
```
syntaxis/service/api/
├── __init__.py
├── generation.py   # POST /api/v1/generate
├── metadata.py     # GET /api/v1/lexicals/schema, /api/v1/features
└── templates.py    # Template CRUD endpoints
```

### Template Endpoints

**Base Path:** `/api/v1/templates`

| Method | Endpoint | Description | Request | Response |
|--------|----------|-------------|---------|----------|
| POST | `/templates` | Save template | `{"template": "..."}` | `{"id": 1, "template": "...", "created_at": "..."}` |
| GET | `/templates` | List all | - | `[{"id": 1, "template": "...", "created_at": "..."}, ...]` |
| GET | `/templates/{id}` | Get by ID | - | `{"id": 1, "template": "...", "created_at": "..."}` |
| DELETE | `/templates/{id}` | Delete by ID | - | `{"message": "Template deleted"}` |

**Error Handling:**
- POST with duplicate template: 409 Conflict
- GET/DELETE non-existent ID: 404 Not Found
- Invalid template format: 400 Bad Request

### Main App Updates

**`syntaxis/service/app.py`:**
```python
from syntaxis.service.api import generation, metadata, templates

app.include_router(generation.router)
app.include_router(metadata.router)
app.include_router(templates.router)
```

All routers use `APIRouter(prefix="/api/v1", tags=[...])`.

## Client Design

### API Service Layer

**`client/src/services/api.js` - New Functions:**
```javascript
export const saveTemplate = async (template) => { ... }
export const listTemplates = async () => { ... }
export const getTemplate = async (id) => { ... }
export const deleteTemplate = async (id) => { ... }
```

### New View: SavedTemplatesView

**File:** `client/src/views/SavedTemplatesView.vue`

**Features:**
- Display all saved templates in a table/list
- Each row shows: template string, created date
- Actions per template: "Load" button, "Delete" button
- Delete with confirmation dialog
- Load navigates to TemplateBuilderView with template data

**Layout:**
```
┌─────────────────────────────────────────────────────┐
│ Saved Templates                                     │
├─────────────────────────────────────────────────────┤
│ Template String                 Created    Actions  │
├─────────────────────────────────────────────────────┤
│ noun(case=nominative...)        11/15     [Load][X] │
│ verb(tense=present...)          11/14     [Load][X] │
└─────────────────────────────────────────────────────┘
```

### TemplateBuilderView Updates

**`client/src/views/TemplateBuilderView.vue`:**

**New Features:**
- "Save Template" button next to "Generate Sentence"
- Enabled when `store.generatedTemplate` has content
- On save: calls `saveTemplate()` API, shows success notification
- Accept loaded template from route params/query or store

**Save Flow:**
1. User clicks "Save Template"
2. Call API with `store.generatedTemplate`
3. Show success message with template ID
4. Optionally navigate to SavedTemplatesView

**Load Flow:**
1. User clicks "Load" in SavedTemplatesView
2. Navigate to TemplateBuilderView with template string
3. Store parses template and populates groups

### Store Updates

**`client/src/stores/templateBuilder.js`:**

**New Method:**
```javascript
loadTemplate(templateString) {
  // Parse template string
  // Populate groups, lexicals, features
  // Update generatedTemplate
}
```

This method reverse-engineers the template string to populate the builder UI state.

### Router Updates

**`client/src/router/index.js`:**
- Add route: `{ path: '/templates', component: SavedTemplatesView }`
- Optionally add navigation link in app header/sidebar

## Implementation Order

1. **Database Layer**
   - Add templates table to `schema.py`
   - Create `templates.py` with CRUD functions
   - Update `__init__.py` exports

2. **API Routes**
   - Split `routes.py` into `generation.py`, `metadata.py`
   - Create `templates.py` router with all endpoints
   - Update `app.py` to include all routers
   - Add request/response schemas

3. **Client API**
   - Add template functions to `api.js`

4. **Client Views**
   - Create `SavedTemplatesView.vue`
   - Update `TemplateBuilderView.vue` with Save button
   - Add `loadTemplate()` to store
   - Update router

5. **Testing**
   - Test duplicate prevention
   - Test all CRUD operations
   - Test UI save/load/delete flows

## Open Questions

None - design approved.

## Success Criteria

- Templates can be saved without duplicates
- Users can view all saved templates
- Users can load templates back into builder
- Users can delete templates
- Routes are organized by resource type
- All existing functionality remains intact
