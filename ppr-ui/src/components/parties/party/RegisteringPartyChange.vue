<template>
  <v-row no-gutters id="reg-party-change">
      <v-col v-if="!openChangeScreen">
        <registering-party
          @changeRegisteringParty="changeRegisteringParty"
        />
      </v-col>
      <v-col class="mt-2 mb-8" v-else>
        <v-card flat class="add-party-container" :class="{ 'border-error-left': showErrorBar }">
          <div class="px-6 pt-8">
            <h3 v-if="!isSbc" class="pb-2">Change Registering Party</h3>
            <span class="body-text">
            {{ !isSbc ? 'Change' : 'Include' }} the Registering Party
            by entering the registering party code
            or their name (business or person), or if the Registering Party you
            want to include is new (i.e., they do not have a registering party
            code) you can add their information manually.
            </span>
          </div>
          <party-search
            :isAutoCompleteDisabled="addEditInProgress"
            :isRegisteringParty="true"
            @showSecuredPartyAdd="initAdd"
            @hideSearch="resetData"
          />
          <div v-if="showAddRegisteringParty">
            <edit-party :isRegisteringParty="true" @resetEvent="resetData" />
          </div>
          <div v-if="!showAddRegisteringParty" class="px-5 pt-0 pb-8" style="height:80px">
            <v-btn
              v-if="!isSbc"
              id="cancel-btn-chg-reg-party"
              large
              outlined
              color="primary"
              class="float-right"
              @click="resetData"
            >
              Cancel
            </v-btn>
          </div>
        </v-card>
      </v-col>
    </v-row>
</template>

<script lang="ts">
import {
  defineComponent,
  reactive,
  toRefs,
  onMounted,
  watch,
  computed
} from 'vue-demi'
import { useStore } from '@/store/store'
import { EditParty, PartySearch, RegisteringParty } from '@/components/parties/party'
import { PartyIF } from '@/interfaces'
import { storeToRefs } from 'pinia' // eslint-disable-line no-unused-vars

export default defineComponent({
  components: {
    PartySearch,
    EditParty,
    RegisteringParty
  },
  props: {
    isSummary: {
      type: Boolean,
      default: false
    },
    setShowErrorBar: {
      type: Boolean,
      default: false
    }
  },
  setup (props, context) {
    const { getAddSecuredPartiesAndDebtors, isRoleStaffSbc } = storeToRefs(useStore())
    const localState = reactive({
      openChangeScreen: false,
      isSbc: isRoleStaffSbc.value,
      showAddRegisteringParty: false,
      addEditInProgress: false,
      registeringParty: computed((): PartyIF => {
        return getAddSecuredPartiesAndDebtors.value.registeringParty
      }),
      summaryView: computed((): boolean => {
        return props.isSummary
      }),
      showErrorBar: computed((): boolean => {
        return props.setShowErrorBar
      })
    })

    onMounted(() => {
      if ((isRoleStaffSbc.value) && ((!localState.registeringParty) || (!localState.registeringParty?.action))) {
        localState.openChangeScreen = true
        context.emit('registeringPartyOpen', true)
      }
    })

    const changeRegisteringParty = () => {
      localState.openChangeScreen = true
      context.emit('registeringPartyOpen', true)
    }

    const initAdd = () => {
      localState.addEditInProgress = true
      localState.showAddRegisteringParty = true
      context.emit('registeringPartyOpen', true)
    }

    const resetData = () => {
      localState.addEditInProgress = false
      localState.showAddRegisteringParty = false
      localState.openChangeScreen = isRoleStaffSbc.value && ((!localState.registeringParty) ||
        (!localState.registeringParty.action))
      context.emit('registeringPartyOpen', false)
    }

    watch(() => localState.registeringParty, (rp) => {
      if (!rp && localState.isSbc) {
        localState.openChangeScreen = true
      }
    })

    return {
      changeRegisteringParty,
      initAdd,
      resetData,
      ...toRefs(localState)
    }
  }
})
</script>

<style lang="scss" scoped>
@import '@/assets/styles/theme.scss';
  .body-text {
    color: $gray7;
  }
</style>
