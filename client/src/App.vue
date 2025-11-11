<template>
  <div id="app" class="container">
    <header class="my-4">
      <nav class="navbar navbar-expand-lg navbar-light bg-light">
        <div class="container-fluid">
          <router-link class="navbar-brand" to="/">Syntaxis Greek Grammar</router-link>
          <div class="collapse navbar-collapse">
            <ul class="navbar-nav me-auto mb-2 mb-lg-0">
              <li class="nav-item">
                <router-link class="nav-link" to="/">Home</router-link>
              </li>
              <li class="nav-item">
                <router-link class="nav-link" to="/exercise/translation">Translation Exercise</router-link>
              </li>
            </ul>
          </div>
        </div>
      </nav>
    </header>
    <main>
      <router-view />
    </main>
  </div>
</template>

<script setup>
// No script setup needed for now, as we are just setting up the layout
</script>

<style scoped>
/* Add component-specific styles here */
</style>
