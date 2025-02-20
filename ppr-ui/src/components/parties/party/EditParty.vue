<template>
  <div id="edit-party" class="white pa-6" :class="{ 'border-error-left': setShowErrorBar }">
    <secured-party-dialog
      v-if="!isRegisteringParty"
      attach="#app"
      :isDuplicate="foundDuplicate"
      :defaultDialog="toggleDialog"
      :defaultParty="currentSecuredParty"
      :defaultResults="dialogResults"
      :activeIndex="activeIndex"
      @emitResetClose="closeAndReset"
      @emitClose="toggleDialog = false"
    />
    <v-expand-transition>
      <v-row no-gutters>
        <v-col cols="3">
          <label
            class="add-party-header generic-label ml"
            :class="{ 'error-text': invalidSection }"
          > {{ labelText }}
          </label>
        </v-col>
        <v-col cols="9">
          <v-form
            ref="partyForm"
            class="party-form"
            v-on:submit.prevent="addParty"
          >
            <v-row class="pb-6" no-gutters>
              <v-col cols="12">
                <v-radio-group
                  v-model="partyType"
                  class="mt-0"
                  row
                  hide-details="true"
                >
                  <v-radio
                    :class="[
                      'individual-radio',
                      'party-radio-individual',
                    ]"
                    label="Individual Person"
                    :value=SecuredPartyTypes.INDIVIDUAL
                    id="party-individual"
                  >
                  </v-radio>

                  <v-radio
                    :class="['business-radio', 'party-radio-business']"
                    label="Business"
                    :value=SecuredPartyTypes.BUSINESS
                    id="party-business"
                  >
                  </v-radio>
                </v-radio-group>
              </v-col>
            </v-row>
            <v-divider class="pb-4" />
            <v-row v-if="partyType" no-gutters>
              <v-col cols="12">
                <v-row no-gutters class="pb-4">
                  <v-col>
                    <label class="generic-label">
                      {{ isPartyTypeBusiness ? "Business Name" : "Person's Name" }}
                    </label>
                  </v-col>
                </v-row>
                <v-row v-if="isPartyTypeBusiness" no-gutters>
                  <v-col>
                    <v-text-field
                      filled
                      id="txt-name-party"
                      ref="partyNameSearchField"
                      label="Find or enter the Full Legal Name of the Business"
                      v-model="searchValue"
                      :error-messages="
                        errors.businessName.message
                          ? errors.businessName.message
                          : ''
                      "
                      persistent-hint
                      :clearable="showClear"
                      @click:clear="showClear = false"
                      @keyup="validateNameField()"
                    >
                      <template v-slot:append>
                        <v-progress-circular
                          v-if="loadingSearchResults"
                          indeterminate
                          color="primary"
                          class="mx-3"
                          :size="25"
                          :width="3"
                        />
                      </template>
                    </v-text-field>

                    <BusinessSearchAutocomplete
                      :searchValue="autoCompleteSearchValue"
                      :setAutoCompleteIsActive="autoCompleteIsActive"
                      v-click-outside="setCloseAutoComplete"
                      @search-value="setSearchValue"
                      @searching="loadingSearchResults = $event"
                      :showDropdown="$refs.partyNameSearchField && $refs.partyNameSearchField.isFocused"
                      isPPR
                    />
                  </v-col>
                </v-row>
                <v-row v-else no-gutters>
                  <v-col cols="4" class="pr-4">
                    <v-text-field
                      filled
                      label="First Name"
                      id="txt-first-party"
                      v-model="currentSecuredParty.personName.first"
                      @keyup="validateNameField()"
                      persistent-hint
                      :error-messages="
                        errors.first.message ? errors.first.message : ''
                      "
                    />
                  </v-col>
                  <v-col cols="4" class="pr-4">
                    <v-text-field
                      filled
                      label="Middle Name (Optional)"
                      id="txt-middle-party"
                      @keyup="validateNameField()"
                      v-model="currentSecuredParty.personName.middle"
                      persistent-hint
                      :error-messages="
                      errors.middle.message ? errors.middle.message : ''
                      "
                    />
                  </v-col>
                  <v-col cols="4">
                    <v-text-field
                      filled
                      label="Last Name"
                      id="txt-last-party"
                      v-model="currentSecuredParty.personName.last"
                      persistent-hint
                      @keyup="validateNameField()"
                      :error-messages="
                        errors.last.message ? errors.last.message : ''
                      "
                    />
                  </v-col>
                </v-row>
                <v-row no-gutters class="pb-4">
                  <v-col>
                    <label class="generic-label">Email Address</label>
                  </v-col>
                </v-row>
                <v-row no-gutters>
                  <v-col>
                    <v-text-field
                      filled
                      id="txt-email-party"
                      :label="isRegisteringParty ? 'Email Address' : 'Email Address (Optional)'"
                      v-model="currentSecuredParty.emailAddress"
                      :error-messages="
                        errors.emailAddress.message
                          ? errors.emailAddress.message
                          : ''
                      "
                      @blur="onBlur('emailAddress')"
                      persistent-hint
                    />
                  </v-col>
                </v-row>
                <v-row no-gutters class="pb-4">
                  <v-col>
                    <label class="generic-label">Address</label>
                  </v-col>
                </v-row>
                <base-address
                  ref="regMailingAddress"
                  v-model="currentSecuredParty.address"
                  :editing="true"
                  :schema="{ ...addressSchema }"
                  :triggerErrors="showAllAddressErrors"
                  @valid="updateValidity($event)"
                />
              </v-col>
            </v-row>
            <v-row>
              <v-col>
                <div class="form__row form__btns">
                  <v-btn
                    large
                    outlined
                    color="error"
                    v-if="!isRegisteringParty"
                    :disabled="activeIndex === -1"
                    @click="removeSecuredParty(activeIndex)"
                    id="remove-btn-party"
                    class="remove-btn"
                    >
                    <span v-if="isAmendment
                              && activeIndex !== -1
                              && (!currentSecuredParty.action || currentSecuredParty.action !== ActionTypes.ADDED)">
                      Delete
                    </span>
                    <span v-else>Remove</span>
                  </v-btn>

                  <v-btn
                    large
                    id="done-btn-party"
                    class="ml-auto"
                    color="primary"
                    :disabled="!partyType"
                    @click="onSubmitForm()"
                  >
                    Done
                  </v-btn>

                  <v-btn
                    id="cancel-btn-party"
                    large
                    outlined
                    color="primary"
                    @click="resetFormAndData(true)"
                  >
                    Cancel
                  </v-btn>
                </div>
              </v-col>
            </v-row>
          </v-form>
        </v-col>
      </v-row>
    </v-expand-transition>
  </div>
</template>

<script lang="ts">
import {
  defineComponent,
  onMounted,
  reactive,
  toRefs,
  computed,
  watch
} from 'vue-demi'
import { SecuredPartyDialog } from '@/components/dialogs'
import { BusinessSearchAutocomplete } from '@/components/search'
import { BaseAddress } from '@/composables/address'
import { SecuredPartyTypes } from '@/enums'
import { useSecuredParty, useSecuredPartyValidation } from '@/composables/parties'
import { formatAddress } from '@/composables/address/factories'
import { SearchPartyIF } from '@/interfaces' // eslint-disable-line no-unused-vars
import { partyCodeSearch } from '@/utils'
import { useValidation } from '@/utils/validators/use-validation'
import { isEqual } from 'lodash'

export default defineComponent({
  name: 'EditParty',
  components: {
    BaseAddress,
    SecuredPartyDialog,
    BusinessSearchAutocomplete
  },
  props: {
    activeIndex: {
      type: Number,
      default: -1
    },
    invalidSection: {
      type: Boolean,
      default: false
    },
    isRegisteringParty: {
      type: Boolean,
      default: false
    },
    setShowErrorBar: {
      type: Boolean,
      default: false
    },
    isEditMode: {
      type: Boolean,
      default: false
    }
  },
  emits: ['addEditParty', 'resetEvent'],
  setup (props, context) {
    const {
      currentSecuredParty,
      currentIsBusiness,
      partyType,
      getSecuredParty,
      resetFormAndData,
      removeSecuredParty,
      addEditSecuredParty,
      registrationFlowType,
      RegistrationFlowType,
      updateAddress,
      ActionTypes,
      setRegisteringParty,
      addressSchema,
      hasMatchingSecuredParty,
      originalSecuredParty
    } = useSecuredParty(context)

    const {
      errors,
      updateValidity,
      validateSecuredPartyForm,
      validateInput
    } = useSecuredPartyValidation()

    const {
      validateFirstName,
      validateMiddleName,
      validateLastName,
      validateBusinessName
    } = useValidation()

    const localState = reactive({
      autoCompleteIsActive: true,
      autoCompleteSearchValue: '',
      foundDuplicate: false,
      searchValue: '',
      loadingSearchResults: false,
      showClear: false,
      toggleDialog: false,
      dialogResults: [],
      showAllAddressErrors: false,
      isPartyTypeBusiness: computed(() => partyType.value === SecuredPartyTypes.BUSINESS),
      isPartyTypeIndividual: computed(() => partyType.value === SecuredPartyTypes.INDIVIDUAL),
      isAmendment: computed(() => registrationFlowType.value === RegistrationFlowType.AMENDMENT),
      labelText: computed((): string => {
        let text = ''
        if (props.activeIndex === -1 && (!currentSecuredParty.value?.action)) {
          text = 'Add '
        } else {
          text = (localState.isAmendment && currentSecuredParty.value?.action !== ActionTypes.ADDED)
            ? 'Amend ' : 'Edit '
        }
        text += props.isRegisteringParty ? 'Registering Party' : 'Secured Party'
        return text
      })
    })

    const showDialog = () => {
      localState.toggleDialog = true
    }

    const onBlur = fieldname => {
      validateInput(fieldname, currentSecuredParty.value[fieldname])
    }

    const closeAndReset = () => {
      localState.toggleDialog = false
      resetFormAndData(true)
    }

    const onSubmitForm = async () => {
      localState.foundDuplicate = false
      currentSecuredParty.value.address = formatAddress(currentSecuredParty.value.address)

      if (validateSecuredPartyForm(partyType.value, currentSecuredParty, props.isRegisteringParty)) {
        if (partyType.value === SecuredPartyTypes.INDIVIDUAL) {
          currentSecuredParty.value.businessName = ''
        } else {
          currentSecuredParty.value.personName.first = ''
          currentSecuredParty.value.personName.middle = ''
          currentSecuredParty.value.personName.last = ''
        }

        if (props.isRegisteringParty) {
          setRegisteringParty(currentSecuredParty.value)
          context.emit('resetEvent')
          return
        }

        // check for duplicate
        if (hasMatchingSecuredParty(currentSecuredParty.value, props.isEditMode, props.activeIndex)) {
          // trigger duplicate secured party dialog
          localState.foundDuplicate = true
          showDialog()
          return
        }

        if (currentSecuredParty.value.businessName && localState.isPartyTypeBusiness) {
          if (!isEqual(currentSecuredParty, originalSecuredParty)) {
            // go to the service and see if there are similar secured parties
            const response: [SearchPartyIF] = await partyCodeSearch(
              currentSecuredParty.value.businessName, false
            )
            // check if any results
            if (response?.length > 0) {
              // show secured party selection popup
              showDialog()
              localState.dialogResults = response?.slice(0, 50)
              return
            }
          }
        }

        addEditSecuredParty(props.activeIndex)
      } else {
        // trigger show validation
        localState.showAllAddressErrors = !localState.showAllAddressErrors
      }
    }

    const validateNameField = () => {
      if (!errors.value.first.succeeded || currentSecuredParty.value.personName.first.length > 50) {
        validateFirstName(currentSecuredParty.value, errors.value)
      }
      if (!errors.value.middle.succeeded || currentSecuredParty.value.personName.middle.length > 50) {
        validateMiddleName(currentSecuredParty.value, errors.value)
      }
      if (!errors.value.last.succeeded || currentSecuredParty.value.personName.last.length > 50) {
        validateLastName(currentSecuredParty.value, errors.value)
      }
      if (!errors.value.businessName.succeeded || currentSecuredParty.value.businessName.length > 150) {
        validateBusinessName(currentSecuredParty.value, errors.value)
      }
    }

    const setSearchValue = (searchValueTyped: string) => {
      localState.autoCompleteIsActive = false
      localState.searchValue = searchValueTyped
      currentSecuredParty.value.businessName = searchValueTyped
      localState.showClear = true
      validateNameField()
    }

    const setCloseAutoComplete = () => {
      localState.autoCompleteIsActive = false
    }

    watch(
      () => localState.searchValue,
      (val: string) => {
        localState.autoCompleteSearchValue = val
        // show autocomplete results when there is a searchValue
        localState.autoCompleteIsActive = val !== ''
        currentSecuredParty.value.businessName = val
      }
    )

    onMounted(() => {
      getSecuredParty(props.isRegisteringParty, props.activeIndex)
      currentSecuredParty.value.businessName && setSearchValue(currentSecuredParty.value.businessName)
    })

    return {
      currentSecuredParty,
      currentIsBusiness,
      partyType,
      SecuredPartyTypes,
      resetFormAndData,
      removeSecuredParty,
      onSubmitForm,
      onBlur,
      addressSchema,
      updateAddress,
      updateValidity,
      validateNameField,
      setSearchValue,
      setCloseAutoComplete,
      errors,
      closeAndReset,
      ActionTypes,
      ...toRefs(localState)
    }
  }
})
</script>

<style lang="scss" scoped>
@import '@/assets/styles/theme.scss';
::v-deep .theme--light.v-icon.mdi-close {
  color: $primary-blue !important;
}
.party-radio-business {
  width: 50%;
  background-color: rgba(0, 0, 0, 0.06);
  height: 60px;
  padding: 10px;
  margin-right: 0px !important;
}
.party-radio-individual {
  width: 47%;
  margin-right: 20px !important;
  background-color: rgba(0, 0, 0, 0.06);
  height: 60px;
  padding: 10px;
}
</style>
