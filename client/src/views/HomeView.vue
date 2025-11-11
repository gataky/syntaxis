<template>
  <div class="home container mt-4">
    <h1 class="mb-4">Welcome to the Syntaxis Greek Grammar Practice App!</h1>
    <p class="lead">Choose an exercise to begin:</p>

    <div class="list-group">
      <router-link to="/exercise/translation" class="list-group-item list-group-item-action">
        Translation Exercise
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
