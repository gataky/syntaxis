# V2 Template Builder Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Add visual form builder to the client for creating V2 templates through a GUI interface

**Architecture:** Pinia store manages template state, single Vue component handles UI, new backend endpoints provide lexical/feature metadata, backend validates generated templates

**Tech Stack:** Vue 3, Pinia, Bootstrap 5, FastAPI, Python 3.12+

---

## Task 1: Backend API - Lexical Schema Endpoint

**Files:**
- Modify: `syntaxis/service/api/routes.py`
- Test: `tests/service/api/test_routes.py`

**Step 1: Write the failing test**

Add to `tests/service/api/test_routes.py`:

```python
def test_get_lexical_schema(client):
    """Test GET /api/v1/lexicals/schema endpoint."""
    response = client.get("/api/v1/lexicals/schema")

    assert response.status_code == 200
    data = response.json()

    assert "lexicals" in data
    assert "noun" in data["lexicals"]
    assert "required" in data["lexicals"]["noun"]
    assert "case" in data["lexicals"]["noun"]["required"]
    assert "gender" in data["lexicals"]["noun"]["required"]
    assert "number" in data["lexicals"]["noun"]["required"]

    # Verify verb requirements
    assert "verb" in data["lexicals"]
    assert "tense" in data["lexicals"]["verb"]["required"]
    assert "voice" in data["lexicals"]["verb"]["required"]
    assert "person" in data["lexicals"]["verb"]["required"]

    # Verify invariable lexicals
    assert "adverb" in data["lexicals"]
    assert data["lexicals"]["adverb"]["required"] == []
```

**Step 2: Run test to verify it fails**

Run: `pytest tests/service/api/test_routes.py::test_get_lexical_schema -v`

Expected: FAIL with "404 Not Found" or similar

**Step 3: Write minimal implementation**

Add to `syntaxis/service/api/routes.py`:

```python
@router.get("/lexicals/schema")
async def get_lexical_schema():
    """
    Get all lexical types with their required features.

    Returns a mapping of lexical types to their required grammatical features.
    """
    schema = {
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
    return schema
```

**Step 4: Run test to verify it passes**

Run: `pytest tests/service/api/test_routes.py::test_get_lexical_schema -v`

Expected: PASS

**Step 5: Commit**

```bash
git add tests/service/api/test_routes.py syntaxis/service/api/routes.py
git commit -m "feat(api): add lexical schema endpoint

Add GET /api/v1/lexicals/schema endpoint that returns all lexical types
with their required grammatical features. Used by template builder UI."
```

---

## Task 2: Backend API - Features Endpoint

**Files:**
- Modify: `syntaxis/service/api/routes.py`
- Test: `tests/service/api/test_routes.py`

**Step 1: Write the failing test**

Add to `tests/service/api/test_routes.py`:

```python
def test_get_features(client):
    """Test GET /api/v1/features endpoint."""
    response = client.get("/api/v1/features")

    assert response.status_code == 200
    data = response.json()

    # Verify case features
    assert "case" in data
    assert "nom" in data["case"]
    assert "acc" in data["case"]
    assert "gen" in data["case"]
    assert "voc" in data["case"]

    # Verify gender features
    assert "gender" in data
    assert "masc" in data["gender"]
    assert "fem" in data["gender"]
    assert "neut" in data["gender"]

    # Verify number features
    assert "number" in data
    assert "sg" in data["number"]
    assert "pl" in data["number"]

    # Verify tense features
    assert "tense" in data
    assert "present" in data["tense"]
    assert "aorist" in data["tense"]
    assert "paratatikos" in data["tense"]

    # Verify voice features
    assert "voice" in data
    assert "active" in data["voice"]
    assert "passive" in data["voice"]

    # Verify person features
    assert "person" in data
    assert "pri" in data["person"]
    assert "sec" in data["person"]
    assert "ter" in data["person"]
```

**Step 2: Run test to verify it fails**

Run: `pytest tests/service/api/test_routes.py::test_get_features -v`

Expected: FAIL with "404 Not Found" or similar

**Step 3: Write minimal implementation**

Add to `syntaxis/service/api/routes.py`:

```python
@router.get("/features")
async def get_features():
    """
    Get all grammatical feature categories and their possible values.

    Returns a mapping of feature categories to lists of valid values.
    """
    features = {
        "case": ["nom", "acc", "gen", "voc"],
        "gender": ["masc", "fem", "neut"],
        "number": ["sg", "pl"],
        "tense": ["present", "aorist", "paratatikos"],
        "voice": ["active", "passive"],
        "person": ["pri", "sec", "ter"]
    }
    return features
```

**Step 4: Run test to verify it passes**

Run: `pytest tests/service/api/test_routes.py::test_get_features -v`

Expected: PASS

**Step 5: Commit**

```bash
git add tests/service/api/test_routes.py syntaxis/service/api/routes.py
git commit -m "feat(api): add features endpoint

Add GET /api/v1/features endpoint that returns all grammatical feature
categories with their valid values. Used by template builder UI."
```

---

## Task 3: Backend Tests - Verify Endpoints Work Together

**Files:**
- Test: `tests/service/api/test_routes.py`

**Step 1: Write integration test**

Add to `tests/service/api/test_routes.py`:

```python
def test_lexical_schema_and_features_consistency(client):
    """Test that schema required features match available features."""
    schema_response = client.get("/api/v1/lexicals/schema")
    features_response = client.get("/api/v1/features")

    schema = schema_response.json()["lexicals"]
    features = features_response.json()

    # Collect all required feature categories
    required_categories = set()
    for lexical_info in schema.values():
        required_categories.update(lexical_info["required"])

    # Verify all required categories have feature definitions
    for category in required_categories:
        assert category in features, f"Category {category} required but not in features"
        assert len(features[category]) > 0, f"Category {category} has no values"
```

**Step 2: Run test to verify it passes**

Run: `pytest tests/service/api/test_routes.py::test_lexical_schema_and_features_consistency -v`

Expected: PASS (should pass with existing implementation)

**Step 3: Commit**

```bash
git add tests/service/api/test_routes.py
git commit -m "test(api): add integration test for schema/features consistency"
```

---

## Task 4: Client - Install Pinia (if not already installed)

**Files:**
- Modify: `client/package.json`

**Step 1: Check if Pinia is installed**

Run: `cd client && grep -q "pinia" package.json && echo "Already installed" || echo "Not installed"`

**Step 2: Install Pinia if needed**

If not installed, run:
```bash
cd client
npm install pinia
```

**Step 3: Verify installation**

Run: `grep "pinia" package.json`

Expected: See pinia in dependencies

**Step 4: Commit if changes made**

```bash
git add package.json package-lock.json
git commit -m "chore(client): add pinia for state management"
```

---

## Task 5: Client - Setup Pinia Store

**Files:**
- Create: `client/src/stores/templateBuilder.js`
- Modify: `client/src/main.js` (if Pinia not already configured)

**Step 1: Create store file with basic structure**

Create `client/src/stores/templateBuilder.js`:

```javascript
import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import api from '../services/api'

export const useTemplateBuilderStore = defineStore('templateBuilder', () => {
  // State
  const groups = ref([])
  const schema = ref(null)
  const features = ref(null)
  const error = ref(null)
  const nextGroupId = ref(1)

  // Getters
  const generatedTemplate = computed(() => {
    if (groups.value.length === 0) return ''

    return groups.value.map(group => {
      // Build lexicals part: "(noun adjective{fem})"
      const lexicalPart = `(${group.lexicals.map(lex => {
        if (lex.overrides && Object.keys(lex.overrides).length > 0) {
          const overrideStr = Object.values(lex.overrides).filter(v => v).join(':')
          return overrideStr ? `${lex.type}{${overrideStr}}` : lex.type
        }
        return lex.type
      }).join(' ')})`

      // Build features part: "@{nom:masc:sg}" or "@$1"
      const featurePart = group.reference
        ? `@$${group.reference.groupId}`
        : `@{${Object.values(group.features).filter(v => v).join(':')}}`

      return lexicalPart + featurePart
    }).join(' ')
  })

  const requiredFeaturesForGroup = computed(() => {
    return (groupId) => {
      const group = groups.value.find(g => g.id === groupId)
      if (!group || !schema.value) return []

      const required = new Set()
      group.lexicals.forEach(lex => {
        const lexicalSchema = schema.value.lexicals[lex.type]
        if (lexicalSchema) {
          lexicalSchema.required.forEach(cat => required.add(cat))
        }
      })
      return Array.from(required)
    }
  })

  const availableReferences = computed(() => {
    return (groupId) => {
      return groups.value.filter(g => g.id < groupId)
    }
  })

  // Actions
  async function fetchMetadata() {
    try {
      const [schemaData, featuresData] = await Promise.all([
        api.getLexicalSchema(),
        api.getFeatures()
      ])
      schema.value = schemaData
      features.value = featuresData
      error.value = null
    } catch (err) {
      error.value = err.message || 'Failed to fetch metadata'
      throw err
    }
  }

  function addGroup() {
    const newGroup = {
      id: nextGroupId.value++,
      lexicals: [],
      features: {},
      reference: null
    }
    groups.value.push(newGroup)
    return newGroup.id
  }

  function removeGroup(groupId) {
    const index = groups.value.findIndex(g => g.id === groupId)
    if (index !== -1) {
      groups.value.splice(index, 1)
      // Clear references to deleted group
      groups.value.forEach(g => {
        if (g.reference && g.reference.groupId === groupId) {
          g.reference = null
        }
      })
    }
  }

  function addLexical(groupId, lexicalType) {
    const group = groups.value.find(g => g.id === groupId)
    if (group) {
      group.lexicals.push({
        type: lexicalType,
        overrides: null
      })
    }
  }

  function removeLexical(groupId, lexicalIndex) {
    const group = groups.value.find(g => g.id === groupId)
    if (group) {
      group.lexicals.splice(lexicalIndex, 1)
    }
  }

  function setFeature(groupId, category, value) {
    const group = groups.value.find(g => g.id === groupId)
    if (group) {
      group.features[category] = value
    }
  }

  function setReference(groupId, targetGroupId) {
    const group = groups.value.find(g => g.id === groupId)
    if (group) {
      group.reference = { groupId: targetGroupId }
      // Clear features when referencing
      group.features = {}
    }
  }

  function clearReference(groupId) {
    const group = groups.value.find(g => g.id === groupId)
    if (group) {
      group.reference = null
    }
  }

  function setLexicalOverride(groupId, lexicalIndex, overrideFeatures) {
    const group = groups.value.find(g => g.id === groupId)
    if (group && group.lexicals[lexicalIndex]) {
      group.lexicals[lexicalIndex].overrides = overrideFeatures
    }
  }

  async function generateSentence() {
    try {
      const template = generatedTemplate.value
      if (!template) {
        throw new Error('No template to generate')
      }
      const result = await api.generateSentence(template)
      error.value = null
      return result
    } catch (err) {
      error.value = err.response?.data?.detail || err.message || 'Failed to generate sentence'
      throw err
    }
  }

  function resetBuilder() {
    groups.value = []
    error.value = null
    nextGroupId.value = 1
  }

  return {
    // State
    groups,
    schema,
    features,
    error,
    // Getters
    generatedTemplate,
    requiredFeaturesForGroup,
    availableReferences,
    // Actions
    fetchMetadata,
    addGroup,
    removeGroup,
    addLexical,
    removeLexical,
    setFeature,
    setReference,
    clearReference,
    setLexicalOverride,
    generateSentence,
    resetBuilder
  }
})
```

**Step 2: Verify Pinia is configured in main.js**

Check `client/src/main.js` for:
```javascript
import { createPinia } from 'pinia'
const pinia = createPinia()
app.use(pinia)
```

If not present, add it.

**Step 3: Commit**

```bash
git add client/src/stores/templateBuilder.js client/src/main.js
git commit -m "feat(client): add template builder Pinia store

Create store for managing template builder state including groups,
lexicals, features, and references. Includes computed template
generation and all mutation actions."
```

---

## Task 6: Client - Extend API Service

**Files:**
- Modify: `client/src/services/api.js`

**Step 1: Add new API methods**

Add to `client/src/services/api.js`:

```javascript
async getLexicalSchema() {
  const response = await axios.get('http://localhost:5000/api/v1/lexicals/schema')
  return response.data
}

async getFeatures() {
  const response = await axios.get('http://localhost:5000/api/v1/features')
  return response.data
}
```

**Step 2: Verify existing generateSentence method exists**

Ensure this exists (should already be there):
```javascript
async generateSentence(template) {
  const response = await axios.post('http://localhost:5000/api/v1/generate', { template })
  return response.data
}
```

**Step 3: Commit**

```bash
git add client/src/services/api.js
git commit -m "feat(client): add API methods for schema and features

Add getLexicalSchema() and getFeatures() methods to fetch metadata
needed by template builder."
```

---

## Task 7: Client - Create Template Builder Component (Part 1: Setup)

**Files:**
- Create: `client/src/views/TemplateBuilderView.vue`

**Step 1: Create component file with basic structure**

Create `client/src/views/TemplateBuilderView.vue`:

```vue
<template>
  <div class="container mt-4">
    <h1 class="mb-4">Template Builder</h1>

    <!-- Loading State -->
    <div v-if="loading" class="alert alert-info">
      Loading metadata...
    </div>

    <!-- Error Display -->
    <div v-if="store.error" class="alert alert-danger alert-dismissible fade show" role="alert">
      <strong>Error:</strong> {{ store.error }}
      <button type="button" class="btn-close" @click="store.error = null"></button>
    </div>

    <!-- Main Content (will be added in next steps) -->
    <div v-if="!loading">
      <p class="text-muted">Template builder UI will go here</p>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useTemplateBuilderStore } from '../stores/templateBuilder'

const store = useTemplateBuilderStore()
const loading = ref(true)

onMounted(async () => {
  try {
    await store.fetchMetadata()
  } catch (err) {
    console.error('Failed to load metadata:', err)
  } finally {
    loading.value = false
  }
})
</script>

<style scoped>
/* Component-specific styles will go here */
</style>
```

**Step 2: Commit**

```bash
git add client/src/views/TemplateBuilderView.vue
git commit -m "feat(client): create template builder view skeleton

Add basic component structure with loading state and error handling."
```

---

## Task 8: Client - Template Builder Component (Part 2: Group List)

**Files:**
- Modify: `client/src/views/TemplateBuilderView.vue`

**Step 1: Add group list section**

Replace the "Main Content" comment section in template with:

```vue
    <!-- Main Content -->
    <div v-if="!loading">
      <!-- Groups List -->
      <div v-if="store.groups.length === 0" class="alert alert-secondary">
        No groups yet. Click "Add Group" to start building your template.
      </div>

      <div v-for="(group, index) in store.groups" :key="group.id" class="card mb-3">
        <div class="card-header d-flex justify-content-between align-items-center">
          <span>
            <span class="badge bg-secondary me-2">Group {{ index + 1 }}</span>
            <small class="text-muted">(ID: {{ group.id }})</small>
          </span>
          <button
            type="button"
            class="btn btn-danger btn-sm"
            @click="store.removeGroup(group.id)"
          >
            Remove Group
          </button>
        </div>
        <div class="card-body">
          <!-- Group content will be added next -->
          <p class="text-muted">Group {{ group.id }} configuration will go here</p>
        </div>
      </div>

      <!-- Add Group Button -->
      <button
        type="button"
        class="btn btn-secondary mb-3"
        @click="store.addGroup()"
      >
        + Add Group
      </button>

      <!-- Live Preview Section -->
      <div class="card mb-3">
        <div class="card-header">Live Preview</div>
        <div class="card-body">
          <pre class="mb-0"><code>{{ store.generatedTemplate || '(empty)' }}</code></pre>
        </div>
      </div>

      <!-- Generate Button -->
      <button
        type="button"
        class="btn btn-primary"
        :disabled="!store.generatedTemplate"
        @click="handleGenerate"
      >
        Generate Sentence
      </button>
    </div>
```

**Step 2: Add handleGenerate method**

Add to script section:

```javascript
const generatedResult = ref(null)

async function handleGenerate() {
  try {
    generatedResult.value = await store.generateSentence()
  } catch (err) {
    console.error('Generation failed:', err)
  }
}
```

Update imports:
```javascript
import { ref, onMounted } from 'vue'
```

**Step 3: Commit**

```bash
git add client/src/views/TemplateBuilderView.vue
git commit -m "feat(client): add group list and controls

Add group cards, add/remove buttons, live preview, and generate button."
```

---

## Task 9: Client - Template Builder Component (Part 3: Lexical Selection)

**Files:**
- Modify: `client/src/views/TemplateBuilderView.vue`

**Step 1: Add lexical selection UI**

Replace "Group content will be added next" section with:

```vue
          <!-- Lexical Selection -->
          <div class="mb-3">
            <label class="form-label fw-bold">Lexicals</label>

            <!-- Selected Lexicals List -->
            <div v-if="group.lexicals.length > 0" class="mb-2">
              <div
                v-for="(lexical, lexIndex) in group.lexicals"
                :key="lexIndex"
                class="d-flex align-items-center mb-2"
              >
                <span class="badge bg-primary me-2">{{ lexical.type }}</span>
                <button
                  type="button"
                  class="btn btn-sm btn-outline-danger"
                  @click="store.removeLexical(group.id, lexIndex)"
                >
                  Remove
                </button>
              </div>
            </div>

            <!-- Add Lexical Dropdown -->
            <div class="input-group" style="max-width: 300px;">
              <select
                class="form-select"
                v-model="selectedLexicals[group.id]"
              >
                <option value="">-- Select lexical --</option>
                <option
                  v-for="lexType in Object.keys(store.schema.lexicals)"
                  :key="lexType"
                  :value="lexType"
                >
                  {{ lexType }}
                </option>
              </select>
              <button
                type="button"
                class="btn btn-secondary"
                :disabled="!selectedLexicals[group.id]"
                @click="addLexicalToGroup(group.id)"
              >
                Add
              </button>
            </div>
          </div>
```

**Step 2: Add reactive state and helper function**

Add to script section:

```javascript
const selectedLexicals = ref({})

function addLexicalToGroup(groupId) {
  const lexType = selectedLexicals.value[groupId]
  if (lexType) {
    store.addLexical(groupId, lexType)
    selectedLexicals.value[groupId] = ''
  }
}
```

**Step 3: Commit**

```bash
git add client/src/views/TemplateBuilderView.vue
git commit -m "feat(client): add lexical selection UI

Add dropdown to select and add lexicals to groups, display selected
lexicals with remove buttons."
```

---

## Task 10: Client - Template Builder Component (Part 4: Reference Control)

**Files:**
- Modify: `client/src/views/TemplateBuilderView.vue`

**Step 1: Add reference control UI**

Add after lexical selection section:

```vue
          <!-- Reference Control -->
          <div class="mb-3">
            <div class="form-check mb-2">
              <input
                type="checkbox"
                class="form-check-input"
                :id="`ref-check-${group.id}`"
                :checked="group.reference !== null"
                :disabled="store.availableReferences(group.id).length === 0"
                @change="toggleReference(group.id, $event.target.checked)"
              >
              <label class="form-check-label" :for="`ref-check-${group.id}`">
                Reference previous group
              </label>
            </div>

            <!-- Reference Selector -->
            <div v-if="group.reference !== null" style="max-width: 300px;">
              <select
                class="form-select"
                :value="group.reference.groupId"
                @change="store.setReference(group.id, parseInt($event.target.value))"
              >
                <option
                  v-for="refGroup in store.availableReferences(group.id)"
                  :key="refGroup.id"
                  :value="refGroup.id"
                >
                  Group {{ store.groups.findIndex(g => g.id === refGroup.id) + 1 }}
                </option>
              </select>
            </div>
          </div>
```

**Step 2: Add toggle function**

Add to script section:

```javascript
function toggleReference(groupId, enabled) {
  if (enabled) {
    const availableRefs = store.availableReferences(groupId)
    if (availableRefs.length > 0) {
      store.setReference(groupId, availableRefs[0].id)
    }
  } else {
    store.clearReference(groupId)
  }
}
```

**Step 3: Commit**

```bash
git add client/src/views/TemplateBuilderView.vue
git commit -m "feat(client): add reference control UI

Add checkbox and dropdown to enable group references to previous groups."
```

---

## Task 11: Client - Template Builder Component (Part 5: Feature Selection)

**Files:**
- Modify: `client/src/views/TemplateBuilderView.vue`

**Step 1: Add feature dropdowns UI**

Add after reference control section:

```vue
          <!-- Feature Selection -->
          <div v-if="!group.reference" class="mb-3">
            <label class="form-label fw-bold">Features</label>

            <div
              v-for="category in store.requiredFeaturesForGroup(group.id)"
              :key="category"
              class="mb-2"
            >
              <label :for="`feature-${group.id}-${category}`" class="form-label text-capitalize">
                {{ category }}:
              </label>
              <select
                :id="`feature-${group.id}-${category}`"
                class="form-select"
                style="max-width: 300px;"
                :value="group.features[category] || ''"
                @change="store.setFeature(group.id, category, $event.target.value)"
              >
                <option value="">-- Select {{ category }} --</option>
                <option
                  v-for="value in store.features[category]"
                  :key="value"
                  :value="value"
                >
                  {{ value }}
                </option>
              </select>
            </div>

            <div v-if="store.requiredFeaturesForGroup(group.id).length === 0" class="text-muted">
              <em>Add lexicals to see feature options</em>
            </div>
          </div>

          <div v-else class="mb-3">
            <p class="text-muted"><em>Features inherited from referenced group</em></p>
          </div>
```

**Step 2: Commit**

```bash
git add client/src/views/TemplateBuilderView.vue
git commit -m "feat(client): add feature selection UI

Add dynamic feature dropdowns based on required features for selected
lexicals. Hide when group uses reference."
```

---

## Task 12: Client - Template Builder Component (Part 6: Lexical Overrides)

**Files:**
- Modify: `client/src/views/TemplateBuilderView.vue`

**Step 1: Add override UI within lexical list**

Modify the selected lexicals list section to include overrides:

```vue
            <!-- Selected Lexicals List -->
            <div v-if="group.lexicals.length > 0" class="mb-2">
              <div
                v-for="(lexical, lexIndex) in group.lexicals"
                :key="lexIndex"
                class="mb-3 border rounded p-2"
              >
                <div class="d-flex align-items-center mb-2">
                  <span class="badge bg-primary me-2">{{ lexical.type }}</span>
                  <button
                    type="button"
                    class="btn btn-sm btn-outline-danger me-2"
                    @click="store.removeLexical(group.id, lexIndex)"
                  >
                    Remove
                  </button>
                  <button
                    type="button"
                    class="btn btn-sm btn-outline-secondary"
                    @click="toggleOverride(group.id, lexIndex)"
                  >
                    {{ lexical.overrides ? 'Disable Override' : 'Enable Override' }}
                  </button>
                </div>

                <!-- Override Controls -->
                <div v-if="lexical.overrides" class="ms-3">
                  <label class="form-label fw-bold small">Override Features:</label>
                  <div
                    v-for="category in getLexicalRequiredFeatures(lexical.type)"
                    :key="category"
                    class="mb-2"
                  >
                    <label class="form-label small text-capitalize">
                      {{ category }}:
                    </label>
                    <select
                      class="form-select form-select-sm"
                      style="max-width: 200px;"
                      :value="lexical.overrides[category] || ''"
                      @change="updateOverride(group.id, lexIndex, category, $event.target.value)"
                    >
                      <option value="">-- Select {{ category }} --</option>
                      <option
                        v-for="value in store.features[category]"
                        :key="value"
                        :value="value"
                      >
                        {{ value }}
                      </option>
                    </select>
                  </div>
                </div>
              </div>
            </div>
```

**Step 2: Add helper functions**

Add to script section:

```javascript
function toggleOverride(groupId, lexicalIndex) {
  const group = store.groups.find(g => g.id === groupId)
  const lexical = group.lexicals[lexicalIndex]

  if (lexical.overrides) {
    store.setLexicalOverride(groupId, lexicalIndex, null)
  } else {
    store.setLexicalOverride(groupId, lexicalIndex, {})
  }
}

function getLexicalRequiredFeatures(lexicalType) {
  if (!store.schema) return []
  const lexicalSchema = store.schema.lexicals[lexicalType]
  return lexicalSchema ? lexicalSchema.required : []
}

function updateOverride(groupId, lexicalIndex, category, value) {
  const group = store.groups.find(g => g.id === groupId)
  const lexical = group.lexicals[lexicalIndex]

  const newOverrides = { ...lexical.overrides }
  if (value) {
    newOverrides[category] = value
  } else {
    delete newOverrides[category]
  }

  store.setLexicalOverride(groupId, lexicalIndex, newOverrides)
}
```

**Step 3: Commit**

```bash
git add client/src/views/TemplateBuilderView.vue
git commit -m "feat(client): add lexical override controls

Add ability to enable overrides on individual lexicals and configure
override features separately from group features."
```

---

## Task 13: Client - Template Builder Component (Part 7: Result Display)

**Files:**
- Modify: `client/src/views/TemplateBuilderView.vue`

**Step 1: Add result display section**

Add after the Generate Button:

```vue
      <!-- Generated Result -->
      <div v-if="generatedResult" class="card mt-4">
        <div class="card-header d-flex justify-content-between align-items-center">
          <span>Generated Sentence</span>
          <button
            type="button"
            class="btn-close"
            @click="generatedResult = null"
          ></button>
        </div>
        <div class="card-body">
          <div class="mb-3">
            <strong>Template:</strong>
            <code>{{ generatedResult.template }}</code>
          </div>

          <div>
            <strong>Words:</strong>
            <div class="mt-2">
              <div
                v-for="(lexical, index) in generatedResult.lexicals"
                :key="index"
                class="mb-3"
              >
                <div class="d-flex align-items-baseline">
                  <span class="badge bg-info me-2">{{ lexical.pos }}</span>
                  <span class="fs-4 me-3">{{ lexical.word.join(', ') }}</span>
                  <span class="text-muted">{{ lexical.translations.join(', ') }}</span>
                </div>
                <div class="text-muted small ms-5">
                  Lemma: {{ lexical.lemma }}
                  <span v-if="Object.keys(lexical.features).length > 0">
                    | Features: {{ Object.entries(lexical.features).map(([k,v]) => `${k}:${v}`).join(', ') }}
                  </span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
```

**Step 2: Commit**

```bash
git add client/src/views/TemplateBuilderView.vue
git commit -m "feat(client): add result display section

Display generated sentence with Greek words, translations, and
grammatical features after successful generation."
```

---

## Task 14: Client - Add Routing

**Files:**
- Modify: `client/src/router/index.js`

**Step 1: Add builder route**

Add to routes array in `client/src/router/index.js`:

```javascript
{
  path: '/builder',
  name: 'builder',
  component: () => import('../views/TemplateBuilderView.vue')
}
```

**Step 2: Verify route works**

Run: `cd client && npm run dev`

Visit: `http://localhost:5173/builder`

Expected: Builder page loads without errors

**Step 3: Commit**

```bash
git add client/src/router/index.js
git commit -m "feat(client): add template builder route

Add /builder route to router configuration."
```

---

## Task 15: Client - Add Navigation Link

**Files:**
- Modify: `client/src/App.vue` (or navigation component if exists)

**Step 1: Find navigation section**

Look for navbar or navigation menu in `client/src/App.vue`.

**Step 2: Add Template Builder link**

Add link to navigation (exact location depends on existing structure):

```vue
<router-link to="/builder" class="nav-link">Template Builder</router-link>
```

**Step 3: Verify navigation works**

Visit app and click "Template Builder" link.

Expected: Navigates to `/builder` route

**Step 4: Commit**

```bash
git add client/src/App.vue
git commit -m "feat(client): add template builder navigation link

Add link to template builder in main navigation."
```

---

## Task 16: Manual End-to-End Test

**Files:**
- None (manual testing)

**Step 1: Start backend server**

Run:
```bash
cd /Users/jeff/Documents/syntaxis
python -m syntaxis.service.api.main
```

Expected: Server starts on port 5000

**Step 2: Start frontend dev server**

Run:
```bash
cd /Users/jeff/Documents/syntaxis/client
npm run dev
```

Expected: Client starts on port 5173

**Step 3: Test complete flow**

1. Navigate to `http://localhost:5173/builder`
2. Click "Add Group"
3. Select "noun" from lexical dropdown, click "Add"
4. Select features: case=nom, gender=masc, number=sg
5. Verify live preview shows: `(noun)@{nom:masc:sg}`
6. Click "Generate Sentence"
7. Verify Greek sentence appears with translations

**Step 4: Test references**

1. Click "Add Group" again
2. Add "verb" to Group 2
3. Check "Reference previous group" checkbox
4. Verify live preview shows: `(noun)@{nom:masc:sg} (verb)@$1`
5. Click "Generate Sentence"
6. Verify results

**Step 5: Test overrides**

1. In Group 1, click "Enable Override" on noun
2. Set override feature (e.g., case=acc)
3. Verify live preview shows: `(noun{acc})@{nom:masc:sg}`
4. Generate and verify

**Step 6: Document any issues**

Note any bugs or unexpected behavior.

---

## Task 17: Add Basic Styling

**Files:**
- Modify: `client/src/views/TemplateBuilderView.vue`

**Step 1: Add component styles**

Add to `<style scoped>` section:

```css
.card {
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}

.card-header {
  background-color: #f8f9fa;
  font-weight: 600;
}

pre code {
  font-family: 'Courier New', monospace;
  font-size: 0.95rem;
}

.badge {
  font-size: 0.85rem;
  padding: 0.35em 0.65em;
}

.form-label {
  margin-bottom: 0.25rem;
  font-size: 0.95rem;
}

.text-capitalize {
  text-transform: capitalize;
}
```

**Step 2: Verify styling looks clean**

Check that cards, badges, and forms look polished.

**Step 3: Commit**

```bash
git add client/src/views/TemplateBuilderView.vue
git commit -m "style(client): add styling to template builder

Add scoped styles for better visual appearance of builder UI."
```

---

## Task 18: Final Testing and Documentation

**Files:**
- Modify: `README.md` (if builder should be documented)

**Step 1: Run full test suite**

Backend tests:
```bash
cd /Users/jeff/Documents/syntaxis
pytest tests/service/api/test_routes.py -v
```

Expected: All tests pass

**Step 2: Test error handling**

1. Try generating with empty template
2. Try generating invalid template (e.g., missing required features)
3. Verify error messages display correctly

**Step 3: Add README section (optional)**

If desired, add to README:

```markdown
## Template Builder

The web client includes a visual template builder at `/builder` that allows you to:
- Build V2 templates using a form-based interface
- Configure groups, lexicals, and grammatical features
- Set group references and lexical overrides
- See live preview of generated V2 syntax
- Generate and test sentences immediately

Visit `http://localhost:5173/builder` after starting the dev server.
```

**Step 4: Final commit**

```bash
git add README.md
git commit -m "docs: document template builder feature

Add documentation for new visual template builder in README."
```

---

## Task 19: Create Pull Request

**Files:**
- None (git operations)

**Step 1: Push feature branch**

Run:
```bash
git push -u origin feature/v2-template-builder
```

**Step 2: Create pull request**

Use GitHub CLI or web interface:
```bash
gh pr create --title "Add V2 Template Builder" --body "$(cat <<'EOF'
## Summary
Add visual form builder to the client for creating V2 templates through a GUI interface.

## Changes
- **Backend**: New API endpoints for lexical schema and features metadata
- **Frontend**: Pinia store for state management
- **Frontend**: Complete template builder UI with all V2 features
- **Frontend**: New `/builder` route and navigation

## Features
- Sequential group addition with visual cards
- Dynamic feature selection based on lexicals
- Group references (@$1, @$2, etc.)
- Lexical-level feature overrides
- Live V2 syntax preview
- Integration with sentence generation API

## Testing
- Backend endpoint tests added
- Manual end-to-end testing completed
- Error handling verified

## Screenshots
[Add screenshots if desired]

🤖 Generated with [Claude Code](https://claude.com/claude-code)
EOF
)"
```

**Step 3: Done!**

Feature is complete and ready for review.

---

## Summary

This implementation adds a complete visual template builder to the Syntaxis client:

**Backend (3 tasks):**
- GET /api/v1/lexicals/schema - Returns lexical types with required features
- GET /api/v1/features - Returns all grammatical feature categories
- Tests for both endpoints

**Frontend (16 tasks):**
- Pinia store with complete state management
- Single-file Vue component with all UI
- Group management (add/remove)
- Lexical selection
- Reference controls
- Feature dropdowns (dynamic based on lexicals)
- Lexical override controls
- Live V2 syntax preview
- Result display
- Routing and navigation
- Styling
- Error handling

**Key Principles Applied:**
- **TDD**: Backend endpoints tested first
- **YAGNI**: No unnecessary features (no client validation, no drag-drop)
- **DRY**: Store handles all business logic, component is pure UI
- **Separation of Concerns**: Backend validates, frontend builds UI

**Total Tasks**: 19 (estimated 3-4 hours for experienced developer)
