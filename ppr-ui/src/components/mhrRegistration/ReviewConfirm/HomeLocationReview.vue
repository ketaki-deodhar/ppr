<template>
  <v-card flat id="home-location-summary" class="mt-10">
    <header class="review-header">
      <img
        class="ml-1 home-location-icon"
        alt="home-location-review-icon"
        src="@/assets/svgs/homelocationicon_reviewscreen.svg"
      />
      <label class="font-weight-bold pl-2">Location of Home</label>
    </header>

    <div :class="{ 'border-error-left':  showStepError && !isTransferReview }">
      <section v-if="showStepError && !isTransferReview"
        :class="{ 'pb-8': !(!!getMhrRegistrationLocation.locationType) && !hasAddress }" class="mx-6 pt-8"
      >
        <span>
          <v-icon color="error">mdi-information-outline</v-icon>
          <span class="error-text mx-1">This step is unfinished.</span>
          <router-link
            :to="{ path: `/${RouteNames.MHR_REGISTRATION}/${RouteNames.HOME_LOCATION}` }"
          >Return to this step to complete it.</router-link>
        </span>
      </section>

      <section v-if="(!!getMhrRegistrationLocation.locationType || hasAddress)"
        class="py-10" id="review-home-location-section"
      >
        <v-row no-gutters class="px-8">
          <v-col cols="3" class="pt-1">
            <h3>Location Type</h3>
          </v-col>
          <v-col cols="9" class="pt-1">
            <p>{{ locationType }}</p>
          </v-col>
        </v-row>

          <!-- Lot Type -->
          <template v-if="getMhrRegistrationLocation.locationType === HomeLocationTypes.LOT">
            <v-row no-gutters class="px-8 pt-1">
              <v-col cols="3" class="pt-1 pr-3">
                <h3>Dealer / Manufacturer Name</h3>
              </v-col>
              <v-col cols="9" class="pt-1">
                <p>{{ getMhrRegistrationLocation.dealerName || '(Not Entered)' }}</p>
              </v-col>
            </v-row>
          </template>

          <!-- Park Type -->
          <template v-if="getMhrRegistrationLocation.locationType === HomeLocationTypes.HOME_PARK">
            <v-row no-gutters class="px-8 pt-1">
              <v-col cols="3" class="pt-1">
                <h3>Park Name</h3>
              </v-col>
              <v-col cols="9" class="pt-1">
                <p>{{ getMhrRegistrationLocation.parkName || '(Not Entered)' }}</p>
              </v-col>
            </v-row>
            <v-row no-gutters class="px-8 pt-1">
              <v-col cols="3" class="pt-1">
                <h3>Pad</h3>
              </v-col>
              <v-col cols="9" class="pt-1">
                <p>{{ getMhrRegistrationLocation.pad || '(Not Entered)' }}</p>
              </v-col>
            </v-row>
          </template>

          <!-- Reserve -->
          <template v-if="getMhrRegistrationLocation.otherType === HomeLocationTypes.OTHER_RESERVE">
            <v-row no-gutters class="px-8 pt-1">
              <v-col cols="3" class="pt-1">
                <h3>Legal Land Description</h3>
              </v-col>
              <v-col cols="9" class="pt-1" v-if="hasManualEntries">
                <p>Band Name: {{ getMhrRegistrationLocation.bandName || '(Not Entered)' }}</p>
                <p>Reserve Number: {{ getMhrRegistrationLocation.reserveNumber || '(Not Entered)' }}</p>
                <p v-if="getMhrRegistrationLocation.additionalDescription">
                  Additional Description: {{ getMhrRegistrationLocation.additionalDescription }}
                </p>

                <p v-if="getMhrRegistrationLocation.lot" class="pt-4">
                  Lot: {{ getMhrRegistrationLocation.lot }}
                </p>
                <p v-if="getMhrRegistrationLocation.parcel">
                  Parcel: {{ getMhrRegistrationLocation.parcel }}
                </p>
                <p v-if="getMhrRegistrationLocation.block">
                  Block: {{ getMhrRegistrationLocation.block }}
                </p>
                <p v-if="getMhrRegistrationLocation.districtLot">
                  District Lot: {{ getMhrRegistrationLocation.districtLot }}
                </p>
                <p v-if="getMhrRegistrationLocation.partOf">
                  Part of: {{ getMhrRegistrationLocation.partOf }}
                </p>
                <p v-if="getMhrRegistrationLocation.section">
                  Section: {{ getMhrRegistrationLocation.section }}
                </p>
                <p v-if="getMhrRegistrationLocation.township">
                  Township: {{ getMhrRegistrationLocation.township }}
                </p>
                <p v-if="getMhrRegistrationLocation.range">
                  Range: {{ getMhrRegistrationLocation.range }}
                </p>
                <p v-if="getMhrRegistrationLocation.meridian">
                  Meridian: {{ getMhrRegistrationLocation.meridian }}
                </p>
                <p v-if="getMhrRegistrationLocation.landDistrict">
                  Land District: {{ getMhrRegistrationLocation.landDistrict }}
                </p>
                <p v-if="getMhrRegistrationLocation.plan">
                  Plan: {{ getMhrRegistrationLocation.plan }}
                </p>
                <p v-if="getMhrRegistrationLocation.exceptionPlan">
                  Except Plan: {{ getMhrRegistrationLocation.exceptionPlan }}
                </p>
              </v-col>
              <v-col v-else>
                <p>(Not Entered)</p>
              </v-col>
            </v-row>
          </template>

          <!-- PID -->
          <template v-if="includesPid">
            <!-- PID Entered-->
            <template v-if="!getIsManualLocation">
              <v-row no-gutters class="px-8 pt-1">
                <v-col cols="3" class="pt-1">
                  <h3>PID Number</h3>
                </v-col>
                <v-col cols="9" class="pt-1">
                  <p>{{ displayPid || '(Not Entered)' }}</p>
                </v-col>
              </v-row>
              <v-row no-gutters v-if="getMhrRegistrationLocation.legalDescription" class="px-8 pt-1">
                <v-col cols="3" class="pt-1">
                  <h3>Legal Land Description</h3>
                </v-col>
                <v-col cols="9" class="pt-1">
                  <p>{{ getMhrRegistrationLocation.legalDescription }}</p>
                </v-col>
              </v-row>
            </template>

            <!-- No PID -->
            <v-row no-gutters v-else class="px-8 pt-1">
              <v-col cols="3" class="pt-1">
                <h3>Legal Land Description</h3>
              </v-col>
              <v-col cols="9" class="pt-1" v-if="hasManualEntries">
                <p v-if="getMhrRegistrationLocation.otherType !== HomeLocationTypes.OTHER_TYPE ||
                  getMhrRegistrationLocation.lot"
                >
                  {{ displayStrata ? 'Strata ' : '' }}Lot: {{ getMhrRegistrationLocation.lot || '(Not Entered)' }}
                </p>
                <p v-if="getMhrRegistrationLocation.parcel">
                  Parcel: {{ getMhrRegistrationLocation.parcel }}
                </p>
                <p v-if="getMhrRegistrationLocation.block">
                  Block: {{ getMhrRegistrationLocation.block }}
                </p>
                <p v-if="getMhrRegistrationLocation.districtLot">
                  District Lot: {{ getMhrRegistrationLocation.districtLot }}
                </p>
                <p v-if="getMhrRegistrationLocation.partOf">
                  Part of: {{ getMhrRegistrationLocation.partOf }}
                </p>
                <p v-if="getMhrRegistrationLocation.section">
                  Section: {{ getMhrRegistrationLocation.section }}
                </p>
                <p v-if="getMhrRegistrationLocation.township">
                  Township: {{ getMhrRegistrationLocation.township }}
                </p>
                <p v-if="getMhrRegistrationLocation.range">
                  Range: {{ getMhrRegistrationLocation.range }}
                </p>
                <p v-if="getMhrRegistrationLocation.meridian">
                  Meridian: {{ getMhrRegistrationLocation.meridian }}
                </p>
                <p v-if="getMhrRegistrationLocation.otherType !== HomeLocationTypes.OTHER_TYPE ||
                  getMhrRegistrationLocation.landDistrict"
                >
                  Land District: {{ getMhrRegistrationLocation.landDistrict || '(Not Entered)' }}
                </p>
                <p v-if="getMhrRegistrationLocation.otherType !== HomeLocationTypes.OTHER_TYPE ||
                  getMhrRegistrationLocation.plan"
                >
                  {{ displayStrata ? 'Strata ' : '' }}Plan: {{ getMhrRegistrationLocation.plan || '(Not Entered)' }}
                </p>
                <p v-if="getMhrRegistrationLocation.exceptionPlan" class="pt-3 pb-1">
                  Except Plan: {{ getMhrRegistrationLocation.exceptionPlan }}
                </p>
              </v-col>
              <v-col cols="9" class="pt-1" v-else>
                <p>(Not Entered)</p>
              </v-col>
            </v-row>

            <!-- Additional Details -->
            <v-row no-gutters class="px-8 pt-1">
              <v-col cols="3" class="pt-1">
                <h3>Additional Description</h3>
              </v-col>
              <v-col cols="9" class="pt-1">
                <p>{{ getMhrRegistrationLocation.additionalDescription || '(Not Entered)' }}</p>
              </v-col>
            </v-row>
          </template>

          <!-- Civic Address -->
          <v-row no-gutters class="px-8 pt-1" >
            <v-col cols="3" class="pt-1">
              <h3>Civic Address</h3>
            </v-col>
            <v-col cols="9" class="pt-1">
              <p v-if="hasAddress">
                {{ getMhrRegistrationLocation.address.street }}<br/>
                <span v-if="!!getMhrRegistrationLocation.address.streetAdditional">
                  {{getMhrRegistrationLocation.address.streetAdditional}}<br/>
                </span>
                {{ getMhrRegistrationLocation.address.city }}
                {{ getMhrRegistrationLocation.address.region }}
                <br>{{ getCountryName(getMhrRegistrationLocation.address.country) }}
              </p>
              <p v-else>
                {{ '(Not Entered)' }}
              </p>
            </v-col>
          </v-row>

          <template v-if="!isMhrManufacturerRegistration && !isTransferReview">
            <v-divider class="mx-4 mt-6"/>

            <!-- Land Details -->
            <v-row no-gutters class="px-8 pt-6" >
              <v-col cols="3" class="pt-1">
                <h3>Land Details</h3>
              </v-col>
            </v-row>

            <!-- Lease or Land Ownership -->
            <v-row no-gutters class="px-8 pt-1" >
              <v-col cols="3" class="pt-1">
                <h3>Lease or Land Ownership</h3>
              </v-col>
              <v-col cols="9" class="pt-1">
                <p>
                  <span v-html="landOwnershipLabel"></span>
                </p>
              </v-col>
            </v-row>
          </template>

      </section>
    </div>
  </v-card>
</template>

<script lang="ts">
import { computed, defineComponent, reactive, toRefs } from 'vue-demi'
import { HomeLocationTypes, RouteNames } from '@/enums'
import { useStore } from '@/store/store'
import { useMhrValidations } from '@/composables'
import { storeToRefs } from 'pinia'
import { useCountriesProvinces } from '@/composables/address/factories'

export default defineComponent({
  name: 'HomeLocationReview',
  props: {
    isTransferReview: {
      type: Boolean,
      default: false
    }
  },
  setup () {
    const {
      getMhrRegistrationLocation,
      getMhrRegistrationValidationModel,
      getIsManualLocation,
      getMhrRegistrationOwnLand,
      isMhrManufacturerRegistration
    } = storeToRefs(useStore())

    const {
      MhrSectVal,
      getStepValidation
    } = useMhrValidations(toRefs(getMhrRegistrationValidationModel.value))
    const countryProvincesHelpers = useCountriesProvinces()

    const localState = reactive({
      includesPid: computed((): boolean => {
        return [HomeLocationTypes.OTHER_STRATA, HomeLocationTypes.OTHER_TYPE]
          .includes(getMhrRegistrationLocation.value.otherType)
      }),
      hasAddress: computed((): boolean => {
        return getMhrRegistrationLocation.value.address?.street ||
        getMhrRegistrationLocation.value.address?.streetAdditional ||
        getMhrRegistrationLocation.value.address?.city
      }),
      displayPid: computed((): string => {
        return getMhrRegistrationLocation.value.pidNumber.replace(/(\d{3})(\d{3})(\d{3})/, '$1-$2-$3')
      }),
      displayStrata: computed((): boolean => {
        return getMhrRegistrationLocation.value.otherType === HomeLocationTypes.OTHER_STRATA
      }),
      locationType: computed((): string => {
        switch (getMhrRegistrationLocation.value.locationType) {
          case HomeLocationTypes.LOT:
            return 'Dealer\'s / Manufacturer\'s lot'
          case HomeLocationTypes.HOME_PARK:
            return 'Manufactured home park (other than a strata park)'
          case HomeLocationTypes.OTHER_LAND:
            switch (getMhrRegistrationLocation.value.otherType) {
              case HomeLocationTypes.OTHER_RESERVE:
                return 'Indian Reserve'
              case HomeLocationTypes.OTHER_STRATA:
                return 'Strata'
              case HomeLocationTypes.OTHER_TYPE:
                return 'Other'
              default:
                return '(Not Entered)'
            }
          default:
            return '(Not Entered)'
        }
      }),
      hasManualEntries: computed((): boolean => {
        const location = getMhrRegistrationLocation.value
        return !!location.lot || !!location.parcel || !!location.block || !!location.districtLot || !!location.partOf ||
          !!location.section || !!location.township || !!location.range || !!location.meridian || !!location.bandName ||
          !!location.landDistrict || !!location.plan || !!location.exceptionPlan || !!location.reserveNumber
      }),
      landOwnershipLabel: computed(() => {
        return `The manufactured home is <b>${getMhrRegistrationOwnLand.value ? '' : 'not'}</b> located on land that the
            homeowners own, or on which they have a registered lease of 3 years or more.`
      }),
      showStepError: computed(() => {
        return !isMhrManufacturerRegistration.value && !getStepValidation(MhrSectVal.LOCATION_VALID)
      })
    })

    return {
      HomeLocationTypes,
      RouteNames,
      MhrSectVal,
      getStepValidation,
      getMhrRegistrationLocation,
      getIsManualLocation,
      isMhrManufacturerRegistration,
      ...countryProvincesHelpers,
      ...toRefs(localState)
    }
  }
})
</script>

<style lang="scss" scoped>
@import '@/assets/styles/theme.scss';
#home-location-summary {
  h3 {
    line-height: unset;
  }

  p {
    margin-bottom: unset;
    line-height: 24px;
    color: $gray7;
  }
}

.error-text {
  font-size: 16px;
}
</style>
