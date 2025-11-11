<template>
  <div class="word-display">
    <p class="english-word">{{ englishWord }}</p>
    <button class="btn btn-sm btn-outline-secondary" @click="toggleVisibility">
      {{ isVisible ? greekWord : 'Show Answer' }}
    </button>
  </div>
</template>

<script>
export default {
  name: 'Word',
  props: {
    englishWord: {
      type: String,
      required: true
    },
    greekWord: {
      type: String,
      required: true
    }
  },
  data() {
    return {
      isVisible: false
    }
  },
  methods: {
    toggleVisibility() {
      this.isVisible = !this.isVisible;
    }
  }
}
</script>

<style scoped>
.english-word {
  font-weight: bold;
}
</style>
