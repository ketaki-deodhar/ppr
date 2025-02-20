# Copyright © 2019 Province of British Columbia
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""This module holds common registration validation functions.

Refactored from registration_validator.
"""
import copy

from flask import current_app

from mhr_api.models import MhrRegistration, MhrDraft
from mhr_api.models import registration_utils as reg_utils, utils as model_utils
from mhr_api.models.type_tables import (
    MhrDocumentTypes,
    MhrLocationTypes,
    MhrNoteStatusTypes,
    MhrOwnerStatusTypes,
    MhrRegistrationStatusTypes,
    MhrRegistrationTypes,
    MhrStatusTypes,
    MhrTenancyTypes
)
from mhr_api.models.utils import is_legacy
from mhr_api.services import ltsa
from mhr_api.utils import valid_charset, validator_utils_legacy


HOME_DESCRIPTION_MIN_YEAR: int = 1900
DOC_ID_REQUIRED = 'Document ID is required for staff registrations. '
DOC_ID_EXISTS = 'Document ID must be unique: provided value already exists. '
DOC_ID_INVALID_CHECKSUM = 'Document ID is invalid: checksum failed. '
STATE_NOT_ALLOWED = 'The MH registration is not in a state where changes are allowed. '
STATE_FROZEN_AFFIDAVIT = 'A transfer to a benificiary is pending after an AFFIDAVIT transfer. '
STATE_FROZEN_NOTE = 'Registration not allowed: this manufactured home has an active TAXN, NCON, or REST unit note. '
STATE_FROZEN_PERMIT = 'Registration not allowed: this manufactured home has an active transport permit. '
DRAFT_NOT_ALLOWED = 'The draft for this registration is out of date: delete the draft and resubmit. '
CHARACTER_SET_UNSUPPORTED = 'The character set is not supported for {desc} value {value}. '
PPR_LIEN_EXISTS = 'This registration is not allowed to complete as an outstanding Personal Property Registry lien ' + \
    'exists on the manufactured home. '
LOCATION_PID_INVALID = 'Location PID verification failed: either the PID is invalid or the LTSA service is ' + \
                       'unavailable. '
SUBMITTING_REQUIRED = 'Submitting Party is required for MH registrations. '
DESCRIPTION_CSA_ENGINEER_REQUIRED = 'Either a CSA number or engineer information is required for this registration. '
DESCRIPTION_MAKE_MODEL_REQUIRED = 'Either description make or description model is required. '
DESCRIPTION_YEAR_INVALID = 'Description manufactured home year invalid: it must be between 1900 and 1 year after ' + \
    'the current year. '
DESCRIPTION_YEAR_REQUIRED = 'Description manufactured home year is required. '
EXEMPT_EXNR_INVALID = 'Registration not allowed: the home is exempt because of an existing non-residential exemption. '
EXEMPT_EXRS_INVALID = 'Residential exemption registration not allowed: the home is already exempt. '
DELETE_GROUP_ID_INVALID = 'The owner group with ID {group_id} is not active and cannot be changed. '
DELETE_GROUP_ID_NONEXISTENT = 'No owner group with ID {group_id} exists. '
DELETE_GROUP_TYPE_INVALID = 'The owner group tenancy type with ID {group_id} is invalid. '
GROUP_INTEREST_MISMATCH = 'The owner group interest numerator sum does not equal the interest common denominator. '
MHR_NUMBER_INVALID = 'MHR nubmer {mhr_num} either is greater than the existng maximum MHR number or already exists. '
LOCATION_INVALID_IDENTICAL = 'The new location cannot be identical to the existing location. '

LOCATION_DEALER_REQUIRED = 'Location dealer/manufacturer name is required for this registration. '
LOCATION_PARK_NAME_REQUIRED = 'Location park name is required for this registration. '
LOCATION_PARK_PAD_REQUIRED = 'Location park PAD is required for this registration. '
LOCATION_STRATA_REQUIRED = 'Location parcel ID or all of lot, plan, land district are required for this registration. '
LOCATION_OTHER_REQUIRED = 'Location parcel ID or all of lot, plan, land district or all of land district, district ' \
    'lot are required for this registration. '
BAND_NAME_REQUIRED = 'The location Indian Reserve band name is required for this registration. '
RESERVE_NUMBER_REQUIRED = 'The location Indian Reserve number is required for this registration. '
LOCATION_MANUFACTURER_ALLOWED = 'Park name, PAD, band name, reserve number, parcel ID, and LTSA details are ' \
    'not allowed with a MANUFACTURER location type. '
LOCATION_PARK_ALLOWED = 'Dealer/manufacturer name, band name, reserve number, parcel ID, and LTSA details are ' \
    'not allowed with a MH_PARK location type. '
LOCATION_RESERVE_ALLOWED = 'Dealer/manufacturer name, park name, and PAD are not allowed with a RESERVE location type. '
LOCATION_STRATA_ALLOWED = 'Dealer/manufacturer name, park name, PAD, band name, and reserve number are not allowed ' \
    'with a STRATA location type. '
LOCATION_OTHER_ALLOWED = 'Dealer/manufacturer name, park name, PAD, band name, and reserve number are not allowed ' \
    'with an OTHER location type. '
LOCATION_TAX_DATE_INVALID = 'Location tax certificate date is invalid. '
LOCATION_TAX_CERT_REQUIRED = 'Location tax certificate and tax certificate expiry date is required. '
STATUS_CONFIRMATION_REQUIRED = 'The land status confirmation is required for this registration. '

PPR_REG_TYPE_ALL = ' SA_TAX TA_TAX TM_TAX '
PPR_REG_TYPE_GOV = ' SA_GOV TA_GOV TM_GOV '
PPR_REG_TYPE_EXEMPTION = PPR_REG_TYPE_ALL + PPR_REG_TYPE_GOV + ' FR LT ML MN SG '
PPR_REG_TYPE_TRANSFER = PPR_REG_TYPE_ALL + PPR_REG_TYPE_GOV + ' FR LT ML MN SG '
PPR_REG_TYPE_PERMIT = PPR_REG_TYPE_ALL + ' LT ML MN '
PPR_RESTRICTED_REG_TYPES = {
    MhrRegistrationTypes.EXEMPTION_RES: PPR_REG_TYPE_EXEMPTION,
    MhrRegistrationTypes.TRANS: PPR_REG_TYPE_TRANSFER,
    MhrRegistrationTypes.PERMIT: PPR_REG_TYPE_PERMIT
}


def validate_doc_id(json_data, check_exists: bool = True):
    """Validate the registration document id."""
    doc_id = json_data.get('documentId')
    current_app.logger.debug(f'Validating doc_id={doc_id}.')
    error_msg = ''
    if not doc_id:
        error_msg += DOC_ID_REQUIRED
    elif not checksum_valid(doc_id):
        error_msg += DOC_ID_INVALID_CHECKSUM
    if check_exists and doc_id:
        exists_count = MhrRegistration.get_doc_id_count(doc_id)
        if exists_count > 0:
            error_msg += DOC_ID_EXISTS
    return error_msg


def checksum_valid(doc_id: str) -> bool:
    """Validate the document id with a checksum algorithm."""
    if not doc_id or len(doc_id) != 8:
        return False
    if doc_id.startswith('1') or doc_id.startswith('9') or doc_id.startswith('8') or doc_id.startswith('REG'):
        return True
    if not doc_id.isnumeric():
        return False
    dig1: int = int(doc_id[0:1])
    dig2: int = int(doc_id[1:2]) * 2
    dig3: int = int(doc_id[2:3])
    dig4: int = int(doc_id[3:4]) * 2
    dig5: int = int(doc_id[4:5])
    dig6: int = int(doc_id[5:6]) * 2
    dig7: int = int(doc_id[6:7])
    check_digit: int = int(doc_id[7:])
    dig_sum = dig1 + dig3 + dig5 + dig7
    if dig2 > 9:
        dig_sum += 1 + (dig2 % 10)
    else:
        dig_sum += dig2
    if dig4 > 9:
        dig_sum += 1 + (dig4 % 10)
    else:
        dig_sum += dig4
    if dig6 > 9:
        dig_sum += 1 + (dig6 % 10)
    else:
        dig_sum += dig6
    mod_sum = dig_sum % 10
    current_app.logger.debug(f'sum={dig_sum}, checkdigit= {check_digit}, mod_sum={mod_sum}')
    if mod_sum == 0:
        return mod_sum == check_digit
    return (10 - mod_sum) == check_digit


def validate_registration_state(registration: MhrRegistration, staff: bool, reg_type: str, doc_type: str = None):
    """Validate registration state: changes are only allowed on active homes."""
    error_msg = ''
    if not registration:
        return error_msg
    if is_legacy():
        return validator_utils_legacy.validate_registration_state(registration, staff, reg_type, doc_type)
    if doc_type and doc_type == MhrDocumentTypes.EXRE:
        return validate_registration_state_exre(registration)
    if reg_type and reg_type in (MhrRegistrationTypes.EXEMPTION_NON_RES, MhrRegistrationTypes.EXEMPTION_RES):
        return validate_registration_state_exemption(registration, reg_type, staff)
    if registration.status_type:
        if registration.status_type != MhrRegistrationStatusTypes.ACTIVE:
            if registration.status_type == MhrRegistrationStatusTypes.CANCELLED or \
                    doc_type is None or \
                    doc_type not in (MhrDocumentTypes.NPUB, MhrDocumentTypes.NCON,
                                     MhrDocumentTypes.NCAN, MhrDocumentTypes.NRED):
                error_msg += STATE_NOT_ALLOWED
        elif registration.change_registrations:
            last_reg: MhrRegistration = registration.change_registrations[-1]
            if not staff and last_reg.registration_type == MhrRegistrationTypes.TRANS_AFFIDAVIT:
                error_msg += STATE_NOT_ALLOWED
            elif staff and last_reg.registration_type == MhrRegistrationTypes.TRANS_AFFIDAVIT and \
                    (not reg_type or reg_type != MhrRegistrationTypes.TRANS):
                error_msg += STATE_NOT_ALLOWED
                error_msg += STATE_FROZEN_AFFIDAVIT
    return check_state_note(registration, staff, error_msg, reg_type)


def validate_registration_state_exre(registration: MhrRegistration):
    """Validate registration state for rescind exemption requests."""
    error_msg = ''
    if registration.status_type:
        if registration.status_type == MhrRegistrationStatusTypes.EXEMPT:
            return error_msg
        error_msg += STATE_NOT_ALLOWED
    return error_msg


def validate_registration_state_exemption(registration: MhrRegistration, reg_type: str, staff: bool):
    """Validate registration state for residential/non-residential exemption requests."""
    error_msg = ''
    if registration.status_type:
        if registration.status_type == MhrRegistrationStatusTypes.ACTIVE:
            return check_state_note(registration, staff, error_msg, reg_type)
        if registration.status_type == MhrRegistrationStatusTypes.CANCELLED:
            error_msg += STATE_NOT_ALLOWED
        elif reg_type == MhrRegistrationTypes.EXEMPTION_RES:
            error_msg += EXEMPT_EXRS_INVALID
        elif registration.change_registrations:
            for reg in registration.change_registrations:
                if reg.registration_type == MhrRegistrationTypes.EXEMPTION_NON_RES and \
                        reg.notes and reg.notes[0].status_type == MhrNoteStatusTypes.ACTIVE:
                    error_msg += EXEMPT_EXNR_INVALID
    return error_msg


def validate_draft_state(json_data):
    """Validate draft state: no change registration on the home after the draft was created."""
    error_msg = ''
    if not json_data.get('draftNumber'):
        return error_msg
    draft: MhrDraft = MhrDraft.find_by_draft_number(json_data.get('draftNumber'))
    if draft and draft.stale_count > 0:
        error_msg += DRAFT_NOT_ALLOWED
    return error_msg


def validate_submitting_party(json_data):
    """Verify submitting party names are valid."""
    error_msg = ''
    if not json_data.get('submittingParty'):
        return SUBMITTING_REQUIRED
    party = json_data.get('submittingParty')
    desc: str = 'submitting party'
    if party.get('businessName'):
        error_msg += validate_text(party.get('businessName'), desc + ' business name')
    elif party.get('personName'):
        error_msg += validate_individual_name(party.get('personName'), desc)
    return error_msg


def validate_party(party: dict, desc: str):
    """Verify party names are valid."""
    error_msg = ''
    if party.get('businessName'):
        error_msg += validate_text(party.get('businessName'), desc + ' business name')
    elif party.get('personName'):
        error_msg += validate_individual_name(party.get('personName'), desc + ' person name')
    return error_msg


def validate_individual_name(name_json, desc: str = ''):
    """Verify individual name is valid."""
    error_msg = validate_text(name_json.get('first'), desc + ' first')
    error_msg += validate_text(name_json.get('last'), desc + ' last')
    error_msg += validate_text(name_json.get('middle'), desc + ' middle')
    return error_msg


def validate_text(value: str, desc: str = ''):
    """Verify text characters are valid."""
    if value and not valid_charset(value):
        return CHARACTER_SET_UNSUPPORTED.format(desc=desc, value=value)
    return ''


def validate_ppr_lien(mhr_number: str, mhr_reg_type: str, staff: bool) -> str:
    """Validate that there are no PPR liens for a change registration."""
    current_app.logger.debug(f'Validating mhr_number={mhr_number} mhr_reg_type={mhr_reg_type} staff={staff}.')
    error_msg = ''
    if staff or not mhr_number or not mhr_reg_type or not PPR_RESTRICTED_REG_TYPES.get(mhr_reg_type):
        return error_msg
    ppr_reg_type: str = reg_utils.get_ppr_registration_type(mhr_number)
    if ppr_reg_type:
        restricted_reg_types: str = PPR_RESTRICTED_REG_TYPES.get(mhr_reg_type)
        current_app.logger.debug(f'Found PPR reg type {ppr_reg_type}, checking against {restricted_reg_types}')
        if restricted_reg_types.find((ppr_reg_type + ' ')) > 0:
            error_msg += PPR_LIEN_EXISTS
    return error_msg


def get_existing_location(registration: MhrRegistration):
    """Get the currently active location JSON."""
    if not registration:
        return {}
    if is_legacy():
        return validator_utils_legacy.get_existing_location(registration)
    if registration.locations and registration.locations[0].status_type == MhrStatusTypes.ACTIVE:
        return registration.locations[0].json
    if registration.change_registrations:
        for reg in registration.change_registrations:
            if reg.locations and reg.locations[0].status_type == MhrStatusTypes.ACTIVE:
                return reg.locations[0].json
    return {}


def get_permit_count(mhr_number: str, name: str) -> int:
    """Execute a query to count existing transport permit registrations on a home."""
    if is_legacy():
        return validator_utils_legacy.get_permit_count(mhr_number, name)
    return reg_utils.get_permit_count(mhr_number, name)


def validate_pid(pid: str):
    """Validate location pid exists with an LTSA lookup."""
    error_msg = ''
    if not pid:
        return error_msg
    lookup_result = ltsa.pid_lookup(pid)
    if not lookup_result:
        error_msg = LOCATION_PID_INVALID
    return error_msg


def get_existing_group_count(registration: MhrRegistration) -> int:
    """Count number of existing owner groups."""
    group_count: int = 0
    if is_legacy():
        return validator_utils_legacy.get_existing_group_count(registration)
    if not registration:
        return group_count
    for existing in registration.owner_groups:
        if existing.status_type in (MhrOwnerStatusTypes.ACTIVE, MhrOwnerStatusTypes.EXEMPT):
            group_count += 1
    if registration.change_registrations:
        for reg in registration.change_registrations:
            if reg.owner_groups:
                for existing in reg.owner_groups:
                    if existing.status_type in (MhrOwnerStatusTypes.ACTIVE, MhrOwnerStatusTypes.EXEMPT):
                        group_count += 1
    return group_count


def check_state_note(registration: MhrRegistration, staff: bool, error_msg: str, reg_type: str) -> str:
    """Check registration state for non-staff: frozen if active TAXN, NCON, or REST unit note."""
    if not registration or staff:
        return error_msg
    if registration.change_registrations:
        for reg in registration.change_registrations:
            if reg.notes and \
                    reg.notes[0].document_type in (MhrDocumentTypes.TAXN,
                                                   MhrDocumentTypes.NCON,
                                                   MhrDocumentTypes.REST) and \
                    reg.notes[0].status_type == MhrNoteStatusTypes.ACTIVE:
                error_msg += STATE_FROZEN_NOTE
            elif reg.registration_type in (MhrRegistrationTypes.PERMIT, MhrRegistrationTypes.PERMIT_EXTENSION) and \
                    reg_type not in (MhrRegistrationTypes.PERMIT, MhrRegistrationTypes.PERMIT_EXTENSION) and \
                    reg.notes and reg.notes[0].status_type == MhrNoteStatusTypes.ACTIVE and \
                    not reg.notes[0].is_expired():
                error_msg += STATE_FROZEN_PERMIT
    return error_msg


def valid_manufacturer_year(year: int) -> bool:
    """Check if a manufacturer MH home year is within 1 year of the current year."""
    now = model_utils.now_ts()
    return now.year == year or now.year == (year + 1) or now.year == (year - 1)


def valid_description_year(year: int, staff: bool) -> bool:
    """Check if a MH home year is within a valid range year."""
    if not staff:
        return valid_manufacturer_year(year)
    if year < HOME_DESCRIPTION_MIN_YEAR:
        return False
    now = model_utils.now_ts()
    return year <= (now.year + 1)


def validate_description(description, staff: bool):
    """Verify the description values."""
    error_msg = ''
    if not description:
        return error_msg
    if description.get('baseInformation'):
        base_info = description.get('baseInformation')
        if not base_info.get('year'):
            error_msg += DESCRIPTION_YEAR_REQUIRED
        elif not valid_description_year(base_info.get('year'), staff):
            error_msg += DESCRIPTION_YEAR_INVALID
        if not base_info.get('make') and not base_info.get('model'):
            error_msg += DESCRIPTION_MAKE_MODEL_REQUIRED
    if not staff and not description.get('csaNumber') and not description.get('engineerDate'):
        error_msg += DESCRIPTION_CSA_ENGINEER_REQUIRED
    return error_msg


def owner_name_match(registration: MhrRegistration = None,  # pylint: disable=too-many-branches
                     request_owner=None):
    """Verify the request owner name matches one of the current owner names."""
    if not registration or not request_owner:
        return False
    if is_legacy():
        return validator_utils_legacy.owner_name_match(registration, request_owner)
    request_name: str = ''
    first_name: str = ''
    last_name: str = ''
    match: bool = False
    is_business = request_owner.get('organizationName')
    if is_business:
        request_name = request_owner.get('organizationName').strip().upper()
    elif request_owner.get('individualName') and request_owner['individualName'].get('first') and \
            request_owner['individualName'].get('last'):
        first_name = request_owner['individualName'].get('first').strip().upper()
        last_name = request_owner['individualName'].get('last').strip().upper()
    if not request_name and not last_name:
        return False
    if registration.owner_groups:
        for group in registration.owner_groups:
            if group.status_type == MhrOwnerStatusTypes.ACTIVE:
                for owner in group.owners:
                    if is_business and owner.business_name == request_name:
                        match = True
                    elif not is_business and owner.first_name == first_name and owner.last_name == last_name:
                        match = True
    if not match and registration.change_registrations:  # pylint: disable=too-many-nested-blocks
        for reg in registration.change_registrations:
            for group in reg.owner_groups:
                if group.status_type == MhrOwnerStatusTypes.ACTIVE:
                    for owner in group.owners:
                        if is_business and owner.business_name == request_name:
                            match = True
                        elif not is_business and owner.first_name == first_name and owner.last_name == last_name:
                            match = True
    return match


def validate_delete_owners(registration: MhrRegistration = None,  # pylint: disable=too-many-branches
                           json_data: dict = None) -> str:
    """Check groups id's and owners are valid for deleted groups."""
    error_msg = ''
    if is_legacy():
        return validator_utils_legacy.validate_delete_owners(registration, json_data)
    if not registration or not json_data.get('deleteOwnerGroups'):
        return error_msg
    for deleted in json_data['deleteOwnerGroups']:  # pylint: disable=too-many-nested-blocks
        if deleted.get('groupId'):
            deleted_group = None
            group_id = deleted['groupId']
            for existing in registration.owner_groups:
                if existing.group_id == group_id:
                    deleted_group = existing
            if not deleted_group and registration.change_registrations:
                for reg in registration.change_registrations:
                    if reg.owner_groups:
                        for existing in reg.owner_groups:
                            if existing.group_id == group_id:
                                deleted_group = existing
            if deleted_group:
                tenancy_type = deleted.get('type')
                if deleted_group.status_type != MhrOwnerStatusTypes.ACTIVE:
                    error_msg += DELETE_GROUP_ID_INVALID.format(group_id=group_id)
                if tenancy_type and deleted_group.tenancy_type != tenancy_type and \
                        tenancy_type != MhrTenancyTypes.NA:
                    error_msg += DELETE_GROUP_TYPE_INVALID.format(group_id=group_id)
            else:
                error_msg += DELETE_GROUP_ID_NONEXISTENT.format(group_id=group_id)
    return error_msg


def delete_group(group_id: int, delete_groups):
    """Check if owner group is flagged for deletion."""
    if not delete_groups or group_id < 1:
        return False
    for group in delete_groups:
        if group.get('groupId', 0) == group_id:
            return True
    return False


def interest_required(groups, registration: MhrRegistration = None, delete_groups=None) -> bool:
    """Determine if group interest is required."""
    group_count: int = len(groups)  # Verify interest if multiple groups or existing interest.
    if group_count > 1:
        return True
    if is_legacy():
        return validator_utils_legacy.interest_required(groups, registration, delete_groups)
    if not registration:
        return False
    for existing in registration.owner_groups:
        if existing.status_type == MhrOwnerStatusTypes.ACTIVE and \
                existing.tenancy_type != MhrTenancyTypes.SOLE and \
                not delete_group(existing.group_id, delete_groups) and \
                existing.interest_denominator > 0:
            group_count += 1
    if registration.change_registrations:
        for reg in registration.change_registrations:
            if reg.owner_groups:
                for existing in reg.owner_groups:
                    if existing.status_type == MhrOwnerStatusTypes.ACTIVE and \
                            existing.tenancy_type != MhrTenancyTypes.SOLE and \
                            not delete_group(existing.group_id, delete_groups) and \
                            existing.interest_denominator > 0:
                        group_count += 1
    return group_count > 1


def validate_group_interest(groups, denominator: int,  # pylint: disable=too-many-branches
                            registration: MhrRegistration = None, delete_groups=None):
    """Verify owner group interest values are valid."""
    error_msg = ''
    if is_legacy():
        return validator_utils_legacy.validate_group_interest(groups, denominator, registration, delete_groups)
    numerator_sum: int = 0
    group_count: int = len(groups)  # Verify interest if multiple groups or existing interest.
    if registration:  # pylint: disable=too-many-nested-blocks
        for existing in registration.owner_groups:
            if existing.status_type == MhrOwnerStatusTypes.ACTIVE and \
                    existing.tenancy_type != MhrTenancyTypes.SOLE and \
                    not delete_group(existing.group_id, delete_groups):
                den = existing.interest_denominator
                if den > 0:
                    group_count += 1
                    if den == denominator:
                        numerator_sum += existing.interest_numerator
                    elif den < denominator:
                        numerator_sum += (denominator/den * existing.interest_numerator)
                    else:
                        numerator_sum += int((denominator * existing.interest_numerator)/den)
        if registration.change_registrations:
            for reg in registration.change_registrations:
                if reg.owner_groups:
                    for existing in reg.owner_groups:
                        if existing.status_type == MhrOwnerStatusTypes.ACTIVE and \
                                existing.tenancy_type != MhrTenancyTypes.SOLE and \
                                not delete_group(existing.group_id, delete_groups):
                            den = existing.interest_denominator
                            if den > 0:
                                group_count += 1
                                if den == denominator:
                                    numerator_sum += existing.interest_numerator
                                elif den < denominator:
                                    numerator_sum += (denominator/den * existing.interest_numerator)
                                else:
                                    numerator_sum += int((denominator * existing.interest_numerator)/den)
    current_app.logger.debug(f'group_count={group_count} denominator={denominator}')
    if group_count < 2:  # Could have transfer of joint tenants with no interest.
        return error_msg
    for group in groups:
        num = group.get('interestNumerator', 0)
        den = group.get('interestDenominator', 0)
        if num and den and num > 0 and den > 0:
            if den == denominator:
                numerator_sum += num
            else:
                numerator_sum += (denominator/den * num)
    if numerator_sum != denominator:
        error_msg = GROUP_INTEREST_MISMATCH
    return error_msg


def get_modified_group(registration: MhrRegistration, group_id: int) -> dict:
    """Find the existing owner group as JSON, matching on the group id."""
    group = {}
    if not registration:
        return group
    if is_legacy():
        return validator_utils_legacy.get_modified_group(registration, group_id)
    for existing in registration.owner_groups:
        if existing.group_id == group_id:
            group = existing.json
            break
    if not group and registration.change_registrations:
        for reg in registration.change_registrations:
            if reg.owner_groups:
                for existing in reg.owner_groups:
                    if existing.group_id == group_id:
                        group = existing.json
                        break
    return group


def validate_mhr_number(mhr_number: str, staff: bool) -> str:
    """Validate that a staff provide new MH mhr number is valid."""
    error_msg = ''
    if not staff or not mhr_number:
        return error_msg
    if not reg_utils.validate_mhr_number(mhr_number):
        error_msg += MHR_NUMBER_INVALID.format(mhr_num=mhr_number)
    return error_msg


def validate_location_different(current_loc: dict, new_loc: dict) -> str:
    """Verify the new location is not identical to the existing location."""
    error_msg = ''
    if not current_loc or not new_loc:
        return error_msg
    loc_1 = copy.deepcopy(current_loc)
    loc_2 = copy.deepcopy(new_loc)
    loc_1['status'] = ''
    loc_1['locationId'] = ''
    loc_1['leaveProvince'] = False
    loc_2['status'] = ''
    loc_2['locationId'] = ''
    loc_2['leaveProvince'] = False
    if loc_1.get('address') and loc_1['address'].get('postalCode') and \
            str(loc_1['address']['postalCode']).strip() == '':
        del loc_1['address']['postalCode']
    if loc_2.get('address') and loc_2['address'].get('postalCode') and \
            str(loc_2['address']['postalCode']).strip() == '':
        del loc_2['address']['postalCode']
    if loc_1 == loc_2:
        error_msg += LOCATION_INVALID_IDENTICAL
    return error_msg


def validate_location(location):  # pylint: disable=too-many-branches
    """Verify the combination of location values is valid."""
    error_msg = ''
    # No point validating if no no required locationType.
    if not location or not location.get('locationType'):
        return error_msg
    loc_type = location['locationType']
    if loc_type == MhrLocationTypes.RESERVE:
        if not location.get('bandName'):
            error_msg += BAND_NAME_REQUIRED
        if not location.get('reserveNumber'):
            error_msg += RESERVE_NUMBER_REQUIRED
    elif loc_type == MhrLocationTypes.MANUFACTURER:
        if not location.get('dealerName'):
            error_msg += LOCATION_DEALER_REQUIRED
    elif loc_type == MhrLocationTypes.MH_PARK:
        if not location.get('parkName'):
            error_msg += LOCATION_PARK_NAME_REQUIRED
        if not location.get('pad'):
            error_msg += LOCATION_PARK_PAD_REQUIRED
    elif loc_type == MhrLocationTypes.STRATA:
        if not location.get('pidNumber') and \
                (not location.get('lot') or not location.get('plan') or not location.get('landDistrict')):
            error_msg += LOCATION_STRATA_REQUIRED
    elif loc_type == MhrLocationTypes.OTHER and not location.get('pidNumber'):
        if not location.get('landDistrict'):
            error_msg += LOCATION_OTHER_REQUIRED
        elif location.get('plan') and location.get('lot'):
            error_msg += ''
        elif not location.get('districtLot'):
            error_msg += LOCATION_OTHER_REQUIRED
    error_msg += validate_location_allowed(location, loc_type)
    return error_msg


def validate_location_allowed(location, loc_type):
    """Verify the allowed location values by location type."""
    error_msg = ''
    if loc_type == MhrLocationTypes.MANUFACTURER:
        if location.get('bandName') or location.get('parkName') or location.get('reserveNumber') or \
                location.get('pad') or has_location_ltsa_details(location):
            error_msg = LOCATION_MANUFACTURER_ALLOWED
    elif loc_type == MhrLocationTypes.MH_PARK and \
            (location.get('bandName') or location.get('reserveNumber') or
             location.get('dealerName') or has_location_ltsa_details(location)):
        error_msg = LOCATION_PARK_ALLOWED
    elif loc_type == MhrLocationTypes.RESERVE and \
            (location.get('dealerName') or location.get('parkName') or location.get('pad')):
        error_msg = LOCATION_RESERVE_ALLOWED
    elif loc_type in (MhrLocationTypes.STRATA, MhrLocationTypes.OTHER):
        if location.get('dealerName') or location.get('parkName') or location.get('pad') or \
                location.get('bandName') or location.get('reserveNumber'):
            if loc_type == MhrLocationTypes.STRATA:
                error_msg = LOCATION_STRATA_ALLOWED
            else:
                error_msg = LOCATION_OTHER_ALLOWED
    return error_msg


def has_location_ltsa_details(location) -> bool:
    """Verify the location has ltsa detail properties."""
    if location.get('lot') or location.get('parcel') or location.get('block') or location.get('districtLot') or\
            location.get('partOf'):
        return True
    if location.get('section') or location.get('township') or location.get('range') or location.get('plan') or \
            location.get('meridian'):
        return True
    if location.get('pidNumber') or location.get('legalDescription') or location.get('landDistrict'):
        return True
    return False


def validate_tax_certificate(request_location, current_location):
    """Validate transport permit business rules specific to a tax certificate."""
    error_msg = ''
    if request_location and request_location.get('taxExpiryDate'):
        tax_ts = model_utils.ts_from_iso_format(request_location.get('taxExpiryDate'))
        if not model_utils.valid_tax_cert_date(model_utils.now_ts(), tax_ts):
            error_msg += LOCATION_TAX_DATE_INVALID
        elif not request_location.get('taxCertificate'):
            error_msg += LOCATION_TAX_CERT_REQUIRED
    else:
        if current_location and current_location.get('dealerName'):
            return error_msg
        if current_location.get('parkName') and request_location.get('parkName'):
            park_1 = current_location.get('parkName').strip().upper()
            park_2 = current_location.get('parkName').strip().upper()
            if park_1 == park_2:
                return error_msg
        error_msg += LOCATION_TAX_CERT_REQUIRED
    return error_msg
