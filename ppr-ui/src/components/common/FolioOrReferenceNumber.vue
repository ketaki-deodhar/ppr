<template>
  <div>
    <h2 :data-test-id="`${sectionId}-title`">
      {{ `${sectionNumber ? sectionNumber + '.' : ''} ${folioOrRefConfig.title}`}}
    </h2>
    <p class="mt-2" :data-test-id="`${sectionId}-description`">
      {{ folioOrRefConfig.description }}
    </p>

    <v-form ref="folioOrRefForm" v-model="isFormValid" :data-test-id="`${sectionId}-form`">
      <v-card
        flat
        rounded
        class="mt-6 pt-10 px-7 pb-5"
        :class="{ 'border-error-left': setShowErrors }"
        :data-test-id="`${sectionId}-card`"
      >
        <FormField
          :sectionId="sectionId"
          :initialValue="initialValue"
          :inputTitle="folioOrRefConfig.inputTitle"
          :inputLabel="folioOrRefConfig.inputLabel"
          :inputColWidth="hasWiderInput ? 10 : undefined"
          :labelColWidth="hasWiderInput ? 2 : undefined"
          :rules="maxLength(30)"
          :showErrors="setShowErrors"
          @updateValue="$emit('setStoreProperty', $event)"
        />
      </v-card>
    </v-form>
  </div>
</template>

<script lang="ts">
import { defineComponent, toRefs, ref, computed, reactive, watch } from 'vue-demi'
import { useInputRules } from '@/composables'
import { FormField } from '@/components/common'
import { folioOrRefConfig } from '@/resources/attnRefConfigs'

export default defineComponent({
  name: 'FolioOrReferenceNumber',
  components: { FormField },
  emits: ['isFolioOrRefNumValid', 'setStoreProperty'],
  props: {
    initialValue: {
      type: String,
      default: ''
    },
    hasWiderInput: {
      type: Boolean,
      default: false
    },
    sectionId: {
      type: String,
      required: true
    },
    sectionNumber: {
      type: Number,
      required: false
    },
    validate: {
      type: Boolean,
      default: false
    }
  },
  setup (props, { emit }) {
    const { maxLength } = useInputRules()

    const folioOrRefForm = ref(null)

    const localState = reactive({
      isFormValid: false,
      setShowErrors: computed((): boolean => props.validate && !localState.isFormValid)
    })

    watch(() => localState.isFormValid, (val: boolean) => {
      emit('isFolioOrRefNumValid', val)
    })

    watch(() => props.validate, (validate: boolean) => {
      validate && folioOrRefForm.value?.validate()
    })

    return {
      folioOrRefConfig,
      folioOrRefForm,
      maxLength,
      ...toRefs(localState)
    }
  }
})
</script>

<style lang="scss" scoped>
@import '@/assets/styles/theme.scss';
</style>
