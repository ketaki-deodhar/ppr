<template>
  <v-container class="header-container view-container px-15 py-0" fluid style="background-color: white;">
    <div class="container pa-0" style="padding: 29px 0 !important;">
      <tombstone-discharge
        v-if="displayDischarge || displayRenewal || displayAmendment || displayMhrInformation"
        :isMhrInformation="displayMhrInformation"
      />
      <tombstone-default v-else />
    </div>
  </v-container>
</template>
<script lang="ts">
// external
import { computed, defineComponent, reactive, toRefs } from 'vue-demi'
import { useRoute } from 'vue2-helpers/vue-router'
// local
import { TombstoneDefault, TombstoneDischarge } from '@/components/tombstone'

export default defineComponent({
  name: 'Tombstone',
  components: {
    TombstoneDefault,
    TombstoneDischarge
  },
  setup () {
    const route = useRoute()
    const localState = reactive({
      currentPath: computed((): string => {
        return route.path
      }),
      displayDischarge: computed((): boolean => {
        return localState.currentPath.includes('discharge')
      }),
      displayRenewal: computed((): boolean => {
        return localState.currentPath.includes('renew')
      }),
      displayAmendment: computed((): boolean => {
        return localState.currentPath.includes('amend')
      }),
      displayMhrInformation: computed((): boolean => {
        return localState.currentPath.includes('mhr-information') || localState.currentPath.includes('exemption')
      })
    })

    return {
      ...toRefs(localState)
    }
  }
})
</script>

<style lang="scss" scoped>
@import '@/assets/styles/theme.scss';
@media print {
  .px-15 {
    padding-left: 10px !important;
    padding-right: 10px !important;
  }
}
</style>
