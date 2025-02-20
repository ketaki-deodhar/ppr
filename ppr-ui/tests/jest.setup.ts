// jest.setup.ts
// Global setup running before all tests
// Extend Jest with Accessibility unit test tool
import { SessionStorageKeys } from 'sbc-common-components/src/util/constants'
import { toHaveNoViolations } from 'jest-axe'

// Extend Jest Expect with AA test
expect.extend(toHaveNoViolations)

// Setup Mock Session Key
sessionStorage.setItem(SessionStorageKeys.KeyCloakToken, 'eyJhbGciOiJSUzI1NiIsInR5cCIgOiAiSldUIiwia2lkIiA6ICJUbWdtZUk0MnVsdUZ0N3FQbmUtcTEzdDUwa0JDbjF3bHF6dHN0UGdUM1dFIn0.eyJleHAiOjE2NDQ1MzYxMzEsImlhdCI6MTY0NDUxODEzMSwiYXV0aF90aW1lIjoxNjQ0NTE2NTM0LCJqdGkiOiIxZjc5OTkyOC05ODQwLTRlNzktYTEwZS1jMmI5ZTJjZTE3ZWQiLCJpc3MiOiJodHRwczovL2Rldi5vaWRjLmdvdi5iYy5jYS9hdXRoL3JlYWxtcy9mY2Ywa3BxciIsImF1ZCI6WyJwcHItc2VydmljZXMiLCJhY2NvdW50LXNlcnZpY2VzIiwiYWNjb3VudCJdLCJzdWIiOiI3NWMzMzE5Ni0zOTk3LTRkOTctODBlNi01ZGQyYWE1YmU5N2IiLCJ0eXAiOiJCZWFyZXIiLCJhenAiOiJwcHItd2ViIiwibm9uY2UiOiIwNDRjYzAyOC01NTZmLTRmNDgtYWM0NS1jNzU5OGEwMWQ0YTgiLCJzZXNzaW9uX3N0YXRlIjoiOGFiNjZmMDktZWQyYi00ZGQ4LWE1YmYtM2NjYWI2MThlMzVhIiwiYWNyIjoiMCIsImFsbG93ZWQtb3JpZ2lucyI6WyIqIl0sInJlYWxtX2FjY2VzcyI6eyJyb2xlcyI6WyJwdWJsaWNfdXNlciIsInBwciIsImVkaXQiLCJhY2NvdW50X2hvbGRlciIsIm9mZmxpbmVfYWNjZXNzIiwidW1hX2F1dGhvcml6YXRpb24iXX0sInJlc291cmNlX2FjY2VzcyI6eyJhY2NvdW50Ijp7InJvbGVzIjpbIm1hbmFnZS1hY2NvdW50IiwibWFuYWdlLWFjY291bnQtbGlua3MiLCJ2aWV3LXByb2ZpbGUiXX19LCJzY29wZSI6Im9wZW5pZCIsImZpcnN0bmFtZSI6IkJDUkVHMiBTdmV0bGFuYSIsInJvbGVzIjpbInB1YmxpY191c2VyIiwicHByIiwiZWRpdCIsImFjY291bnRfaG9sZGVyIiwib2ZmbGluZV9hY2Nlc3MiLCJ1bWFfYXV0aG9yaXphdGlvbiJdLCJuYW1lIjoiQkNSRUcyIFN2ZXRsYW5hIEZPVVJURUVOIiwiaWRwX3VzZXJpZCI6IkhERjNEWVFFUUhQVU1VT01QUUMyQkFGSVJETFZPV0s2IiwicHJlZmVycmVkX3VzZXJuYW1lIjoiYmNzYy9oZGYzZHlxZXFocHVtdW9tcHFjMmJhZmlyZGx2b3drNiIsImxvZ2luU291cmNlIjoiQkNTQyIsImxhc3RuYW1lIjoiRk9VUlRFRU4iLCJ1c2VybmFtZSI6ImJjc2MvaGRmM2R5cWVxaHB1bXVvbXBxYzJiYWZpcmRsdm93azYifQ.UUamIDN1LWms2oK5YG9yEmfen6ISFoY9AGw7ZJrsmDiElt0XwI_lj6DPYdMieXgXQ4Ji7jRVSMNhX4LfxpC1JipepUbI3kBLf0lelTudhZyD9MOg-VYaLAAEwAY57Z8h7EOCQp0PLS8NAMwNs90t4sJ449uZ3HprEMfMvkaZ0X3Cv495U0m5Qr-GDT7PHeLqkh3297gvxx3PdIGZIWcIwz-lFo8jNYxpEtY1LivZXnCsfrLDEW-vVK5kmnB1boIJksiUq8ATjF6F26B7ytBhE89SvolmA5nMkLiB-yusbSMY0ccxRWpPmX4MJ2yKuM6Sr6L6Dxrw_FWBHU1ThnnxUw') // eslint-disable-line max-len

// Vue2 mock pdf embed
jest.mock('vue-pdf-embed/dist/vue2-pdf-embed', () => () => '<mock-vue-pdf-embed/>')

// Vue3 mock pdf embed: For post upgrade
// jest.mock('vue-pdf-embed', () => () => '<mock-vue-pdf-embed/>')
