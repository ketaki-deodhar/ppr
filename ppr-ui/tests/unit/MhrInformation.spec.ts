// Libraries
import Vue, { nextTick } from 'vue'
import Vuetify from 'vuetify'
import { createPinia, setActivePinia } from 'pinia'
import { useStore } from '../../src/store/store'
import VueRouter from 'vue-router'
import { createLocalVue, mount, Wrapper } from '@vue/test-utils'

// local components
import { HomeOwners, MhrInformation } from '@/views'
import {
  AccountInfo,
  CautionBox,
  StickyContainer,
  CertifyInformation,
  SharedDatePicker,
  ContactInformation,
  DocumentId,
  LienAlert
} from '@/components/common'
import mockRouter from './MockRouter'
import {
  AuthRoles,
  HomeTenancyTypes,
  RouteNames,
  ApiTransferTypes,
  UITransferTypes,
  ProductCode,
  UnitNoteDocTypes
} from '@/enums'
import { HomeOwnersTable } from '@/components/mhrRegistration/HomeOwners'
import { getTestId } from './utils'
import {
  mockedAddedPerson,
  mockedRemovedPerson,
  mockedOrganization,
  mockedPerson,
  mockMhrTransferCurrentHomeOwner,
  mockedRegisteringParty1,
  mockedAccountInfo,
  mockedLockedMhRegistration,
  mockedUnitNotes5,
  mockedPerson2,
  mockedExecutor,
  mockedAdministrator,
  mockedResidentialExemptionOrder,
  mockedUnitNotes3
} from './test-data'
import {
  CertifyIF,
  MhrRegistrationHomeOwnerGroupIF,
  MhrRegistrationHomeOwnerIF,
  TransferTypeSelectIF
} from '@/interfaces'
import { TransferDetails, TransferDetailsReview, TransferType } from '@/components/mhrTransfers'

import { defaultFlagSet, toDisplayPhone } from '@/utils'
import { UnitNotesInfo } from '@/resources'

Vue.use(Vuetify)

const vuetify = new Vuetify({})
setActivePinia(createPinia())
const store = useStore()

/**
 * Creates and mounts a component, so that it can be tested.
 *
 * @returns a Wrapper<any> object with the given parameters.
 */
function createComponent (): Wrapper<any> {
  const localVue = createLocalVue()
  localVue.use(Vuetify)
  localVue.use(VueRouter)
  const router = mockRouter.mock()
  router.push({
    name: RouteNames.MHR_INFORMATION
  })

  document.body.setAttribute('data-app', 'true')
  return mount(MhrInformation as any, {
    localVue,
    store,
    propsData: {
      appReady: true,
      isMhrTransfer: true
    },
    vuetify,
    stubs: { Affix: true },
    router
  })
}

const TRANSFER_DECLARED_VALUE = '123'
const TRANSFER_CONSIDERATION = `$${TRANSFER_DECLARED_VALUE}.00`
const TRANSFER_DATE = '2020-10-10'

// TODO: Remove after API updates to include the ID for Owners
function addIDsForOwners (ownersGroups): Array<any> {
  // Create an ID to each individual owner for UI Tracking
  ownersGroups.forEach(ownerGroup => {
    for (const [index, owner] of ownerGroup.owners.entries()) {
      owner.ownerId = ownerGroup.groupId + (index + 1)
    }
  })

  return ownersGroups
}

async function setupCurrentHomeOwners (): Promise<void> {
  await store.setMhrTransferCurrentHomeOwnerGroups([mockMhrTransferCurrentHomeOwner])
  // TODO: Remove after API updates to include the ID for Owners
  const homeOwnerWithIdsArray = addIDsForOwners([mockMhrTransferCurrentHomeOwner])
  await store.setMhrTransferHomeOwnerGroups(homeOwnerWithIdsArray)
}

async function setupCurrentMultipleHomeOwnersGroups (): Promise<void> {
  // setup two groups so they can be shown in the table
  const currentHomeOwnersGroups = [
    mockMhrTransferCurrentHomeOwner,
    {
      ...mockMhrTransferCurrentHomeOwner,
      groupId: 2
    }
  ]

  await store.setMhrTransferCurrentHomeOwnerGroups(currentHomeOwnersGroups)
  // TODO: Remove after API updates to include the ID for Owners
  const homeOwnerWithIdsArray = addIDsForOwners(currentHomeOwnersGroups)
  await store.setMhrTransferHomeOwnerGroups(homeOwnerWithIdsArray)
}

async function triggerUnsavedChange (): Promise<void> {
  // set unsaved changes to make Transfer Details visible
  await store.setUnsavedChanges(true)
  await nextTick()
}

// For future use when Transfer Details will be required to go to Review
async function enterTransferDetailsFields (transferDetailsWrapper: Wrapper<any, Element>): Promise<void> {
  transferDetailsWrapper.find(getTestId('consideration')).trigger('mousedown')
  transferDetailsWrapper.findComponent(SharedDatePicker).vm.$emit('emitDate', TRANSFER_DATE)
  await nextTick()
}

async function enterTransferTypeFields (transferTypeWrapper: Wrapper<any, Element>): Promise<void> {
  transferTypeWrapper.find(getTestId('declared-value')).setValue(TRANSFER_DECLARED_VALUE)
  transferTypeWrapper.find(getTestId('declared-value')).trigger('blur')
  await nextTick()
}

describe('Mhr Information', () => {
  let wrapper: Wrapper<any>
  const currentAccount = {
    id: 'test_id'
  }
  sessionStorage.setItem('KEYCLOAK_TOKEN', 'token')
  sessionStorage.setItem('CURRENT_ACCOUNT', JSON.stringify(currentAccount))
  sessionStorage.setItem('AUTH_API_URL', 'https://bcregistry-bcregistry-mock.apigee.net/mockTarget/auth/api/v1/')

  const LEGAL_NAME = 'TEST NAME'

  beforeEach(async () => {
    defaultFlagSet['mhr-transfer-enabled'] = true
    await store.setCertifyInformation({
      valid: false,
      certified: false,
      legalName: LEGAL_NAME,
      registeringParty: mockedRegisteringParty1
    } as CertifyIF)
    wrapper = createComponent()
  })

  afterEach(() => {
    wrapper.destroy()
  })

  it('renders and displays the Mhr Information View', async () => {
    setupCurrentHomeOwners()
    wrapper.vm.dataLoaded = true
    await nextTick()

    expect(wrapper.vm.getMhrTransferCurrentHomeOwnerGroups.length).toBe(1)
    expect(wrapper.vm.getMhrTransferHomeOwners.length).toBe(1)

    expect(wrapper.findComponent(MhrInformation).exists()).toBe(true)
    expect(wrapper.find('#mhr-information-header').text()).toContain('Manufactured Home Information')
    expect(wrapper.findComponent(LienAlert).exists()).toBe(false)

    expect(wrapper.findComponent(TransferType).exists()).toBe(false)

    expect(wrapper.findComponent(HomeOwners).exists()).toBeTruthy()
    const homeOwnersTable = wrapper.findComponent(HomeOwnersTable)
    expect(homeOwnersTable.exists()).toBeTruthy()
    expect(homeOwnersTable.text()).toContain(mockMhrTransferCurrentHomeOwner.owners[0].organizationName)
    expect(homeOwnersTable.text()).toContain(mockMhrTransferCurrentHomeOwner.owners[0].address.city)
  })

  it('renders and displays the correct sub components', async () => {
    wrapper.vm.dataLoaded = true
    await nextTick()

    expect(wrapper.findComponent(LienAlert).exists()).toBe(false)
    // Verify it does render before changes
    expect(wrapper.findComponent(StickyContainer).exists()).toBe(false)
    expect(wrapper.findComponent(DocumentId).exists()).toBe(false)
    expect(wrapper.findComponent(TransferType).exists()).toBe(false)
    expect(wrapper.findComponent(TransferDetails).exists()).toBe(false)

    await wrapper.find('#home-owners-change-btn').trigger('click')
    await nextTick()

    // Sticky container w/ Fee Summary, Document Id, Transfer Type and Transfer Details components
    expect(wrapper.findComponent(StickyContainer).exists()).toBe(true)
    // Document Id should not exists because the role isn't staff
    expect(wrapper.findComponent(DocumentId).exists()).toBeFalsy()
    expect(wrapper.findComponent(TransferType).exists()).toBe(true)
    await store.setUnsavedChanges(true)
    await nextTick()
    expect(wrapper.findComponent(TransferDetails).exists()).toBe(true)
    // reset staff role
    await store.setAuthRoles([AuthRoles.MHR])
  })

  it('should show Document Id component for Staff transfers only', async () => {
    wrapper.vm.dataLoaded = true
    await nextTick()

    // initial check that Document Id isn't showing
    expect(wrapper.findComponent(DocumentId).exists()).toBeFalsy()

    await wrapper.find('#home-owners-change-btn').trigger('click')

    // Document Id should not exists for non-staff
    expect(wrapper.findComponent(DocumentId).exists()).toBeFalsy()

    await store.setAuthRoles([AuthRoles.STAFF])
    await nextTick()
    // Document Id should exists because the role is staff
    expect(wrapper.findComponent(DocumentId).exists()).toBeTruthy()
    // reset staff role
    await store.setAuthRoles([AuthRoles.MHR])
  })

  it('should render Added badge after Owner is added to the table', async () => {
    setupCurrentHomeOwners()
    wrapper.vm.dataLoaded = true
    await nextTick()

    const mhrInformationComponent = wrapper
    expect(mhrInformationComponent.exists()).toBeTruthy()
    wrapper.vm.dataLoaded = true
    await nextTick()

    expect(mhrInformationComponent.findComponent(HomeOwnersTable).exists()).toBeTruthy()

    // same IF for Transfer and Registration
    const owners = [mockedAddedPerson, mockedRemovedPerson] as MhrRegistrationHomeOwnerIF[]
    const homeOwnerGroup = [
      mockMhrTransferCurrentHomeOwner,
      { groupId: 1, owners: owners }
    ] as MhrRegistrationHomeOwnerGroupIF[]

    await store.setMhrTransferHomeOwnerGroups(homeOwnerGroup)

    const ownersTable = mhrInformationComponent.findComponent(HomeOwners).findComponent(HomeOwnersTable)

    const newlyAddedOwner = ownersTable.find(getTestId(`owner-info-${mockedPerson.ownerId}`))
    expect(newlyAddedOwner.text()).toContain(mockedPerson.individualName.first)
    expect(newlyAddedOwner.text()).toContain(mockedPerson.individualName.last)

    const addedBadge = newlyAddedOwner.find(getTestId('ADDED-badge'))
    expect(addedBadge.isVisible()).toBeTruthy()

    const removedBadge = ownersTable.find(getTestId('DELETED-badge'))
    expect(removedBadge.isVisible()).toBeTruthy()
  })

  it('should show correct Home Tenancy Type for MHR Transfers', async () => {
    await store.setMhrTransferHomeOwnerGroups([
      {
        ...mockMhrTransferCurrentHomeOwner,
        interestNumerator: null,
        interestDenominator: null
      }
    ])

    wrapper.vm.dataLoaded = true
    await nextTick()

    const homeOwnerGroup = [{ groupId: 1, owners: [mockedPerson], type: '' }]
    const homeOwnersComponent = wrapper.findComponent(HomeOwners) as Wrapper<any>

    expect(homeOwnersComponent.vm.getHomeOwners.length).toBe(1)
    expect(wrapper.findComponent(HomeOwners).find(getTestId('home-owner-tenancy-type')).text()).toBe(
      HomeTenancyTypes.SOLE
    )

    // Add a second Owner to the existing group
    homeOwnerGroup[0].owners.push(mockedOrganization)

    await store.setMhrTransferHomeOwnerGroups(homeOwnerGroup)
    await nextTick()

    expect(homeOwnersComponent.vm.getHomeOwners.length).toBe(2)
    expect(wrapper.findComponent(HomeOwners).find(getTestId('home-owner-tenancy-type')).text()).toBe(
      HomeTenancyTypes.JOINT
    )

    // Enable Groups
    homeOwnerGroup.push({ groupId: 2, owners: [mockedPerson], type: '' })
    await nextTick()

    expect(wrapper.findComponent(HomeOwners).find(getTestId('home-owner-tenancy-type')).text()).toBe(
      HomeTenancyTypes.COMMON
    )
  })

  it('should correctly show current and newly added Owner Groups', async () => {
    setupCurrentMultipleHomeOwnersGroups()
    wrapper.vm.dataLoaded = true
    await nextTick()

    // check current Owners and Groups
    const homeOwnersComponent = wrapper.findComponent(HomeOwners) as Wrapper<any>
    homeOwnersComponent.vm.setShowGroups(true)
    await nextTick()

    expect(homeOwnersComponent.vm.getMhrTransferCurrentHomeOwnerGroups.length).toBe(2)
    expect(store.getMhrTransferHomeOwnerGroups.length).toBe(2)

    const homeOwnersTable = homeOwnersComponent.findComponent(HomeOwnersTable)

    const currentOwnerGroupHeader = homeOwnersTable.find(
      `#mhr-home-edit-owners-group-${mockMhrTransferCurrentHomeOwner.groupId}`
    )
    expect(currentOwnerGroupHeader.text()).toContain(`Group ${mockMhrTransferCurrentHomeOwner.groupId}`)
    expect(currentOwnerGroupHeader.text()).toContain('Owners: 1')

    expect(homeOwnersTable.findAll('.owner-info').length).toBe(2)
    const currentOwnerInfo = homeOwnersTable.findAll('.owner-info').at(0)

    expect(currentOwnerInfo.text()).toContain(mockMhrTransferCurrentHomeOwner.owners[0].organizationName)
    expect(currentOwnerInfo.text()).toContain(mockMhrTransferCurrentHomeOwner.owners[0].address.city)

    // Get current Groups
    const homeOwnerGroups = store.getMhrTransferHomeOwnerGroups as MhrRegistrationHomeOwnerGroupIF[]

    // Add a second Group
    const NEW_GROUP_ID = 3
    const newHomeOwnerGroup = { groupId: NEW_GROUP_ID, owners: [mockedPerson] } as MhrRegistrationHomeOwnerGroupIF
    homeOwnerGroups.push(newHomeOwnerGroup)
    await store.setMhrTransferHomeOwnerGroups(homeOwnerGroups)
    await nextTick()

    // Check that new Groups and Owner info are added to the table
    expect(store.getMhrTransferHomeOwnerGroups.length).toBe(3)
    expect(homeOwnersTable.findAll('.owner-info').length).toBe(3)

    const newOwnerGroupHeader = homeOwnersTable.find(`#mhr-home-edit-owners-group-${NEW_GROUP_ID}`)
    expect(newOwnerGroupHeader.text()).toContain(`Group ${NEW_GROUP_ID}`)

    const newOwnerInfo = homeOwnersTable.findAll('.owner-info').at(2)
    expect(newOwnerInfo.text()).toContain(mockedPerson.individualName.first)
    expect(newOwnerInfo.text()).toContain(mockedPerson.address.city)
  })

  // TRANSFER DETAILS COMPONENT TESTS

  it('should render Transfer Details component', async () => {
    setupCurrentHomeOwners()
    wrapper.vm.dataLoaded = true
    await nextTick()

    expect(wrapper.vm.getMhrTransferCurrentHomeOwnerGroups.length).toBe(1)
    expect(wrapper.vm.getMhrTransferHomeOwners.length).toBe(1)

    expect(wrapper.findComponent(DocumentId).exists()).toBeFalsy()
    expect(wrapper.findComponent(TransferDetails).exists()).toBeFalsy()
    expect(wrapper.findComponent(HomeOwnersTable).exists()).toBeTruthy()

    // Add some owners so Transfer Details will display
    // same IF for Transfer and Registration
    const owners = [mockedAddedPerson, mockedRemovedPerson] as MhrRegistrationHomeOwnerIF[]
    const homeOwnerGroup = [
      mockMhrTransferCurrentHomeOwner,
      { groupId: 1, owners: owners }
    ] as MhrRegistrationHomeOwnerGroupIF[]

    await store.setMhrTransferHomeOwnerGroups(homeOwnerGroup)

    expect(wrapper.exists()).toBe(true)

    const mhrTransferDetailsComponent: Wrapper<any> = wrapper.findComponent(TransferDetails)
    expect(mhrTransferDetailsComponent.exists()).toBeTruthy()

    await wrapper.find('#home-owners-change-btn').trigger('click')
    await nextTick()

    // Document Id should not exists because role is not staff
    expect(wrapper.findComponent(DocumentId).exists()).toBeFalsy()

    const mhrTransferTypeComponent = wrapper.findComponent(TransferType)
    expect(mhrTransferTypeComponent.exists()).toBeTruthy()
    await enterTransferTypeFields(mhrTransferTypeComponent)
    await nextTick()

    // Check for component's fields
    // expect(mhrTransferDetailsComponent.find(getTestId('declared-value')).exists()).toBeFalsy()
    expect(mhrTransferDetailsComponent.find(getTestId('consideration')).exists()).toBeTruthy()
    expect(mhrTransferDetailsComponent.find(getTestId('transfer-date')).exists()).toBeTruthy()
    expect(mhrTransferDetailsComponent.find(getTestId('lease-own-checkbox')).exists()).toBeTruthy()
    mhrTransferDetailsComponent.find(getTestId('consideration')).trigger('mousedown')
    await nextTick()

    // Check that Consideration displayed Declared Value on blur
    expect(mhrTransferDetailsComponent.vm.consideration).toBe('$123.00')
  })

  it('should render Attention or Reference Number section on Review screen', async () => {
    setupCurrentHomeOwners()
    wrapper.vm.dataLoaded = true
    wrapper.vm.showTransferType = true
    await nextTick()

    expect(wrapper.find('#transfer-ref-num-section').exists()).toBeFalsy()

    // Set Wrapper Validations
    wrapper.vm.setValidation('isDocumentIdValid', true)
    wrapper.vm.setValidation('isValidTransferType', true)
    wrapper.vm.setValidation('isValidTransferOwners', true)
    wrapper.vm.setValidation('isTransferDetailsValid', true)

    // go to Review screen
    await triggerUnsavedChange()
    await enterTransferDetailsFields(wrapper.findComponent(TransferDetails))

    await wrapper.find('#btn-stacked-submit').trigger('click')
    await nextTick()

    const section = 'transfer-ref-num-section'

    expect(wrapper.find(`#${section}`).exists()).toBeTruthy()
    expect(wrapper.find(getTestId(`${section}-card`)).classes('border-error-left')).toBeFalsy()

    expect(wrapper.find(getTestId(`${section}-text-field`)).exists()).toBe(true)

    // trigger error in Attn Ref Num field (40+ chars)
    await wrapper.find(getTestId(`${section}-text-field`)).setValue('5'.repeat(45))
    expect(store.getMhrTransferAttentionReference).toBe('5'.repeat(45))
    await nextTick()
    await nextTick()

    expect(wrapper.find(getTestId(`${section}-card`)).classes('border-error-left')).toBeTruthy()
    expect(
      wrapper
        .find(getTestId(`${section}-card`))
        .find('.v-input')
        .classes('error--text')
    ).toBeTruthy()
    expect(
      wrapper
        .find(getTestId(`${section}-card`))
        .find('.v-text-field__details .v-messages__message')
        .exists()
    ).toBeTruthy()

    // reset Attention Reference Number validation (to not affect other tests)
    wrapper.vm.isRefNumValid = true
  })

  it('should render Authorization component on review', async () => {
    setupCurrentHomeOwners()
    wrapper.vm.dataLoaded = true
    wrapper.vm.showTransferType = true
    await nextTick()

    expect(wrapper.vm.getMhrTransferCurrentHomeOwnerGroups.length).toBe(1)
    expect(wrapper.vm.getMhrTransferHomeOwners.length).toBe(1)
    expect(wrapper.exists()).toBe(true)

    // Set Wrapper Validations
    wrapper.vm.setValidation('isValidTransferType', true)
    wrapper.vm.setValidation('isValidTransferOwners', true)
    wrapper.vm.setValidation('isTransferDetailsValid', true)

    // Enter review mode
    await triggerUnsavedChange()
    await enterTransferDetailsFields(wrapper.findComponent(TransferDetails))

    await wrapper.find('#btn-stacked-submit').trigger('click')
    await nextTick()

    // Check if Authorization renders in review mode
    expect(wrapper.findComponent(MhrInformation).findComponent(CertifyInformation).exists()).toBe(true)

    // Check for component's attributes
    const authorizationComponent = wrapper.findComponent(CertifyInformation)
    expect(authorizationComponent.find('#certify-summary').exists()).toBeTruthy()
    expect(authorizationComponent.find('#certify-information').exists()).toBeTruthy()
    expect(authorizationComponent.find('#checkbox-certified').exists()).toBeTruthy()
    expect(authorizationComponent.text()).toContain(mockedRegisteringParty1.address.city)
    expect(authorizationComponent.text()).toContain(mockedRegisteringParty1.address.street)
    expect(authorizationComponent.text()).toContain(mockedRegisteringParty1.address.postalCode)
  })

  it('should render Submitting Party component on the Review screen', async () => {
    setupCurrentHomeOwners()
    wrapper.vm.dataLoaded = true
    wrapper.vm.showTransferType = true
    await nextTick()

    expect(wrapper.find('#account-info').exists()).toBeFalsy()

    // set Account Info in local state
    wrapper.vm.accountInfo = mockedAccountInfo

    // Set Wrapper Validations
    wrapper.vm.setValidation('isValidTransferType', true)
    wrapper.vm.setValidation('isValidTransferOwners', true)
    wrapper.vm.setValidation('isTransferDetailsValid', true)

    await triggerUnsavedChange()
    await enterTransferDetailsFields(wrapper.findComponent(TransferDetails))

    await wrapper.find('#btn-stacked-submit').trigger('click')
    await nextTick()

    // Submitting Party for Staff should not exist
    expect(wrapper.find('#staff-transfer-submitting-party').exists()).toBeFalsy()

    expect(wrapper.find('#account-info').exists()).toBeTruthy()
    expect(wrapper.find(getTestId('submitting-party-tooltip')).exists()).toBeTruthy()

    const accountInfoTable = wrapper.findComponent(AccountInfo).find(getTestId('account-info-table'))
    expect(accountInfoTable.exists()).toBeTruthy()

    const accountInfoText = accountInfoTable.text()
    expect(accountInfoText).toContain(mockedAccountInfo.name)
    expect(accountInfoText).toContain(toDisplayPhone(mockedAccountInfo.accountAdmin.phone))
    expect(accountInfoText).toContain(mockedAccountInfo.accountAdmin.email)
    expect(accountInfoText).toContain('Ext ' + mockedAccountInfo.accountAdmin.phoneExtension)
    expect(accountInfoText).toContain(mockedAccountInfo.mailingAddress.city)
    expect(accountInfoText).toContain(mockedAccountInfo.mailingAddress.street)
    expect(accountInfoText).toContain(mockedAccountInfo.mailingAddress.postalCode)
  })

  it('should render Party Search and Submitting Party component on the Review screen (Staff)', async () => {
    await store.setAuthRoles([AuthRoles.PPR_STAFF])
    setupCurrentHomeOwners()
    wrapper.vm.dataLoaded = true
    wrapper.vm.showTransferType = true
    await nextTick()

    // Set Wrapper Validations
    wrapper.vm.setValidation('isValidTransferType', true)
    wrapper.vm.setValidation('isValidTransferOwners', true)
    wrapper.vm.setValidation('isTransferDetailsValid', true)

    await triggerUnsavedChange()
    await enterTransferDetailsFields(wrapper.findComponent(TransferDetails))

    await wrapper.find('#btn-stacked-submit').trigger('click')
    await nextTick()

    // Submitting Party for non-Staff should not exist
    expect(wrapper.find('#transfer-submitting-party').exists()).toBeFalsy()

    const staffSubmittingParty = wrapper.find('#staff-transfer-submitting-party')
    expect(staffSubmittingParty.exists()).toBeTruthy()
    expect(staffSubmittingParty.find('#ppr-party-code').exists()).toBe(true)
    expect(staffSubmittingParty.findComponent(ContactInformation).exists()).toBe(true)

    // click submit to trigger errors
    wrapper.find('#btn-stacked-submit').trigger('click')
    await nextTick()

    // should show 4 errors for Submitting Party, Confirm, Auth and Pay components
    expect(wrapper.findAll('.border-error-left').length).toBe(4)
    // reset staff role
    await store.setAuthRoles([AuthRoles.MHR])
  })

  it('should render TransferDetailsReview on Review screen', async () => {
    setupCurrentHomeOwners()
    wrapper.vm.dataLoaded = true
    await nextTick()

    // Should hide transfer details if no changes made
    expect(wrapper.findComponent(TransferDetails).exists()).toBeFalsy()

    // Add some owners so Transfer Details will display
    const owners = [mockedAddedPerson, mockedRemovedPerson] as MhrRegistrationHomeOwnerIF[]
    const homeOwnerGroup = [
      mockMhrTransferCurrentHomeOwner,
      { groupId: 1, owners: owners }
    ] as MhrRegistrationHomeOwnerGroupIF[]

    await store.setMhrTransferHomeOwnerGroups(homeOwnerGroup)

    // Should show transfer details once changes made
    expect(wrapper.findComponent(TransferDetails).exists()).toBeTruthy()

    // set some test values for transfer details fields
    const mhrTransferDetailsComponent = wrapper.findComponent(TransferDetails)
    mhrTransferDetailsComponent.find(getTestId('lease-own-checkbox')).setChecked()

    await wrapper.find('#home-owners-change-btn').trigger('click')
    await nextTick()

    const mhrTransferTypeComponent = wrapper.findComponent(TransferType)
    expect(mhrTransferTypeComponent.exists()).toBeTruthy()
    await enterTransferTypeFields(mhrTransferTypeComponent)
    await nextTick()

    expect(wrapper.findComponent(TransferDetailsReview).exists()).toBeFalsy()

    // Set Wrapper Validations
    wrapper.vm.setValidation('isValidTransferType', true)
    wrapper.vm.setValidation('isValidTransferOwners', true)
    wrapper.vm.setValidation('isTransferDetailsValid', true)

    // go to Review screen
    await triggerUnsavedChange()
    await enterTransferDetailsFields(wrapper.findComponent(TransferDetails))

    await wrapper.find('#btn-stacked-submit').trigger('click')
    await nextTick()

    // renders TransferDetailsReviewc
    expect(wrapper.findComponent(TransferDetailsReview).exists()).toBeTruthy()
    const mhrTransferDetailsReviewComponent = wrapper.findComponent(TransferDetailsReview)

    // displaying correct declared value
    expect(mhrTransferDetailsReviewComponent.find('#declared-value-display').exists()).toBeFalsy()

    // autofilled consideration and displaying correct consideration value
    expect(mhrTransferDetailsReviewComponent.find('#consideration-display').exists()).toBeTruthy()
    const currentConsideration = mhrTransferDetailsReviewComponent.find('#consideration-display')
    expect(currentConsideration.text()).toBe(TRANSFER_CONSIDERATION)

    // displaying lease land row when checked
    expect(mhrTransferDetailsReviewComponent.find('#lease-land-display').exists()).toBeTruthy()
  })

  it('should render yellow message bar on the Review screen', async () => {
    setupCurrentHomeOwners()
    wrapper.vm.dataLoaded = true
    wrapper.vm.showTransferType = true
    await nextTick()

    // doesn't exist on manufactured home page
    expect(wrapper.find('#yellow-message-bar').exists()).toBeFalsy()

    // Set Wrapper Validations
    wrapper.vm.setValidation('isValidTransferType', true)
    wrapper.vm.setValidation('isValidTransferOwners', true)
    wrapper.vm.setValidation('isTransferDetailsValid', true)

    // trigger review
    await triggerUnsavedChange()
    await enterTransferDetailsFields(wrapper.findComponent(TransferDetails))

    await wrapper.find('#btn-stacked-submit').trigger('click')
    await nextTick()

    // exists on review page
    expect(wrapper.findComponent(CautionBox).exists()).toBe(true)
    expect(wrapper.findComponent(CautionBox).find('.v-icon').exists()).toBeFalsy()

    // trigger back button
    wrapper.find('#btn-stacked-back').trigger('click')
    await nextTick()

    // message is removed once out of review screen
    expect(wrapper.find('#yellow-message-bar').exists()).toBeFalsy()
  })

  it('should render Confirm Completion component on the Review screen', async () => {
    setupCurrentHomeOwners()
    wrapper.vm.dataLoaded = true
    wrapper.vm.showTransferType = true
    await nextTick()

    expect(wrapper.find('#transfer-confirm-section').exists()).toBeFalsy()

    // Set Wrapper Validations
    wrapper.vm.setValidation('isValidTransferType', true)
    wrapper.vm.setValidation('isValidTransferOwners', true)
    wrapper.vm.setValidation('isTransferDetailsValid', true)

    await triggerUnsavedChange()
    await enterTransferDetailsFields(wrapper.findComponent(TransferDetails))

    await wrapper.find('#btn-stacked-submit').trigger('click')
    await nextTick()

    expect(wrapper.find('#transfer-confirm-section').exists()).toBeTruthy()

    const confirmCompletionCard = wrapper.find(getTestId('confirm-completion-card'))
    expect(confirmCompletionCard.exists()).toBeTruthy()
    expect(confirmCompletionCard.classes('border-error-left')).toBeFalsy()
    expect(confirmCompletionCard.find(getTestId('confirm-completion-checkbox')).exists()).toBeTruthy()
    expect(confirmCompletionCard.find('.confirm-checkbox').text()).toContain(LEGAL_NAME)
  })

  it('SALE OR GIFT Flow: display correct Confirm Completion sections', async () => {
    setupCurrentHomeOwners()
    wrapper.vm.dataLoaded = true
    wrapper.vm.showTransferType = true
    await nextTick()

    expect(wrapper.find('#transfer-confirm-section').exists()).toBeFalsy()

    // Set Wrapper Validations
    wrapper.vm.setValidation('isValidTransferType', true)
    wrapper.vm.setValidation('isValidTransferOwners', true)
    wrapper.vm.setValidation('isTransferDetailsValid', true)

    await triggerUnsavedChange()
    await enterTransferDetailsFields(wrapper.findComponent(TransferDetails))
    await store.setMhrTransferType({
      transferType: ApiTransferTypes.SALE_OR_GIFT,
      textLabel: UITransferTypes.SALE_OR_GIFT
    } as TransferTypeSelectIF)
    await wrapper.find('#btn-stacked-submit').trigger('click')
    await nextTick()

    expect(wrapper.find('#transfer-confirm-section').exists()).toBeTruthy()

    const confirmCompletionCard = wrapper.find(getTestId('confirm-completion-card'))
    expect(confirmCompletionCard.exists()).toBeTruthy()
    expect(confirmCompletionCard.classes('border-error-left')).toBeFalsy()
    expect(confirmCompletionCard.find(getTestId('confirm-completion-checkbox')).exists()).toBeTruthy()
    expect(confirmCompletionCard.find('.confirm-checkbox').text()).toContain(LEGAL_NAME)

    // Contains Sale or Gift Flow Sections
    expect(confirmCompletionCard.find(getTestId('bill-of-sale-sale-or-gift')).exists()).toBeTruthy()
    expect(confirmCompletionCard.find(getTestId('change-ownership-section')).exists()).toBeFalsy()
    expect(confirmCompletionCard.find(getTestId('confirm-search-sale-or-gift')).exists()).toBeTruthy()

    // Doesn't contain any other flow sections
    expect(confirmCompletionCard.find(getTestId('death-certificate-section')).exists()).toBeFalsy()

    // Verify different section 2 is displayed for staff
    await store.setAuthRoles([AuthRoles.STAFF])

    expect(confirmCompletionCard.find(getTestId('bill-of-sale-sale-or-gift')).exists()).toBeTruthy()
    expect(confirmCompletionCard.find(getTestId('change-ownership-section')).exists()).toBeTruthy()
    expect(confirmCompletionCard.find(getTestId('certified-copy-section')).exists()).toBeTruthy()
    expect(confirmCompletionCard.find(getTestId('confirm-search-sale-or-gift')).exists()).toBeTruthy()
    expect(confirmCompletionCard.find(getTestId('ppr-lien-sale-or-gift')).exists()).toBeTruthy()


    await store.setAuthRoles([AuthRoles.MHR])
  })

  it('SALE OR GIFT Flow: should correctly validate all fields', async () => {
    const homeOwnerGroups: MhrRegistrationHomeOwnerGroupIF[] = [
      {
        groupId: 1,
        interest: 'Undivided',
        interestNumerator: 1,
        interestDenominator: 2,
        owners: [mockedExecutor, mockedAdministrator],
        type: ''
      },
      {
        groupId: 2,
        interest: 'Undivided',
        interestNumerator: 1,
        interestDenominator: 2,
        owners: [mockedPerson2, mockedOrganization],
        type: ''
      }
    ]

    await store.setMhrTransferCurrentHomeOwnerGroups(homeOwnerGroups)
    await store.setMhrTransferHomeOwnerGroups(homeOwnerGroups)
    await store.setMhrTransferType({ transferType: ApiTransferTypes.SALE_OR_GIFT } as TransferTypeSelectIF)
    await store.setMhrTransferDocumentId('12345678')

    wrapper.vm.dataLoaded = true
    wrapper.vm.showTransferType = true
    await nextTick()

    // should be no errors on the page
    expect(wrapper.findAll('.error-text')).toHaveLength(0)
    expect(wrapper.findAll('.border-left-error')).toHaveLength(0)

    expect(wrapper.findComponent(TransferDetails).exists()).toBeFalsy()

    await enterTransferTypeFields(wrapper.findComponent(TransferType))

    await wrapper.find(HomeOwners).findAll(getTestId('table-delete-btn')).at(0).trigger('click')
    await nextTick()

    // should show group error because we removed one Executor
    expect(wrapper.findAll('.error-text')).toHaveLength(1)
    expect(wrapper.find(getTestId('invalid-group-msg')).exists()).toBeTruthy()

    await enterTransferDetailsFields(wrapper.findComponent(TransferDetails))
    await wrapper.find('#btn-stacked-submit').trigger('click')
    await nextTick()

    // make sure we are still on Mhr Information page due to the error in the table
    expect(wrapper.find('#mhr-information-header').text()).toContain('Manufactured Home Information')
    expect(wrapper.find(HomeOwners).props().isReadonlyTable).toBe(false)
    // should be three border errors, for: error message itself, owner 1 and owner 2
    expect(wrapper.findAll('.border-error-left').length).toBe(3)
  })

  it('SURVIVING JOINT TENANT Flow: display correct Confirm Completion sections', async () => {
    setupCurrentHomeOwners()
    wrapper.vm.dataLoaded = true
    wrapper.vm.showTransferType = true
    await nextTick()
    await store.setAuthRoles([AuthRoles.STAFF])

    expect(wrapper.find('#transfer-confirm-section').exists()).toBeFalsy()

    // Set Wrapper Validations
    wrapper.vm.setValidation('isDocumentIdValid', true)
    wrapper.vm.setValidation('isValidTransferType', true)
    wrapper.vm.setValidation('isValidTransferOwners', true)
    wrapper.vm.setValidation('isTransferDetailsValid', true)

    await triggerUnsavedChange()
    await enterTransferDetailsFields(wrapper.findComponent(TransferDetails))
    await store.setMhrTransferType({
      transferType: ApiTransferTypes.SURVIVING_JOINT_TENANT,
      textLabel: UITransferTypes.SURVIVING_JOINT_TENANT
    } as TransferTypeSelectIF)
    await wrapper.find('#btn-stacked-submit').trigger('click')
    await nextTick()

    expect(wrapper.find('#transfer-confirm-section').exists()).toBeTruthy()

    const confirmCompletionCard = wrapper.find(getTestId('confirm-completion-card'))
    expect(confirmCompletionCard.exists()).toBeTruthy()
    expect(confirmCompletionCard.classes('border-error-left')).toBeFalsy()
    expect(confirmCompletionCard.find(getTestId('confirm-completion-checkbox')).exists()).toBeTruthy()
    expect(confirmCompletionCard.find('.confirm-checkbox').text()).toContain(LEGAL_NAME)

    // Contains Surviving Joint Tenant Flow Sections
    expect(confirmCompletionCard.find(getTestId('death-certificate-section')).exists()).toBeTruthy()
    expect(confirmCompletionCard.find(getTestId('change-ownership-section')).exists()).toBeTruthy()
    expect(confirmCompletionCard.find(getTestId('ppr-lien-sale-or-gift')).exists()).toBeTruthy()

    // Doesn't contain any other flow sections
    expect(confirmCompletionCard.find(getTestId('confirm-search-section')).exists()).toBeFalsy()
    await store.setAuthRoles([AuthRoles.MHR])
  })

  it('TRANS WILL Flow: display correct Confirm Completion sections', async () => {
    setupCurrentHomeOwners()
    wrapper.vm.dataLoaded = true
    wrapper.vm.showTransferType = true
    await nextTick()
    await store.setAuthRoles([AuthRoles.STAFF])

    expect(wrapper.find('#transfer-confirm-section').exists()).toBeFalsy()

    // Set Wrapper Validations
    wrapper.vm.setValidation('isDocumentIdValid', true)
    wrapper.vm.setValidation('isValidTransferType', true)
    wrapper.vm.setValidation('isValidTransferOwners', true)
    wrapper.vm.setValidation('isTransferDetailsValid', true)

    await triggerUnsavedChange()
    await enterTransferDetailsFields(wrapper.findComponent(TransferDetails))
    await store.setMhrTransferType({
      transferType: ApiTransferTypes.TO_EXECUTOR_PROBATE_WILL,
      textLabel: UITransferTypes.TO_EXECUTOR_PROBATE_WILL
    } as TransferTypeSelectIF)
    await wrapper.find('#btn-stacked-submit').trigger('click')
    await nextTick()

    expect(wrapper.find('#transfer-confirm-section').exists()).toBeTruthy()

    const confirmCompletionCard = wrapper.find(getTestId('confirm-completion-card'))
    expect(confirmCompletionCard.exists()).toBeTruthy()
    expect(confirmCompletionCard.classes('border-error-left')).toBeFalsy()
    expect(confirmCompletionCard.find(getTestId('confirm-completion-checkbox')).exists()).toBeTruthy()
    expect(confirmCompletionCard.find('.confirm-checkbox').text()).toContain(LEGAL_NAME)

    // Contains Executor Will Flow Sections
    expect(confirmCompletionCard.find(getTestId('death-certificate-section')).exists()).toBeTruthy()
    expect(confirmCompletionCard.find(getTestId('change-ownership-section')).exists()).toBeTruthy()
    expect(confirmCompletionCard.find(getTestId('probate-will-section')).exists()).toBeTruthy()
    expect(confirmCompletionCard.find(getTestId('ppr-lien-section')).exists()).toBeTruthy()

    // Doesn't contain any other flow sections
    expect(confirmCompletionCard.find(getTestId('confirm-search-section')).exists()).toBeFalsy()
    await store.setAuthRoles([AuthRoles.MHR])
  })

  it('should render read only home owners on the Review screen', async () => {
    setupCurrentHomeOwners()
    wrapper.vm.dataLoaded = true
    wrapper.vm.showTransferType = true
    await nextTick()

    // TODO: check that removed owners are not displayed in review
    const owners = [mockedRemovedPerson] as MhrRegistrationHomeOwnerIF[] // same IF for Transfer and Registration
    const homeOwnerGroup = [
      mockMhrTransferCurrentHomeOwner,
      { groupId: 1, owners: owners }
    ] as MhrRegistrationHomeOwnerGroupIF[]

    const homeOwnersComponent: Wrapper<any> = wrapper.findComponent(HomeOwners)
    await store.setMhrTransferHomeOwnerGroups(homeOwnerGroup)
    expect(homeOwnersComponent.findComponent(HomeOwnersTable).exists()).toBeTruthy()

    // check owners are in table
    expect(homeOwnersComponent.vm.getHomeOwners.length).toBe(2)

    // review table doesn't exist yet
    expect(wrapper.find('#owners-review').exists()).toBeFalsy()

    // Set Wrapper Validations
    wrapper.vm.setValidation('isDocumentIdValid', true)
    wrapper.vm.setValidation('isValidTransferType', true)
    wrapper.vm.setValidation('isValidTransferOwners', true)
    wrapper.vm.setValidation('isTransferDetailsValid', true)

    await triggerUnsavedChange()
    await enterTransferDetailsFields(wrapper.findComponent(TransferDetails))

    await wrapper.find('#btn-stacked-submit').trigger('click')
    await nextTick()
    await nextTick()

    // review table renders
    const homeOwnerReadOnly: Wrapper<any> = wrapper.find('#owners-review').findComponent(HomeOwners)
    expect(homeOwnerReadOnly.exists()).toBeTruthy()

    // values remain in table
    expect(homeOwnerReadOnly.props().isReadonlyTable).toBe(true)
    expect(homeOwnersComponent.vm.getHomeOwners.length).toBe(2)
  })

  it('should validate and show components errors on Review screen', async () => {
    setupCurrentHomeOwners()
    wrapper.vm.dataLoaded = true
    wrapper.vm.showTransferType = true
    await nextTick()
    await triggerUnsavedChange()

    const feeSummaryContainer = wrapper.find(getTestId('fee-summary'))
    expect(feeSummaryContainer.find('.err-msg').exists()).toBeFalsy()

    // Set Wrapper Validations
    wrapper.vm.setValidation('isDocumentIdValid', true)
    wrapper.vm.setValidation('isValidTransferType', true)
    wrapper.vm.setValidation('isValidTransferOwners', true)
    wrapper.vm.setValidation('isTransferDetailsValid', true)

    await enterTransferDetailsFields(wrapper.findComponent(TransferDetails))

    await wrapper.find('#btn-stacked-submit').trigger('click')
    await nextTick()

    expect(wrapper.find('#mhr-information-header').text()).toContain('Review and Confirm')
    expect(feeSummaryContainer.find('.err-msg').exists()).toBeFalsy()
    expect(wrapper.findAll('.border-error-left').length).toBe(0)
    await wrapper.find(getTestId('transfer-ref-num-section-text-field')).setValue('5'.repeat(45))

    wrapper.find('#btn-stacked-submit').trigger('click')
    await nextTick()

    // should show 3 errors for Ref Num, Confirm and Auth components
    expect(feeSummaryContainer.find('.err-msg').exists()).toBeTruthy()
    expect(wrapper.findAll('.border-error-left').length).toBe(3)
  })

  it('should clear Transfer Details fields on Undo click', async () => {
    setupCurrentHomeOwners()
    wrapper.vm.dataLoaded = true
    await nextTick()

    expect(wrapper.findComponent(TransferDetails).exists()).toBeFalsy()

    await triggerUnsavedChange()

    const transferDetailsWrapper: Wrapper<any> = wrapper.findComponent(TransferDetails)
    expect(transferDetailsWrapper.exists()).toBeTruthy()
    await enterTransferDetailsFields(wrapper.findComponent(TransferDetails))

    await wrapper.find('#home-owners-change-btn').trigger('click')
    await nextTick()

    const mhrTransferTypeComponent: Wrapper<any> = wrapper.findComponent(TransferType)
    expect(mhrTransferTypeComponent.exists()).toBeTruthy()
    await enterTransferTypeFields(mhrTransferTypeComponent)
    await nextTick()

    transferDetailsWrapper.find(getTestId('consideration')).trigger('mousedown')
    expect(transferDetailsWrapper.vm.consideration).toBe(TRANSFER_CONSIDERATION)
    expect(transferDetailsWrapper.vm.transferDate).toContain(TRANSFER_DATE)

    // simulate 'Undo'
    await store.setUnsavedChanges(false)
    await transferDetailsWrapper.vm.clearTransferDetailsData()
    await nextTick()

    expect(transferDetailsWrapper.exists()).toBeFalsy()
    // Open up Transfer Details again and check that fields are cleared
    await triggerUnsavedChange()

    expect(store.getMhrTransferConsideration).toBe('')
    expect(store.getMhrTransferDate).toBe(null)
  })

  it('should hide the Transfer Change button when the feature flag is false', async () => {
    defaultFlagSet['mhr-transfer-enabled'] = false
    await nextTick()
    wrapper = createComponent()

    setupCurrentHomeOwners()
    wrapper.vm.dataLoaded = true
    await nextTick()

    expect(wrapper.find('#home-owners-change-btn').exists()).toBe(false)
  })

  it('should display Alert Msg for Qualified Supplier', async () => {
    // setup Qualified Supplier as Manufacturer
    await store.setAuthRoles([AuthRoles.MHR_TRANSFER_SALE])
    await store.setUserProductSubscriptionsCodes([ProductCode.MANUFACTURER])

    // Add Unit Note that triggers locked state
    await store.setMhrUnitNotes(mockedUnitNotes5)

    await nextTick()
    wrapper = await createComponent()
    await store.setMhrInformation(mockedLockedMhRegistration)
    await store.setMhrFrozenDocumentType(UnitNoteDocTypes.NOTICE_OF_TAX_SALE)

    await nextTick()
    expect(wrapper.findComponent(MhrInformation).exists()).toBe(true)
    expect(wrapper.findComponent(LienAlert).exists()).toBe(false)

    const CautionBoxComponent = wrapper.findComponent(CautionBox)
    expect(CautionBoxComponent.exists()).toBe(true)
    expect(CautionBoxComponent.classes('alert-box')).toBeTruthy()
    expect(CautionBoxComponent.find('.v-icon').classes('alert-icon')).toBeTruthy()
    expect(CautionBoxComponent.text()).toContain(UnitNotesInfo[UnitNoteDocTypes.NOTICE_OF_TAX_SALE].header)
  })

  it('should have read only view for exempt MHR (Residential Exemption filed)', async () => {
    wrapper = createComponent()

    // add unit notes with Residential Exemption
    await store.setMhrUnitNotes([mockedResidentialExemptionOrder, ...mockedUnitNotes3])
    await store.setAuthRoles([AuthRoles.PPR_STAFF])
    wrapper.vm.dataLoaded = true
    await nextTick()

    expect(wrapper.find(getTestId('correct-into-desc')).exists()).toBeFalsy()
    expect(wrapper.find(getTestId('mhr-alert-msg')).exists()).toBeTruthy()
    // message for Staff should contain unique text
    expect(wrapper.find(getTestId('mhr-alert-msg')).text()).toContain('See Unit Notes for further information')
    expect(wrapper.find(HomeOwners).find('#home-owners-change-btn').exists()).toBeFalsy()

    // setup Qualified Supplier as Manufacturer
    await store.setAuthRoles([AuthRoles.MHR_TRANSFER_SALE])
    await store.setUserProductSubscriptionsCodes([ProductCode.MANUFACTURER])
    await nextTick()

    // message for QS should contain unique text
    expect(wrapper.find(getTestId('mhr-alert-msg')).text()).toContain('contact BC Registries staff')
  })
})
