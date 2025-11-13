# V2 Template Builder Design

**Date:** 2025-11-12
**Status:** Approved
**Goal:** Add visual form builder to the client for creating V2 templates without typing syntax

## Overview

This design adds a visual template builder to the Vue.js client that enables users to construct V2 templates through a form-based interface. The builder focuses on speed and convenience for frequent users, providing a faster way to create templates than manual typing while showing live V2 syntax preview.

## Requirements

### Functional Requirements
1. Visual form builder with sequential group addition
2. Support for all V2 template features (groups, references, overrides)
3. Live preview of generated V2 template syntax
4. Integration with existing sentence generation API
5. Support for group references (@$1, @$2, etc.)
6. Support for lexical-level feature overrides (e.g., `noun{fem}`)
7. Standalone route separate from existing manual input

### Non-Functional Requirements
1. No changes to existing TranslationExerciseView
2. Backend handles all template validation
3. Simple, Bootstrap-based UI consistent with existing app
4. Metadata (lexicals, features) fetched from backend

## Architecture

### High-Level Design

**Two-Part Architecture:**

1. **Pinia Store** - Manages template state and business logic
2. **Vue Component** - Single-file component handling all UI

**Data Flow:**
```
User Action → Store Action → State Update → Getter Recomputes → UI Updates
```

### New Backend API Endpoints

#### 1. GET /api/v1/lexicals/schema
Returns all lexical types with their required features.

**Response:**
```json
{
  "lexicals": {
    "noun": {"required": ["case", "gender", "number"]},
    "verb": {"required": ["tense", "voice", "person", "number"]},
    "adjective": {"required": ["case", "gender", "number"]},
    "article": {"required": ["case", "gender", "number"]},
    "pronoun": {"required": ["case", "person", "number"]},
    "adverb": {"required": []},
    "preposition": {"required": []},
    "conjunction": {"required": []},
    "numeral": {"required": []}
  }
}
```

**Implementation:** Read from existing `constants.py`

#### 2. GET /api/v1/features
Returns all feature categories and their possible values.

**Response:**
```json
{
  "case": ["nom", "acc", "gen", "voc"],
  "gender": ["masc", "fem", "neut"],
  "number": ["sg", "pl"],
  "tense": ["present", "aorist", "paratatikos"],
  "voice": ["active", "passive"],
  "person": ["pri", "sec", "ter"]
}
```

**Implementation:** Read from existing `constants.py`

### Frontend Architecture

#### File Structure
```
client/src/
  stores/
    templateBuilder.js        # Pinia store
  views/
    TemplateBuilderView.vue   # Main component (single file)
  services/
    api.js                     # Add getLexicalSchema(), getFeatures()
  router/
    index.js                   # Add /builder route
```

#### Pinia Store Schema

**State:**
```javascript
{
  groups: [
    {
      id: 1,                    // Auto-incrementing ID
      lexicals: [
        {
          type: 'noun',
          overrides: null       // or { case: 'acc', gender: 'fem' }
        },
        {
          type: 'adjective',
          overrides: null
        }
      ],
      features: {
        case: 'nom',
        gender: 'masc',
        number: 'sg'
      },
      reference: null           // or { groupId: 1 }
    }
  ],
  schema: null,                 // Fetched lexical schema
  features: null,               // Fetched feature categories
  error: null                   // API error message
}
```

**Key Getters:**

1. `generatedTemplate` - Computes V2 syntax string
   - Example: `"(noun adjective)@{nom:masc:sg} (verb)@$1"`

2. `requiredFeaturesForGroup(groupId)` - Union of required features for group's lexicals
   - Example: For [noun, adjective] returns `['case', 'gender', 'number']`

3. `availableReferences(groupId)` - Returns referenceable groups (ID < groupId)

**Key Actions:**

1. `fetchMetadata()` - Load schema + features from API
2. `addGroup()` - Append new empty group
3. `removeGroup(groupId)` - Delete group
4. `addLexical(groupId, lexicalType)` - Add lexical to group
5. `removeLexical(groupId, lexicalIndex)` - Remove lexical
6. `setFeature(groupId, category, value)` - Set group feature
7. `setReference(groupId, targetGroupId)` - Set group reference
8. `clearReference(groupId)` - Remove reference
9. `setLexicalOverride(groupId, lexicalIndex, features)` - Set override features
10. `generateSentence()` - Call API with generated template

#### Template Generation Algorithm

**In `generatedTemplate` getter:**

```javascript
groups.map(group => {
  // Build lexicals part: "(noun adjective{fem})"
  const lexicalPart = `(${group.lexicals.map(lex => {
    if (lex.overrides && Object.keys(lex.overrides).length > 0) {
      const overrideStr = Object.entries(lex.overrides)
        .map(([k, v]) => v)
        .join(':');
      return `${lex.type}{${overrideStr}}`;
    }
    return lex.type;
  }).join(' ')})`;

  // Build features part: "@{nom:masc:sg}" or "@$1"
  const featurePart = group.reference
    ? `@$${group.reference.groupId}`
    : `@{${Object.values(group.features).join(':')}}`;

  return lexicalPart + featurePart;
}).join(' ');
```

## Component Design

### UI Layout

```
┌─────────────────────────────────────────┐
│ Template Builder                         │
├─────────────────────────────────────────┤
│ ┌─────────────────────────────────────┐ │
│ │ Group 1                             │ │
│ │ Lexicals: [noun ▼] [+ Add Lexical] │ │
│ │ ☐ Reference previous group          │ │
│ │ Features:                           │ │
│ │   Case: [nom ▼] Gender: [masc ▼]   │ │
│ │   Number: [sg ▼]                    │ │
│ │                                     │ │
│ │ Lexical Overrides:                  │ │
│ │   • noun [Override ▼]               │ │
│ │     ☐ Enable override               │ │
│ │                                     │ │
│ │                        [Remove Group]│ │
│ └─────────────────────────────────────┘ │
│                                          │
│ [+ Add Group]                            │
│                                          │
│ ┌─────────────────────────────────────┐ │
│ │ Live Preview:                       │ │
│ │ (noun)@{nom:masc:sg}                │ │
│ └─────────────────────────────────────┘ │
│                                          │
│ [Generate Sentence]                      │
└─────────────────────────────────────────┘
```

### Component Sections

1. **Group List** - Sequential card-based display
   - Each group in a Bootstrap card
   - Group number badge (Group 1, Group 2, etc.)
   - All controls contained in card body

2. **Lexical Selection**
   - Dropdown to add lexicals to group
   - List of selected lexicals with remove buttons
   - Each lexical has collapsible override controls

3. **Reference Control**
   - Checkbox: "Reference previous group"
   - When checked: dropdown of previous groups
   - When checked: feature dropdowns disabled

4. **Feature Dropdowns** (Bootstrap `form-select`)
   - Dynamic based on selected lexicals
   - Only show categories needed by lexicals in group
   - Example: [noun, adjective] → show case, gender, number
   - Example: [verb] → show tense, voice, person, number

5. **Lexical Overrides**
   - Collapsible section under each lexical
   - Checkbox "Enable override"
   - When enabled: feature dropdowns for that lexical only

6. **Live Preview**
   - Read-only text display (monospace font)
   - Updates in real-time via `generatedTemplate` getter
   - Shows complete V2 syntax

7. **Action Buttons**
   - "Add Group" - appends new group
   - "Remove Group" - deletes group
   - "Generate Sentence" - calls API

### Bootstrap Components Used

- `card`, `card-body`, `card-header` - Group containers
- `form-select` - All dropdowns
- `form-check`, `form-check-input` - Checkboxes
- `btn btn-primary` - Generate button
- `btn btn-secondary` - Add group button
- `btn btn-danger btn-sm` - Remove buttons
- `alert alert-danger` - Error messages
- `badge bg-secondary` - Group numbers

## Validation & Error Handling

### Client-Side Validation

**Minimal - enforced by UI constraints only:**

1. Empty groups prevented by UI (can't configure without lexicals)
2. Reference dropdown only shows valid previous groups
3. Feature dropdowns only show valid values from schema

**No explicit validation checks** - backend handles all validation logic.

### Backend Validation

When user clicks "Generate Sentence":
1. Client sends generated V2 template to `/api/v1/generate`
2. Backend V2Parser validates
3. On error: returns detailed error message
4. Client displays error in alert banner

**Error Display:**
```
┌─────────────────────────────────────────┐
│ ⚠️ Template Error:                      │
│ Missing required feature 'case' for     │
│ lexical 'noun' in group 1               │
└─────────────────────────────────────────┘
```

### Edge Cases

1. **Deleting referenced group:**
   - Update subsequent group IDs in references
   - Clear invalid references (point to deleted group)
   - Show warning to user

2. **Empty template:**
   - "Add Group" button is primary action when empty
   - Generate button disabled if no groups

3. **Reference when features disabled:**
   - When reference checkbox checked, disable feature dropdowns
   - Clear any previously set features (inherited from reference)

## Integration

### Routing

**New Route:** `/builder` → `TemplateBuilderView.vue`

**Router Configuration:**
```javascript
{
  path: '/builder',
  name: 'builder',
  component: TemplateBuilderView
}
```

**Navigation:**
- Add "Template Builder" link to app navigation
- Standalone view (no changes to existing `/exercise` route)

### Shared Code

- Use existing `api.generateSentence()` from `services/api.js`
- Can optionally use `ExerciseDisplay.vue` to show results
- Store isolated to builder (no impact on exercise view)

### API Service Extensions

**Add to `services/api.js`:**
```javascript
async getLexicalSchema() {
  const response = await axios.get('/api/v1/lexicals/schema');
  return response.data;
}

async getFeatures() {
  const response = await axios.get('/api/v1/features');
  return response.data;
}
```

**Existing method (unchanged):**
```javascript
async generateSentence(template) {
  const response = await axios.post('/api/v1/generate', { template });
  return response.data;
}
```

## User Flow

1. User navigates to `/builder`
2. Component mounts, calls `store.fetchMetadata()`
3. Fetches schema and features from new API endpoints
4. User clicks "Add Group"
5. User selects lexical(s) from dropdown (e.g., "noun")
6. Feature dropdowns appear dynamically (case, gender, number)
7. User selects feature values
8. Live preview updates: `(noun)@{nom:masc:sg}`
9. User optionally:
   - Adds more groups
   - Sets group references
   - Configures lexical overrides
10. User clicks "Generate Sentence"
11. Store calls `api.generateSentence(store.generatedTemplate)`
12. On success: Display Greek sentence and translations
13. On error: Display error message from backend

## Success Criteria

1. Users can build valid V2 templates without knowing syntax
2. All V2 features supported (groups, references, overrides)
3. Live preview shows correct V2 template string
4. Generated sentences match manual template results
5. Clean, intuitive Bootstrap UI
6. No impact on existing exercise view
7. Backend remains single source of truth for validation

## Future Enhancements (Out of Scope)

1. Client-side validation for better UX (show errors before generate)
2. Template save/load functionality
3. Template library of common patterns
4. Hybrid mode (visual builder + text editor that sync)
5. Syntax highlighting in live preview
6. Undo/redo for group operations
7. Drag-and-drop group reordering

## Implementation Notes

- Use Vue 3 Composition API (consistent with existing code)
- Pinia store for state management
- Bootstrap 5 for styling (already in project)
- Axios for API calls (already configured)
- Single component approach for simplicity
- Backend endpoints read from existing `constants.py`
