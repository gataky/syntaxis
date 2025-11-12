<template>
  <div class="translation-exercise container mt-4">
    <h1 class="mb-4">Translation Exercise</h1>

    <div class="mb-3">
      <label for="templateInput" class="form-label">Enter Grammar Template:</label>
      <textarea class="form-control" id="templateInput" rows="3" v-model="template"></textarea>
    </div>

    <button class="btn btn-primary" @click="generateExercise">Generate</button>

    <div v-if="error" class="alert alert-danger mt-4" role="alert">
      {{ error }}
    </div>

    <ExerciseDisplay v-if="exerciseData" :template="exerciseData.template" :lexicals="exerciseData.lexicals" />

    <div class="d-flex justify-content-between mt-4">
      <button class="btn btn-secondary" @click="goBack">Back</button>
      <button class="btn btn-info" @click="regenerateExercise">Regenerate</button>
    </div>
  </div>
</template>

<script>
import api from '@/services/api';
import ExerciseDisplay from '@/components/ExerciseDisplay.vue';

export default {
  name: 'TranslationExerciseView',
  components: {
    ExerciseDisplay
  },
  data() {
    return {
      template: '',
      exerciseData: null,
      error: null,
    }
  },
  methods: {
    async generateExercise() {
      this.error = null;
      this.exerciseData = null;
      try {
        this.exerciseData = await api.generateSentence(this.template);
      } catch (error) {
        this.error = error.message;
      }
    },
    goBack() {
      this.$router.push('/');
    },
    regenerateExercise() {
      this.generateExercise();
    }
  }
}
</script>

<style scoped>
/* Add component-specific styles here */
</style>
