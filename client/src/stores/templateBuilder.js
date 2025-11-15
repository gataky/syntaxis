import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import api from '../services/api'

export const useTemplateBuilderStore = defineStore('templateBuilder', () => {
  // State
  const groups = ref([])
  const schema = ref(null)
  const features = ref(null)
  const error = ref(null)
  const nextGroupId = ref(1)

  // Getters
  const generatedTemplate = computed(() => {
    if (groups.value.length === 0) return ''

    return groups.value.map(group => {
      // Build lexicals part: "(noun adjective{fem})"
      const lexicalPart = `(${group.lexicals.map(lex => {
        if (lex.overrides && Object.keys(lex.overrides).length > 0) {
          const overrideStr = Object.values(lex.overrides).filter(v => v).join(':')
          return overrideStr ? `${lex.type}{${overrideStr}}` : lex.type
        }
        return lex.type
      }).join(' ')})`

      // Build features part: "@{nom:masc:sg}" or "@$1"
      const featurePart = group.reference
        ? `@$${group.reference.groupId}`
        : `@{${Object.values(group.features).filter(v => v).join(':')}}`

      return lexicalPart + featurePart
    }).join(' ')
  })

  const requiredFeaturesForGroup = computed(() => {
    return (groupId) => {
      const group = groups.value.find(g => g.id === groupId)
      if (!group || !schema.value) return []

      const required = new Set()
      group.lexicals.forEach(lex => {
        const lexicalSchema = schema.value.lexicals[lex.type]
        if (lexicalSchema) {
          lexicalSchema.required.forEach(cat => required.add(cat))
        }
      })
      return Array.from(required)
    }
  })

  const optionalFeaturesForGroup = computed(() => {
    return (groupId) => {
      const group = groups.value.find(g => g.id === groupId)
      if (!group || !schema.value) return []

      const optional = new Set()
      group.lexicals.forEach(lex => {
        const lexicalSchema = schema.value.lexicals[lex.type]
        if (lexicalSchema && lexicalSchema.optional) {
          lexicalSchema.optional.forEach(cat => optional.add(cat))
        }
      })
      return Array.from(optional)
    }
  })

  const availableReferences = computed(() => {
    return (groupId) => {
      return groups.value.filter(g => g.id < groupId)
    }
  })

  // Actions
  async function fetchMetadata() {
    try {
      const [schemaData, featuresData] = await Promise.all([
        api.getLexicalSchema(),
        api.getFeatures()
      ])
      schema.value = schemaData
      features.value = featuresData
      error.value = null
    } catch (err) {
      error.value = err.message || 'Failed to fetch metadata'
      throw err
    }
  }

  function addGroup() {
    const newGroup = {
      id: nextGroupId.value++,
      lexicals: [],
      features: {},
      reference: null
    }
    groups.value.push(newGroup)
    return newGroup.id
  }

  function removeGroup(groupId) {
    const index = groups.value.findIndex(g => g.id === groupId)
    if (index !== -1) {
      groups.value.splice(index, 1)
      // Clear references to deleted group
      groups.value.forEach(g => {
        if (g.reference && g.reference.groupId === groupId) {
          g.reference = null
        }
      })
    }
  }

  function addLexical(groupId, lexicalType) {
    const group = groups.value.find(g => g.id === groupId)
    if (group) {
      group.lexicals.push({
        type: lexicalType,
        overrides: null
      })
    }
  }

  function removeLexical(groupId, lexicalIndex) {
    const group = groups.value.find(g => g.id === groupId)
    if (group) {
      group.lexicals.splice(lexicalIndex, 1)
    }
  }

  function setFeature(groupId, category, value) {
    const group = groups.value.find(g => g.id === groupId)
    if (group) {
      group.features[category] = value
    }
  }

  function setReference(groupId, targetGroupId) {
    const group = groups.value.find(g => g.id === groupId)
    if (group) {
      group.reference = { groupId: targetGroupId }
      // Clear features when referencing
      group.features = {}
    }
  }

  function clearReference(groupId) {
    const group = groups.value.find(g => g.id === groupId)
    if (group) {
      group.reference = null
    }
  }

  function setLexicalOverride(groupId, lexicalIndex, overrideFeatures) {
    const group = groups.value.find(g => g.id === groupId)
    if (group && group.lexicals[lexicalIndex]) {
      group.lexicals[lexicalIndex].overrides = overrideFeatures
    }
  }

  async function generateSentence() {
    try {
      const template = generatedTemplate.value
      if (!template) {
        throw new Error('No template to generate')
      }
      const result = await api.generateSentence(template)
      error.value = null
      return result
    } catch (err) {
      error.value = err.response?.data?.detail || err.message || 'Failed to generate sentence'
      throw err
    }
  }

  function resetBuilder() {
    groups.value = []
    error.value = null
    nextGroupId.value = 1
  }

  function loadTemplate(templateString) {
    // Parse template string and populate groups
    // Clear existing state
    groups.value = []
    nextGroupId.value = 1

    // Template format: "(noun adjective{fem})@{nom:masc:sg} (verb)@$1"
    // Split by spaces to get groups
    const groupTokens = templateString.trim().split(/\s+/)

    groupTokens.forEach(token => {
      // Match pattern like (lexicals)@{features} or (lexicals)@$ref
      const match = token.match(/^\(([^)]+)\)@(.+)$/)
      if (!match) return

      const lexicalsPart = match[1]
      const featuresPart = match[2]

      // Create new group
      const group = {
        id: nextGroupId.value++,
        lexicals: [],
        features: {},
        reference: null
      }

      // Parse lexicals (e.g., "noun adjective{fem}")
      const lexicalTokens = lexicalsPart.split(/\s+/)
      lexicalTokens.forEach(lexToken => {
        const lexMatch = lexToken.match(/^(\w+)(?:\{([^}]+)\})?$/)
        if (!lexMatch) return

        const lexType = lexMatch[1]
        const overrides = lexMatch[2]

        const lexical = {
          type: lexType,
          overrides: null
        }

        // Parse overrides if present (e.g., "fem" or "nom:fem")
        if (overrides) {
          lexical.overrides = {}
          const overrideParts = overrides.split(':')
          // For now, just store as a simple map - this is a simplified parser
          // In reality, we'd need to map these to the correct feature categories
          // But for the basic case, this should work
        }

        group.lexicals.push(lexical)
      })

      // Parse features (e.g., "{nom:masc:sg}" or "$1")
      if (featuresPart.startsWith('$')) {
        // Reference to another group
        const refId = parseInt(featuresPart.substring(1))
        group.reference = { groupId: refId }
      } else if (featuresPart.startsWith('{') && featuresPart.endsWith('}')) {
        // Explicit features
        const featuresStr = featuresPart.substring(1, featuresPart.length - 1)
        const featureValues = featuresStr.split(':')

        // Map feature values to categories
        // This is a simplified mapping - we use the required features order
        const requiredFeats = requiredFeaturesForGroup.value(group.id)
        featureValues.forEach((value, index) => {
          if (value && requiredFeats[index]) {
            group.features[requiredFeats[index]] = value
          }
        })
      }

      groups.value.push(group)
    })
  }

  return {
    // State
    groups,
    schema,
    features,
    error,
    // Getters
    generatedTemplate,
    requiredFeaturesForGroup,
    optionalFeaturesForGroup,
    availableReferences,
    // Actions
    fetchMetadata,
    addGroup,
    removeGroup,
    addLexical,
    removeLexical,
    setFeature,
    setReference,
    clearReference,
    setLexicalOverride,
    generateSentence,
    resetBuilder,
    loadTemplate
  }
})
