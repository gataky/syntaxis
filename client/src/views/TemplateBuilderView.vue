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
          <!-- Lexical Selection -->
          <div class="mb-3">
            <label class="form-label fw-bold">Lexicals</label>

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
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useTemplateBuilderStore } from '../stores/templateBuilder'

const store = useTemplateBuilderStore()
const loading = ref(true)
const selectedLexicals = ref({})
const generatedResult = ref(null)

onMounted(async () => {
  try {
    await store.fetchMetadata()
  } catch (err) {
    console.error('Failed to load metadata:', err)
  } finally {
    loading.value = false
  }
})

function addLexicalToGroup(groupId) {
  const lexType = selectedLexicals.value[groupId]
  if (lexType) {
    store.addLexical(groupId, lexType)
    selectedLexicals.value[groupId] = ''
  }
}

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

async function handleGenerate() {
  try {
    generatedResult.value = await store.generateSentence()
  } catch (err) {
    console.error('Generation failed:', err)
  }
}
</script>

<style scoped>
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
</style>
