<template>
  <v-container v-if="dataLoaded" class="view-container pa-0" fluid>
    <v-overlay v-model="submitting">
      <v-progress-circular color="primary" size="50" indeterminate />
    </v-overlay>

    <div class="view-container px-15 py-0">
      <div class="container pa-0 pt-4">
        <v-row no-gutters>
          <v-col cols="9">
            <v-row no-gutters id="registration-header" class="pt-3 pb-3 soft-corners-top">
              <v-col cols="auto">
                <h1>{{ `Manufactured Home Registration${isDraft ? ' - Draft' : ''}` }}</h1>
              </v-col>
            </v-row>
            <Stepper
              class="mt-4"
              :stepConfig="getMhrSteps"
              :showStepErrors="isValidatingApp && !isValidMhrRegistration"
            />
           <!-- Component Steps -->
            <component
              v-for="step in getMhrSteps"
              v-show="isRouteName(step.to)"
              :is="step.component"
              :key="step.step"
            />
          </v-col>
          <v-col class="pl-6 pt-5" cols="3">
            <aside>
              <affix relative-element-selector=".col-9" :offset="{ top: 90, bottom: -100 }">
                <sticky-container
                  :setRightOffset="true"
                  :setShowFeeSummary="true"
                  :setFeeType="feeType"
                  :setRegistrationLength="registrationLength"
                  :setRegistrationType="registrationTypeUI"
                />
              </affix>
            </aside>
          </v-col>
        </v-row>
      </div>
    </div>
    <v-row no-gutters class="mt-20">
      <v-col cols="12">
        <ButtonFooter
          isMhr
          :navConfig="getFooterButtonConfig"
          :currentStepName="$route.name"
          :forceSave="saveDraftExit"
          @error="emitError($event)"
          @submit="submit()"
          @cancelProceed="resetAllValidations()"
        />
      </v-col>
    </v-row>
  </v-container>
</template>

<script lang="ts">
import { computed, defineComponent, nextTick, onMounted, reactive, toRefs } from 'vue-demi'
import { useStore } from '@/store/store'
import { storeToRefs } from 'pinia'
import { RegistrationFlowType, UIRegistrationTypes } from '@/enums'
import { getFeatureFlag, getMhrDraft, submitMhrRegistration } from '@/utils'
import { ButtonFooter, Stepper, StickyContainer } from '@/components/common'
import { useAuth, useHomeOwners, useMhrValidations, useNavigation, useNewMhrRegistration } from '@/composables'
import { FeeSummaryTypes } from '@/composables/fees/enums'
/* eslint-disable no-unused-vars */
import { ErrorIF, MhrRegistrationIF, RegTableNewItemI, StepIF } from '@/interfaces'
import { RegistrationLengthI } from '@/composables/fees/interfaces'
/* eslint-enable no-unused-vars */

export default defineComponent({
  name: 'MhrRegistration',
  components: {
    ButtonFooter,
    Stepper,
    StickyContainer
  },
  props: {
    appReady: {
      type: Boolean,
      default: false
    },
    isJestRunning: {
      type: Boolean,
      default: false
    },
    saveDraftExit: {
      type: Boolean,
      default: false
    }
  },
  setup (props, context) {
    const { isRouteName, goToDash } = useNavigation()
    const { isAuthenticated } = useAuth()
    const {
      // Actions
      setUnsavedChanges,
      setRegTableNewItem,
      setMhrTransferType
    } = useStore()
    const {
      // Getters
      getMhrSteps,
      getFooterButtonConfig,
      getMhrDraftNumber,
      getRegistrationType,
      getRegistrationFlowType,
      getMhrRegistrationValidationModel
    } = storeToRefs(useStore())

    const {
      MhrCompVal,
      MhrSectVal,
      setValidation,
      getValidation,
      resetAllValidations,
      scrollToInvalidReviewConfirm
    } = useMhrValidations(toRefs(getMhrRegistrationValidationModel.value))

    const {
      initDraftMhr,
      buildApiData,
      parseStaffPayment
    } = useNewMhrRegistration()

    const {
      setShowGroups
    } = useHomeOwners()

    const localState = reactive({
      dataLoaded: false,
      submitting: false,
      feeType: FeeSummaryTypes.NEW_MHR,
      registrationLength: computed((): RegistrationLengthI => {
        return { lifeInfinite: true, lifeYears: 0 }
      }),
      registrationTypeUI: computed((): UIRegistrationTypes => {
        return getRegistrationType.value?.registrationTypeUI || ('' as UIRegistrationTypes)
      }),
      isDraft: computed((): boolean => {
        return getMhrDraftNumber.value
      }),
      isValidatingApp: computed((): boolean => {
        return getValidation(MhrSectVal.REVIEW_CONFIRM_VALID, MhrCompVal.VALIDATE_APP)
      }),
      isValidMhrRegistration: computed((): boolean => {
        return getMhrSteps.value.every((step: StepIF) => step.valid)
      })
    })

    const emitError = (error: ErrorIF): void => {
      context.emit('error', error)
    }

    onMounted(async (): Promise<void> => {
      // do not proceed if app is not ready
      // redirect if not authenticated (safety check - should never happen) or if app is not open to user (ff)
      if (!props.appReady || !isAuthenticated.value ||
        (!props.isJestRunning && !getFeatureFlag('mhr-registration-enabled'))) {
        goToDash()
        return
      }
      // redirect if store doesn't contain all needed data (happens on page reload, etc.)
      if (!getRegistrationType.value || getRegistrationFlowType.value !== RegistrationFlowType.NEW) {
        goToDash()
        return
      }

      // Reset validations
      setMhrTransferType(null)
      resetAllValidations()

      // page is ready to view
      if (getMhrDraftNumber.value) {
        const { registration } = await getMhrDraft(getMhrDraftNumber.value)
        await initDraftMhr(registration as unknown as MhrRegistrationIF)
      }

      context.emit('emitHaveData', true)
      localState.dataLoaded = true
    })

    const submit = async () => {
      // Prompt App Validations
      await setValidation(MhrSectVal.REVIEW_CONFIRM_VALID, MhrCompVal.VALIDATE_APP, true)
      await nextTick()

      if (localState.isValidMhrRegistration) {
        // Submit Filing
        localState.submitting = true
        const data = buildApiData()

        // In cases where hasNoCertification is selected:
        // Need to clear hasNoCertification for submission and replace it with an empty csa number
        // This is to meet the API Schema requirements.
        // This does not apply to drafts as we want to maintain that property for resuming drafts
        if (data?.description?.hasNoCertification) {
          delete data.description.hasNoCertification
          data.description.csaNumber = ''
        }

        // Property is maintained for resuming draft but removed for submission
        if (data.submittingParty.hasUsedPartyLookup) {
          delete data.submittingParty.hasUsedPartyLookup
        }

        const mhrSubmission = await submitMhrRegistration(data, parseStaffPayment())
        localState.submitting = false
        if (!mhrSubmission.error && mhrSubmission?.mhrNumber) {
          resetAllValidations()
          setShowGroups(false)
          const newRegItem: RegTableNewItemI = {
            addedReg: mhrSubmission.mhrNumber,
            addedRegParent: '',
            addedRegSummary: mhrSubmission,
            prevDraft: mhrSubmission.documentId
          }
          setRegTableNewItem(newRegItem)
          setUnsavedChanges(false)
          goToDash()
        } else {
          emitError(mhrSubmission?.error)
        }
      } else {
        let stepsValidation = getMhrSteps.value.map((step : StepIF) => step.valid)
        stepsValidation.pop() // Removes review confirm step from stepsValidation
        scrollToInvalidReviewConfirm(stepsValidation)
      }
    }

    return {
      getMhrSteps,
      emitError,
      isRouteName,
      submit,
      resetAllValidations,
      getFooterButtonConfig,
      ...toRefs(localState)
    }
  }
})
</script>

<style lang="scss" module>
@import '@/assets/styles/theme.scss';
.step-container {
  margin-top: 1rem;
  padding: 1.25rem;
}
.meta-container {
  display: flex;
  flex-flow: column nowrap;
  position: relative;
  > label:first-child {
    font-weight: 700;
  }
}
@media (min-width: 768px) {
  .meta-container {
    flex-flow: row nowrap;
    > label:first-child {
      flex: 0 0 auto;
      padding-right: 2rem;
      width: 12rem;
    }
  }
}
.reg-default-btn {
  background-color: $gray3 !important;
}
.reg-default-btn::before {
  background-color: transparent !important;
}
</style>
