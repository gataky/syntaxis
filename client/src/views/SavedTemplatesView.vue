<template>
  <div class="container mt-4">
    <h1 class="mb-4">Saved Templates</h1>

    <!-- Loading State -->
    <div v-if="loading" class="alert alert-info">
      Loading templates...
    </div>

    <!-- Error Display -->
    <div v-if="error" class="alert alert-danger alert-dismissible fade show" role="alert">
      <strong>Error:</strong> {{ error }}
      <button type="button" class="btn-close" @click="error = null"></button>
    </div>

    <!-- Empty State -->
    <div v-if="!loading && templates.length === 0" class="alert alert-secondary">
      No saved templates yet. Go to the Template Builder to create and save templates.
    </div>

    <!-- Templates Table -->
    <div v-if="!loading && templates.length > 0" class="card">
      <div class="card-body">
        <table class="table table-hover">
          <thead>
            <tr>
              <th>Template</th>
              <th>Created</th>
              <th style="width: 200px;">Actions</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="template in templates" :key="template.id">
              <td>
                <code>{{ template.template }}</code>
              </td>
              <td>
                <small class="text-muted">{{ formatDate(template.created_at) }}</small>
              </td>
              <td>
                <button
                  type="button"
                  class="btn btn-sm btn-success me-2"
                  @click="loadToExercise(template)"
                  title="Load in Translation Exercise"
                >
                  Load
                </button>
                <button
                  type="button"
                  class="btn btn-sm btn-danger"
                  @click="confirmDelete(template)"
                >
                  Delete
                </button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- Delete Confirmation Modal -->
    <div
      v-if="templateToDelete"
      class="modal fade show d-block"
      tabindex="-1"
      style="background-color: rgba(0, 0, 0, 0.5);"
    >
      <div class="modal-dialog">
        <div class="modal-content">
          <div class="modal-header">
            <h5 class="modal-title">Confirm Delete</h5>
            <button type="button" class="btn-close" @click="templateToDelete = null"></button>
          </div>
          <div class="modal-body">
            <p>Are you sure you want to delete this template?</p>
            <code>{{ templateToDelete.template }}</code>
          </div>
          <div class="modal-footer">
            <button type="button" class="btn btn-secondary" @click="templateToDelete = null">
              Cancel
            </button>
            <button type="button" class="btn btn-danger" @click="handleDelete">
              Delete
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
import api from '../services/api'

const router = useRouter()
const templates = ref([])
const loading = ref(true)
const error = ref(null)
const templateToDelete = ref(null)

onMounted(async () => {
  await loadTemplates()
})

async function loadTemplates() {
  try {
    loading.value = true
    error.value = null
    templates.value = await api.listTemplates()
  } catch (err) {
    error.value = err.message
    console.error('Failed to load templates:', err)
  } finally {
    loading.value = false
  }
}

function formatDate(dateString) {
  const date = new Date(dateString)
  return date.toLocaleString()
}

function loadToBuilder(template) {
  // Navigate to builder with template string as query param
  router.push({
    name: 'builder',
    query: { template: template.template }
  })
}

function loadToExercise(template) {
  // Navigate to exercise with template string as query param
  router.push({
    name: 'translation',
    query: { template: template.template }
  })
}

function confirmDelete(template) {
  templateToDelete.value = template
}

async function handleDelete() {
  if (!templateToDelete.value) return

  try {
    await api.deleteTemplate(templateToDelete.value.id)
    templateToDelete.value = null
    // Reload templates
    await loadTemplates()
  } catch (err) {
    error.value = err.message
    console.error('Failed to delete template:', err)
    templateToDelete.value = null
  }
}
</script>

<style scoped>
.card {
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}

.table {
  margin-bottom: 0;
}

code {
  font-size: 0.9rem;
  color: #d63384;
  background-color: #f8f9fa;
  padding: 0.2rem 0.4rem;
  border-radius: 0.25rem;
}
</style>
