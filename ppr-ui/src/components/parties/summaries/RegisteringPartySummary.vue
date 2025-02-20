<template>
  <v-container class="pa-0 party-summary flat">
    <base-party-summary
      :setHeaders="registeringPartyHeaders"
      :setItems="registeringParty"
      :setOptions="registeringPartyOptions"
      @triggerNoDataAction="goToParties()"
    />
  </v-container>
</template>

<script lang="ts">
import {
  defineComponent,
  reactive,
  computed,
  onMounted,
  toRefs
} from 'vue-demi'
import { useStore } from '@/store/store'
import { useRouter } from 'vue2-helpers/vue-router'
import { BasePartySummary } from '@/components/parties/summaries'
import { AddPartiesIF, PartyIF, PartySummaryOptionsI } from '@/interfaces' // eslint-disable-line no-unused-vars
import { registeringTableHeaders } from '@/resources'
import { RegistrationFlowType } from '@/enums'
import { useRegisteringParty } from '@/composables/useRegisteringParty'
import { storeToRefs } from 'pinia'

export default defineComponent({
  name: 'RegisteringPartySummary',
  components: {
    BasePartySummary
  },
  props: {
    setEnableNoDataAction: {
      default: false
    },
    setHeader: {
      default: ''
    }
  },
  setup (props) {
    const router = useRouter()
    const { setAddSecuredPartiesAndDebtors } = useStore()
    const {
      // Getters
      getAddSecuredPartiesAndDebtors,
      getOriginalAddSecuredPartiesAndDebtors,
      getRegistrationFlowType
    } = storeToRefs(useStore())
    const { getRegisteringParty } = useRegisteringParty()
    const parties: AddPartiesIF = getAddSecuredPartiesAndDebtors.value

    const localState = reactive({
      registeringParty: computed((): Array<PartyIF> => {
        let regParty: PartyIF = parties?.registeringParty
        if (getRegistrationFlowType.value !== RegistrationFlowType.NEW) {
          regParty = getOriginalAddSecuredPartiesAndDebtors.value?.registeringParty
        } else {
          regParty = getAddSecuredPartiesAndDebtors.value?.registeringParty
        }
        if (regParty !== null) {
          return [regParty]
        }
        return []
      }),
      registeringPartyHeaders: computed(function () {
        return [...registeringTableHeaders]
      }),
      registeringPartyOptions: {
        header: props.setHeader,
        iconColor: 'darkBlue',
        iconImage: 'mdi-account',
        isDebtorSummary: false,
        enableNoDataAction: props.setEnableNoDataAction,
        isRegisteringParty: true
      } as PartySummaryOptionsI
    })

    onMounted(async () => {
      const regParty = parties?.registeringParty
      if (regParty === null) {
        try {
          await getRegisteringParty()
        } catch (e) {
          console.error('RegisteringParty.vue onMounted error: ' + ((e as Error).message))
        }
      }
    })

    const goToParties = (): void => {
      parties.showInvalid = true
      setAddSecuredPartiesAndDebtors(parties)
      router.push({ path: '/new-registration/add-securedparties-debtors' })
    }

    return {
      goToParties,
      ...toRefs(localState)
    }
  }
})
</script>

<style lang="scss" module>
@import '@/assets/styles/theme.scss';
</style>
