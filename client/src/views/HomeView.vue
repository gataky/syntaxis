<template>
  <div class="home container mt-5">
    <div class="p-5 mb-4 bg-tertiary rounded-3">
      <div class="container-fluid py-5">
        <h1 class="display-5 fw-bold">Welcome to Syntaxis</h1>
        <p class="col-md-8 fs-4">
          Your personal workshop for mastering Ancient Greek syntax. This application is designed to help you practice and improve your understanding of Greek grammar through a series of interactive exercises.
        </p>
      </div>
    </div>

    <h2 class="mb-4">Available Exercises</h2>
    <div class="list-group">
      <router-link to="/exercise/translation" class="list-group-item list-group-item-action">
        <h5 class="mb-1">Translation Exercise</h5>
        <p class="mb-1">Translate sentences from Greek to English and vice versa to test your comprehension.</p>
      </router-link>
    </div>
  </div>
</template>

<script>
export default {
  name: 'HomeView'
}
</script>

<style scoped>
/* Add component-specific styles here */
</style>
