<template>
  <div class="container mt-4">
    <div class="d-flex justify-content-between align-items-center mb-4">
      <h1 class="mb-0">Template Builder</h1>
      <button type="button" class="btn btn-outline-info" @click="showHelp = true">
        <span class="me-1">?</span> Syntax Help
      </button>
    </div>

    <!-- Loading State -->
    <div v-if="loading" class="alert alert-info">
      Loading metadata...
    </div>

    <!-- Error Display -->
    <div v-if="store.error" class="alert alert-danger alert-dismissible fade show" role="alert">
      <strong>Error:</strong> {{ store.error }}
      <button type="button" class="btn-close" @click="store.error = null"></button>
    </div>

    <!-- Success Display -->
    <div v-if="saveSuccess" class="alert alert-success alert-dismissible fade show" role="alert">
      <strong>Success:</strong> {{ saveSuccess }}
      <button type="button" class="btn-close" @click="saveSuccess = null"></button>
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
                        {{ formatFeatureValue(value, category) }}
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

            <!-- Required Features -->
            <div
              v-for="category in store.requiredFeaturesForGroup(group.id)"
              :key="category"
              class="mb-2"
            >
              <label :for="`feature-${group.id}-${category}`" class="form-label text-capitalize">
                {{ category }}<span class="text-danger">*</span>:
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
                  {{ formatFeatureValue(value, category) }}
                </option>
              </select>
            </div>

            <!-- Optional Features -->
            <div
              v-for="category in store.optionalFeaturesForGroup(group.id)"
              :key="`optional-${category}`"
              class="mb-2"
            >
              <label :for="`feature-${group.id}-${category}`" class="form-label text-capitalize">
                {{ category }} <span class="text-muted small">(optional)</span>:
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
                  {{ formatFeatureValue(value, category) }}
                </option>
              </select>
            </div>

            <div v-if="store.requiredFeaturesForGroup(group.id).length === 0 && store.optionalFeaturesForGroup(group.id).length === 0" class="text-muted">
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
      <button
        type="button"
        class="btn btn-success ms-2"
        :disabled="!store.generatedTemplate"
        @click="handleSave"
      >
        Save Template
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

    <!-- Help Modal -->
    <div
      v-if="showHelp"
      class="modal fade show d-block"
      tabindex="-1"
      style="background-color: rgba(0, 0, 0, 0.5);"
    >
      <div class="modal-dialog modal-lg">
        <div class="modal-content">
          <div class="modal-header">
            <h5 class="modal-title">Template Syntax Cheat Sheet</h5>
            <button type="button" class="btn-close" @click="showHelp = false"></button>
          </div>
          <div class="modal-body">
            <h6 class="fw-bold">Template Format</h6>
            <p class="mb-3">
              <code>(lexical lexical)@{features}</code> or <code>(lexical)@$groupId</code>
            </p>

            <h6 class="fw-bold">Lexical Types</h6>
            <ul class="mb-3">
              <li><code>noun</code> - Nouns (requires: case, gender, number)</li>
              <li><code>verb</code> - Verbs (requires: tense, voice, person, number)</li>
              <li><code>adjective</code> - Adjectives (requires: case, gender, number)</li>
              <li><code>article</code> - Articles (requires: case, gender, number)</li>
              <li><code>pronoun</code> - Pronouns (requires: type; optional: case, person, number, gender)</li>
              <li><code>adverb</code> - Adverbs (no features required)</li>
              <li><code>preposition</code> - Prepositions (no features required)</li>
              <li><code>conjunction</code> - Conjunctions (no features required)</li>
            </ul>

            <h6 class="fw-bold">Feature Values</h6>
            <div class="row mb-3">
              <div class="col-md-6">
                <strong>Case:</strong> nominative, genitive, accusative, vocative<br>
                <strong>Gender:</strong> masculine, feminine, neuter, <span class="badge bg-warning text-dark">⚡ wildcard</span><br>
                <strong>Number:</strong> singular, plural, <span class="badge bg-warning text-dark">⚡ wildcard</span>
              </div>
              <div class="col-md-6">
                <strong>Tense:</strong> present, past, future<br>
                <strong>Voice:</strong> active, passive<br>
                <strong>Person:</strong> first, second, third
              </div>
            </div>

            <div class="alert alert-info mb-3">
              <strong>⚡ Wildcards:</strong> Select "Wildcard (Random)" for gender or number to generate varied sentences.
              Each generation will randomly choose a different value (e.g., masculine, feminine, or neuter for gender).
            </div>

            <h6 class="fw-bold">Examples</h6>
            <div class="mb-2">
              <strong>Simple noun phrase:</strong><br>
              <code>(article noun)@{nominative:masculine:singular}</code>
            </div>
            <div class="mb-2">
              <strong>With adjective:</strong><br>
              <code>(article adjective noun)@{nominative:feminine:singular}</code>
            </div>
            <div class="mb-2">
              <strong>Complete sentence:</strong><br>
              <code>(article noun)@{nominative:masculine:singular} (verb)@{present:active:third:singular}</code>
            </div>
            <div class="mb-2">
              <strong>With agreement (reference):</strong><br>
              <code>(article noun)@{nominative:masculine:singular} (adjective)@$1</code><br>
              <small class="text-muted">The adjective inherits features from group 1</small>
            </div>
            <div class="mb-2">
              <strong>Override individual features:</strong><br>
              <code>(article noun adjective{feminine})@{nominative:masculine:singular}</code><br>
              <small class="text-muted">Adjective overrides gender to feminine</small>
            </div>
            <div class="mb-2">
              <strong>⚡ With wildcards:</strong><br>
              <code>(article noun)@{nom:*gender*:sg}</code><br>
              <small class="text-muted">Generates different genders each time - great for practice!</small>
            </div>

            <h6 class="fw-bold mt-3">Tips</h6>
            <ul class="mb-0">
              <li>Use the UI above to build templates visually</li>
              <li>Features must match the order shown for each lexical type</li>
              <li>References ($1, $2, etc.) must point to earlier groups</li>
              <li>Overrides let you specify different features for individual lexicals within a group</li>
              <li><strong>⚡ Use wildcards</strong> for gender or number to practice with varied sentence structures</li>
            </ul>
          </div>
          <div class="modal-footer">
            <button type="button" class="btn btn-primary" @click="showHelp = false">
              Close
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useTemplateBuilderStore } from '../stores/templateBuilder'
import api from '../services/api'

const router = useRouter()
const store = useTemplateBuilderStore()
const loading = ref(true)
const selectedLexicals = ref({})
const generatedResult = ref(null)
const saveSuccess = ref(null)
const showHelp = ref(false)

onMounted(async () => {
  try {
    await store.fetchMetadata()

    // Check if we have a template to load from query params
    const templateFromQuery = router.currentRoute.value.query.template
    if (templateFromQuery) {
      store.loadTemplate(templateFromQuery)
    }
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
  if (!lexicalSchema) return []

  // For pronouns, include both required and optional features
  const allFeatures = [...lexicalSchema.required]
  if (lexicalSchema.optional) {
    allFeatures.push(...lexicalSchema.optional)
  }
  return allFeatures
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

function formatFeatureValue(value, category) {
  // Check if this is a wildcard for gender, number, or person
  if (category === 'gender' && value === '*gender*') {
    return '⚡ Wildcard (Random)'
  }
  if (category === 'number' && value === '*number*') {
    return '⚡ Wildcard (Random)'
  }
  if (category === 'person' && value === '*person*') {
    return '⚡ Wildcard (Random)'
  }
  // Return the value as-is for non-wildcards
  return value
}

async function handleGenerate() {
  try {
    generatedResult.value = await store.generateSentence()
  } catch (err) {
    console.error('Generation failed:', err)
  }
}

async function handleSave() {
  try {
    const result = await api.saveTemplate(store.generatedTemplate)
    saveSuccess.value = `Template saved with ID ${result.id}`
    setTimeout(() => {
      saveSuccess.value = null
    }, 3000)
  } catch (err) {
    store.error = err.message
    console.error('Failed to save template:', err)
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
