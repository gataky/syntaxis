<template>
  <div class="translation-exercise container mt-4">
    <h1 class="mb-4">Translation Exercise</h1>

    <!-- Template Display -->
    <div v-if="template" class="card mb-4">
      <div class="card-header">Grammar Template</div>
      <div class="card-body">
        <pre><code>{{ template }}</code></pre>
        <div class="d-flex justify-content-end">
          <button class="btn btn-sm btn-outline-secondary me-2" @click="goBack">
            Back to Home
          </button>
          <button class="btn btn-sm btn-primary" @click="regenerateExercise">
            Regenerate
          </button>
        </div>
      </div>
    </div>

    <!-- Template Input -->
    <div v-if="!template" class="mb-3">
      <label for="templateInput" class="form-label">Enter Grammar Template:</label>
      <textarea
        class="form-control"
        id="templateInput"
        rows="3"
        v-model="inputTemplate"
        @keyup.enter="generateExercise"
      ></textarea>
      <div class="d-flex justify-content-end mt-2">
        <button class="btn btn-primary" @click="generateExercise">Generate</button>
      </div>
    </div>

    <!-- Error Display -->
    <div v-if="error" class="alert alert-danger mt-4" role="alert">
      {{ error }}
    </div>

    <!-- Exercise -->
    <ExerciseDisplay
      v-if="exerciseData"
      :template="exerciseData.template"
      :lexicals="exerciseData.lexicals"
    />
  </div>
</template>

<script>
import api from '@/services/api'
import ExerciseDisplay from '@/components/ExerciseDisplay.vue'

export default {
  name: 'TranslationExerciseView',
  components: {
    ExerciseDisplay,
  },
  data() {
    return {
      inputTemplate: '',
      template: null,
      exerciseData: null,
      error: null,
    }
  },
  mounted() {
    // Check if template was passed via query params
    const templateFromQuery = this.$route.query.template
    if (templateFromQuery) {
      this.template = templateFromQuery
      // Auto-generate on load
      this.fetchExercise()
    }
  },
  methods: {
    async fetchExercise() {
      this.error = null
      this.exerciseData = null
      try {
        this.exerciseData = await api.generateSentence(this.template)
      } catch (error) {
        this.error = error.message
      }
    },
    generateExercise() {
      if (this.inputTemplate) {
        // Navigate to the same route but with the template as a query param
        this.$router.push({
          query: { template: this.inputTemplate },
        })
      }
    },
    goBack() {
      this.$router.push('/')
    },
    regenerateExercise() {
      this.fetchExercise()
    },
  },
  watch: {
    '$route.query.template'(newTemplate) {
      this.template = newTemplate
      if (newTemplate) {
        this.fetchExercise()
      } else {
        this.exerciseData = null
        this.inputTemplate = ''
      }
    },
  },
}
</script>

<style scoped>
pre {
  background-color: var(--bs-dark);
  color: var(--bs-light);
  padding: 1rem;
  border-radius: 0.25rem;
}

.card {
  border-color: var(--bs-border-color);
}

.card-header {
  background-color: var(--bs-tertiary-bg);
}
</style>
