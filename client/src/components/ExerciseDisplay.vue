<template>
  <div class="exercise-display mt-4">
    <div class="card">
      <div class="card-header">
        Template: <code>{{ template }}</code>
      </div>
      <div class="card-body">
        <div class="row text-center mb-3">
          <div v-for="(lexical, index) in lexicals" :key="index" class="col">
            <strong>{{ lexical.features.lexical }}</strong>
          </div>
        </div>
        <div class="row text-center mb-3">
          <div v-for="(lexical, index) in lexicals" :key="index" class="col">
            <!-- Placeholder for Word component -->
            <p>{{ lexical.translations[0] }}</p>
            <p class="text-muted">({{ lexical.word[0] }})</p>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'ExerciseDisplay',
  props: {
    template: {
      type: String,
      required: true
    },
    lexicals: {
      type: Array,
      required: true
    }
  }
}
</script>

<style scoped>
/* Add component-specific styles here */
</style>
