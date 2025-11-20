<template>
  <div class="exercise-display mt-4">
    <div class="card mb-4">
      <div class="card-header">
        Template: <code>{{ template }}</code>
      </div>
    </div>

    <div class="d-flex flex-wrap gap-3 justify-content-center">
      <div
        v-for="(lexical, index) in lexicals"
        :key="index"
        class="word-card card text-center"
      >
        <div class="card-body">
          <!-- Feature at top (number: sg/pl) -->
          <div class="feature-badge mb-3">
            <span class="badge bg-secondary">{{ lexical.features.number || 'N/A' }}</span>
          </div>

          <!-- English translation(s) -->
          <div class="translation mb-3">
            <div v-for="(trans, tIndex) in lexical.translations" :key="tIndex" class="translation-word">
              {{ trans }}
            </div>
          </div>

          <!-- Greek word (hidden/blurred, click to reveal) -->
          <div class="greek-word">
            <div
              v-if="!revealed[index]"
              class="greek-hidden"
              @click="revealWord(index)"
            >
              <span class="blurred">{{ lexical.word[0] }}</span>
              <div class="click-hint">Click to reveal</div>
            </div>
            <div v-else class="greek-revealed">
              {{ lexical.word[0] }}
            </div>
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
  },
  data() {
    return {
      revealed: {}
    }
  },
  methods: {
    revealWord(index) {
      this.revealed[index] = true
      // Force reactivity update
      this.revealed = { ...this.revealed }
    }
  },
  watch: {
    lexicals() {
      // Reset revealed state when lexicals change (new exercise)
      this.revealed = {}
    }
  }
}
</script>

<style scoped>
.word-card {
  width: 200px;
  min-height: 250px;
  border-color: var(--bs-border-color);
  background-color: var(--bs-tertiary-bg);
  transition: transform 0.2s, box-shadow 0.2s;
}

.word-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.25);
}

.feature-badge {
  font-size: 1rem;
  font-weight: bold;
}

.translation {
  font-size: 1.1rem;
  font-weight: 500;
  color: var(--bs-body-color);
}

.translation-word {
  margin: 0.25rem 0;
}

.greek-word {
  margin-top: 1rem;
  padding-top: 1rem;
  border-top: 2px solid var(--bs-border-color);
}

.greek-hidden {
  cursor: pointer;
  user-select: none;
}

.greek-hidden:hover {
  opacity: 0.8;
}

.blurred {
  filter: blur(8px);
  font-size: 1.2rem;
  font-weight: bold;
  color: var(--bs-gray-500);
}

.click-hint {
  font-size: 0.75rem;
  color: var(--bs-gray-400);
  margin-top: 0.5rem;
}

.greek-revealed {
  font-size: 1.3rem;
  font-weight: bold;
  color: var(--bs-primary);
  animation: fadeIn 0.3s ease-in;
}

@keyframes fadeIn {
  from {
    opacity: 0;
    transform: scale(0.95);
  }
  to {
    opacity: 1;
    transform: scale(1);
  }
}

.gap-3 {
  gap: 1rem;
}
</style>
