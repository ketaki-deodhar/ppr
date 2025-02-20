<template>
  <v-container fluid class="view-container breadcrumb-row px-15 py-0">
    <div class="container pa-0">
      <v-row no-gutters class="container" style="padding: 6px 0;">
        <v-col cols="auto">
          <v-row no-gutters>
            <v-col cols="auto">
              <v-btn id="breadcrumb-back-btn" class="back-btn" exact icon small @click="navigate()">
                <v-icon>mdi-arrow-left</v-icon>
              </v-btn>
            </v-col>
            <v-col class="pl-3" cols="auto" style="padding-top: 2px;">
              <div style="border-right: thin solid #ced4da; height: 28px;" />
            </v-col>
          </v-row>
        </v-col>

        <v-col cols="auto" class="pl-3" style="padding-top: 6px;">
          <v-breadcrumbs class="pa-0 breadcrumb-text" :items="breadcrumbs">
            <template v-slot:item="{ item }">
              <v-breadcrumbs-item
                class="breadcrumb-text"
                data-test-id='breadcrumb-item'
                :disabled="item.disabled"
                :to="item.to"
                :href="item.href"
              >
                {{ handleStaff(item.text) }}
              </v-breadcrumbs-item>
            </template>
            <template v-slot:divider>
              <v-icon color="white" class="px-1">mdi-chevron-right</v-icon>
            </template>
          </v-breadcrumbs>
        </v-col>
      </v-row>
    </div>
  </v-container>
</template>
<script lang="ts">
// external
import { computed, defineComponent, reactive, toRefs, Ref } from 'vue-demi' // eslint-disable-line
import { useRoute, useRouter } from 'vue2-helpers/vue-router'
import { useStore } from '@/store/store'
// local
import { BreadcrumbIF } from '@/interfaces' // eslint-disable-line
import {
  tombstoneBreadcrumbDashboard,
  tombstoneBreadcrumbDischarge,
  tombstoneBreadcrumbRenewal,
  tombstoneBreadcrumbAmendment,
  tombstoneBreadcrumbRegistration,
  tombstoneBreadcrumbSearch,
  tombstoneBreadcrumbSearchConfirm,
  breadcrumbsTitles,
  tombstoneBreadcrumbMhrInformation,
  tombstoneBreadcrumbMhrUnitNote,
  tombstoneBreadcrumbQsApplication,
  tombstoneBreadcrumbExemption
} from '@/resources'
import { RouteNames } from '@/enums'
import { getRoleProductCode } from '@/utils'
import { storeToRefs } from 'pinia'
import { UnitNotesInfo } from '@/resources/unitNotes'

export default defineComponent({
  name: 'Breadcrumb',
  setup () {
    const route = useRoute()
    const router = useRouter()
    const {
      // Getters
      getRegistrationNumber,
      getRegistrationType,
      isRoleStaff,
      getUserRoles,
      getUserProductSubscriptionsCodes,
      getMhrInformation,
      getMhrUnitNoteType
    } = storeToRefs(useStore())

    const localState = reactive({
      backUrl: computed((): any => {
        const length = localState.breadcrumbs?.length || 0
        if (length > 1) {
          return localState.breadcrumbs[length - 1].to || localState.breadcrumbs[length - 2].href ||
            sessionStorage.getItem('REGISTRY_URL')
        }
        return ''
      }),
      breadcrumbs: computed((): Array<BreadcrumbIF> => {
        const roleBasedBreadcrumbTitle = breadcrumbsTitles[
          getRoleProductCode(getUserRoles.value, getUserProductSubscriptionsCodes.value)
        ]
        const allTombstoneBreadcrumbs = [
          tombstoneBreadcrumbDashboard,
          tombstoneBreadcrumbDischarge,
          tombstoneBreadcrumbRenewal,
          tombstoneBreadcrumbAmendment,
          tombstoneBreadcrumbRegistration,
          tombstoneBreadcrumbSearch,
          tombstoneBreadcrumbSearchConfirm,
          tombstoneBreadcrumbMhrInformation,
          tombstoneBreadcrumbMhrUnitNote
        ]
        if (isRoleStaff.value) {
          for (const tombstoneBreadcrumb of allTombstoneBreadcrumbs) {
            tombstoneBreadcrumb[0].text = 'Staff Dashboard'
          }
        }
        if ((route.name === RouteNames.DASHBOARD) || (route.name === RouteNames.SIGN_IN)) {
          tombstoneBreadcrumbDashboard[1].text = roleBasedBreadcrumbTitle || tombstoneBreadcrumbDashboard[1].text
          return tombstoneBreadcrumbDashboard
        } else if ((route.name === RouteNames.SEARCH) || (route.name === RouteNames.MHRSEARCH)) {
          tombstoneBreadcrumbSearch[1].text = roleBasedBreadcrumbTitle
          return tombstoneBreadcrumbSearch
        } else if (route.name === RouteNames.MHRSEARCH_CONFIRM) {
          tombstoneBreadcrumbSearchConfirm[1].text = roleBasedBreadcrumbTitle ||
            tombstoneBreadcrumbSearchConfirm[1].text
          return tombstoneBreadcrumbSearchConfirm
        } else if (route.path?.includes('user-access')) {
          tombstoneBreadcrumbQsApplication[1].text = roleBasedBreadcrumbTitle ||
            tombstoneBreadcrumbQsApplication[1].text
          return tombstoneBreadcrumbQsApplication
        } else if (route.path?.includes('discharge')) {
          const dischargeBreadcrumb = [...tombstoneBreadcrumbDischarge]
          dischargeBreadcrumb[1].text = roleBasedBreadcrumbTitle
          dischargeBreadcrumb[2].text =
            `Base Registration ${getRegistrationNumber.value} - Total Discharge` || dischargeBreadcrumb[2].text
          return dischargeBreadcrumb
        } else if (route.path?.includes('renew')) {
          const renewBreadcrumb = [...tombstoneBreadcrumbRenewal]
          renewBreadcrumb[1].text = roleBasedBreadcrumbTitle || renewBreadcrumb[1].text
          renewBreadcrumb[2].text =
            `Base Registration ${getRegistrationNumber.value} - Renewal` || renewBreadcrumb[2].text
          return renewBreadcrumb
        } else if (route.path?.includes('amend')) {
          const amendBreadcrumb = [...tombstoneBreadcrumbAmendment]
          amendBreadcrumb[1].text = roleBasedBreadcrumbTitle || amendBreadcrumb[1].text
          amendBreadcrumb[2].text =
            `Base Registration ${getRegistrationNumber.value} - Amendment` || amendBreadcrumb[2].text
          return amendBreadcrumb
        } else if (route.name === RouteNames.MHR_INFORMATION) {
          const mhrInfoBreadcrumb = [...tombstoneBreadcrumbMhrInformation]
          mhrInfoBreadcrumb[2].text = `MHR Number ${getMhrInformation.value.mhrNumber}`
          return mhrInfoBreadcrumb
        } else if (route.name === RouteNames.MHR_INFORMATION_NOTE) {
          const mhrUnitNoteBreadcrumb = [...tombstoneBreadcrumbMhrUnitNote]
          mhrUnitNoteBreadcrumb[2].text = `MHR Number ${getMhrInformation.value.mhrNumber}`
          mhrUnitNoteBreadcrumb[3].text = UnitNotesInfo[getMhrUnitNoteType.value].header
          return mhrUnitNoteBreadcrumb
        } else if (route.path?.includes('exemption')) {
          return tombstoneBreadcrumbExemption
        } else {
          const registrationBreadcrumb = [...tombstoneBreadcrumbRegistration]
          registrationBreadcrumb[1].text = roleBasedBreadcrumbTitle || registrationBreadcrumb[1].text
          registrationBreadcrumb[2].text =
            getRegistrationType.value?.registrationTypeUI || registrationBreadcrumb[2].text
          return registrationBreadcrumb
        }
      })
    })

    const handleStaff = (breadcrumbText): string => {
      if (isRoleStaff.value) {
        breadcrumbText = breadcrumbText.replace('My', 'Staff')
      }
      return breadcrumbText
    }

    const buildHref = (href: string): string => {
      return `${href}${getParams()}`
    }

    const navigate = (): void => {
      const breadcrumb = localState.breadcrumbs[localState.breadcrumbs.length - 2] as BreadcrumbIF

      if (breadcrumb.to) {
        router.push(breadcrumb.to).catch(error => error)
      } else if (breadcrumb.href) {
        window.location.assign(buildHref(breadcrumb.href))
      }
    }

    /** Returns URL param string with Account ID if present, else empty string. */
    const getParams = (): string => {
      const accountId = sessionStorage.getItem('ACCOUNT_ID')
      return accountId ? `?accountid=${accountId}` : ''
    }

    return {
      handleStaff,
      navigate,
      ...toRefs(localState)
    }
  }
})
</script>

<style lang="scss" scoped>
@import '@/assets/styles/theme.scss';
.back-btn {
  background-color: white;
  color: $primary-blue !important;
  height: 32px !important;
  width: 32px !important;
}
.breadcrumb-row {
  background-color: $BCgovBlue3-5;
  color: white;
}
.breadcrumb-text {
  color: white !important;
  font-size: 0.8125rem !important;
}
::v-deep {
  .v-breadcrumbs__item {
    color: white !important;
  }

  .v-breadcrumbs__item:not(.v-breadcrumbs__item--disabled){
    text-decoration: underline !important;
  }

  .v-breadcrumbs__item--disabled {
    opacity: unset;
  }
}
</style>
