import { BreadcrumbIF } from '@/interfaces'
import { RouteNames } from '@/enums'

// breadcrumb data in tombstone
export const tombstoneBreadcrumbDashboard: Array<BreadcrumbIF> = [
  {
    disabled: false,
    href: sessionStorage.getItem('REGISTRY_URL'),
    text: 'BC Registries Dashboard'
  },
  {
    disabled: true,
    href: '',
    text: 'My Personal Property Registry'
  }
]
export const tombstoneBreadcrumbDischarge: Array<BreadcrumbIF> = [
  {
    disabled: false,
    href: sessionStorage.getItem('REGISTRY_URL'),
    text: 'BC Registries Dashboard'
  },
  {
    disabled: false,
    href: sessionStorage.getItem('BASE_URL') + 'dashboard',
    to: { name: RouteNames.DASHBOARD },
    text: 'My Personal Property Registry'
  },
  {
    disabled: true,
    href: '',
    text: 'Total Discharge'
  }
]
export const tombstoneBreadcrumbRenewal: Array<BreadcrumbIF> = [
  {
    disabled: false,
    href: sessionStorage.getItem('REGISTRY_URL'),
    text: 'BC Registries Dashboard'
  },
  {
    disabled: false,
    href: sessionStorage.getItem('BASE_URL') + 'dashboard',
    to: { name: RouteNames.DASHBOARD },
    text: 'My Personal Property Registry'
  },
  {
    disabled: true,
    href: '',
    text: 'Renewal'
  }
]
export const tombstoneBreadcrumbAmendment: Array<BreadcrumbIF> = [
  {
    disabled: false,
    href: sessionStorage.getItem('REGISTRY_URL'),
    text: 'BC Registries Dashboard'
  },
  {
    disabled: false,
    href: sessionStorage.getItem('BASE_URL') + 'dashboard',
    to: { name: RouteNames.DASHBOARD },
    text: 'My Personal Property Registry'
  },
  {
    disabled: true,
    href: '',
    text: 'Amendment'
  }
]
export const tombstoneBreadcrumbRegistration: Array<BreadcrumbIF> = [
  {
    disabled: false,
    href: sessionStorage.getItem('REGISTRY_URL'),
    text: 'BC Registries Dashboard'
  },
  {
    disabled: false,
    href: sessionStorage.getItem('BASE_URL') + 'dashboard',
    to: { name: RouteNames.DASHBOARD },
    text: 'My Personal Property Registry'
  },
  {
    disabled: true,
    href: '',
    text: 'New Registration'
  }
]
export const tombstoneBreadcrumbSearch: Array<BreadcrumbIF> = [
  {
    disabled: false,
    href: sessionStorage.getItem('REGISTRY_URL'),
    text: 'BC Registries Dashboard'
  },
  {
    disabled: false,
    href: sessionStorage.getItem('BASE_URL') + 'dashboard',
    to: { name: RouteNames.DASHBOARD },
    text: 'My Personal Property Registry'
  },
  {
    disabled: true,
    href: '',
    text: 'Selection List'
  }
]
export const tombstoneBreadcrumbSearchConfirm: Array<BreadcrumbIF> = [
  {
    disabled: false,
    href: sessionStorage.getItem('REGISTRY_URL'),
    text: 'BC Registries Dashboard'
  },
  {
    disabled: false,
    href: sessionStorage.getItem('BASE_URL') + 'dashboard',
    to: { name: RouteNames.DASHBOARD },
    text: 'My Personal Property Registry'
  },
  {
    disabled: false,
    href: sessionStorage.getItem('BASE_URL') + 'mhr/search',
    to: { name: RouteNames.MHRSEARCH },
    text: 'Selection List'
  },
  {
    disabled: true,
    href: '',
    text: 'Selection Review'
  }
]
export const tombstoneBreadcrumbMhrInformation: Array<BreadcrumbIF> = [
  {
    disabled: false,
    href: sessionStorage.getItem('REGISTRY_URL'),
    text: 'BC Registries Dashboard'
  },
  {
    disabled: false,
    to: { name: RouteNames.DASHBOARD },
    text: 'My Asset Registries'
  },
  {
    disabled: true,
    href: '',
    text: 'MHR Number'
  }
]
export const tombstoneBreadcrumbMhrUnitNote: Array<BreadcrumbIF> = [
  {
    disabled: false,
    href: sessionStorage.getItem('REGISTRY_URL'),
    text: 'BC Registries Dashboard'
  },
  {
    disabled: false,
    to: { name: RouteNames.DASHBOARD },
    text: 'My Asset Registries'
  },
  {
    disabled: false,
    href: sessionStorage.getItem('BASE_URL') + RouteNames.MHR_INFORMATION,
    to: { name: RouteNames.MHR_INFORMATION },
    text: 'MHR Number'
  },
  {
    disabled: true,
    text: '' // dynamic based on the Unit Note type
  }
]
export const tombstoneBreadcrumbQsApplication: Array<BreadcrumbIF> = [
  {
    disabled: false,
    href: sessionStorage.getItem('REGISTRY_URL'),
    text: 'BC Registries Dashboard'
  },
  {
    disabled: false,
    to: { name: RouteNames.DASHBOARD },
    text: 'My Asset Registries'
  },
  {
    disabled: true,
    href: '',
    text: 'Qualified Supplier Application'
  }
]

export const tombstoneBreadcrumbExemption: Array<BreadcrumbIF> = [
  {
    disabled: false,
    href: sessionStorage.getItem('REGISTRY_URL'),
    text: 'BC Registries Dashboard'
  },
  {
    disabled: false,
    to: { name: RouteNames.DASHBOARD },
    text: 'My Asset Registries'
  },
  {
    disabled: true,
    href: '',
    text: 'Residential Exemption'
  }
]
