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
"""This module holds registration validation for rules not covered by the schema.

Validation includes verifying the data combination for various registrations/filings and timestamps.
"""
from flask import current_app

from mhr_api.models import MhrRegistration
from mhr_api.models import registration_utils as reg_utils, utils as model_utils
from mhr_api.models.type_tables import MhrDocumentTypes, MhrLocationTypes
from mhr_api.models.type_tables import MhrTenancyTypes, MhrPartyTypes, MhrRegistrationTypes
from mhr_api.services.authz import MANUFACTURER_GROUP, QUALIFIED_USER_GROUP, DEALERSHIP_GROUP
from mhr_api.utils import validator_utils


OWNERS_NOT_ALLOWED = 'Owners not allowed with new registrations: use ownerGroups instead. '
OWNER_GROUPS_REQUIRED = 'At least one owner group is required for staff registrations. '
DECLARED_VALUE_REQUIRED = 'Declared value is required and must be greater than 0 for this registration. '
CONSIDERATION_REQUIRED = 'Consideration is required for this registration. '
TRANSFER_DATE_REQUIRED = 'Transfer date is required for this registration. '
ADD_SOLE_OWNER_INVALID = 'Only one sole owner and only one sole owner group can be added. '
GROUP_COMMON_INVALID = 'More than 1 group is required with the Tenants in Common owner group type. '
GROUP_NUMERATOR_MISSING = 'The owner group interest numerator is required and must be an integer greater than 0. '
GROUP_DENOMINATOR_MISSING = 'The owner group interest denominator is required and must be an integer greater than 0. '
VALIDATOR_ERROR = 'Error performing extra validation. '
NOTE_DOC_TYPE_INVALID = 'The note document type is invalid for the registration type. '
OWNERS_JOINT_INVALID = 'The owner group must contain at least 2 owners. '
OWNERS_COMMON_INVALID = 'Each COMMON owner group must contain exactly 1 owner. '
OWNERS_COMMON_SOLE_INVALID = 'SOLE owner group tenancy type is not allowed when there is more than 1 ' \
    'owner group. Use COMMON instead. '
LOCATION_ADDRESS_MISMATCH = 'The existing location address must match the current location address. '
OWNER_NAME_MISMATCH = 'The existing owner name must match exactly a current owner name for this registration. '
MANUFACTURER_DEALER_INVALID = 'The existing location must be a dealer or manufacturer lot for this registration. '
MANUFACTURER_PERMIT_INVALID = 'A manufacturer can only submit a transport permit once for a home. '
PARTY_TYPE_INVALID = 'Death of owner requires an executor, trustee, administrator owner party type. '
GROUP_PARTY_TYPE_INVALID = 'For TRUSTEE, ADMINISTRATOR, or EXECUTOR, all owner party types within the group ' + \
                            'must be identical. '
OWNER_DESCRIPTION_REQUIRED = 'Owner description is required for the owner party type. '
TRANSFER_PARTY_TYPE_INVALID = 'Owner party type of administrator, executor, trustee not allowed for this registration. '
TENANCY_PARTY_TYPE_INVALID = 'Owner group tenancy type must be NA for executors, trustees, or administrators. '
TENANCY_TYPE_NA_INVALID = 'Tenancy type NA is not allowed when there is 1 active owner group with 1 owner. '
TENANCY_TYPE_NA_INVALID2 = 'Tenancy type NA is only allowed when all owners are ADMINISTRATOR, EXECUTOR, ' \
    'or TRUSTEE party types. '
REG_STAFF_ONLY = 'Only BC Registries Staff are allowed to submit this registration. '
TRAN_DEATH_GROUP_COUNT = 'Only one owner group can be modified in a transfer due to death registration. '
TRAN_DEATH_JOINT_TYPE = 'The existing tenancy type must be joint for this transfer registration. '
TRAN_ADMIN_OWNER_INVALID = 'The existing owners must be administrators for this registration. '
TRAN_DEATH_OWNER_INVALID = 'The owners must be individuals or businesses for this registration. '
TRAN_EXEC_OWNER_INVALID = 'The owners must be individuals, businesses, or executors for this registration. '
TRAN_ADMIN_NEW_OWNER = 'The new owners must be administrators for this registration. '
TRAN_DEATH_NEW_OWNER = 'The new owners must be individuals or businesses for this registration. '
TRAN_AFFIDAVIT_NEW_OWNER = 'The new owners must be executors for this registration. '
TRAN_DEATH_ADD_OWNER = 'Owners cannot be added with this registration. '
TRAN_DEATH_CERT_MISSING = 'A death certificate number is required with this registration. '
TRAN_DEATH_CORP_NUM_MISSING = 'A removed business owner corporation number is required with this registration. '
TRAN_DEATH_DATE_MISSING = 'A death date and time is required with this registration. '
TRAN_DEATH_DATE_INVALID = 'A death date and time must be in the past. '
TRAN_AFFIDAVIT_DECLARED_VALUE = 'Declared value must be cannot be greater than 25000 for this registration. '
TRAN_WILL_PROBATE = 'One (and only one) deceased owner must have a probate document (no death certificate). '
TRAN_WILL_DEATH_CERT = 'Deceased owners without a probate document must have a death certificate. '
TRAN_WILL_NEW_OWNER = 'The new owners must be executors for this registration. '
TRAN_EXEC_DEATH_CERT = 'All deceased owners must have a death certificate. '
TRAN_ADMIN_GRANT = 'One (and only one) deceased owner must have a grant document (no death certificate). '
TRAN_ADMIN_DEATH_CERT = 'Deceased owners without a grant document must have a death certificate. '
TRAN_QUALIFIED_DELETE = 'Qualified suppliers must either delete one owner group or all owner groups. '
NOTICE_NAME_REQUIRED = 'The giving notice party person or business name is required. '
NOTICE_ADDRESS_REQUIRED = 'The giving notice address is required. '
DESTROYED_FUTURE = 'The exemption destroyed date and time (expiryDateTime) cannot be in the future. '
DESTROYED_EXRS = 'The destroyed date and time (note expiryDateTime) cannot be submitted with a residential exemption. '
LOCATION_NOT_ALLOWED = 'A Residential Exemption is not allowed when the home current location is a ' \
    'dealer/manufacturer lot or manufactured home park. '
TRANS_DOC_TYPE_INVALID = 'The transferDocumentType is only allowed with a TRANS transfer due to sale or gift. '

PPR_SECURITY_AGREEMENT = ' SA TA TG TM '


def validate_registration(json_data, staff: bool = False):
    """Perform all registration data validation checks not covered by schema validation."""
    error_msg = ''
    try:
        if staff:
            error_msg += validator_utils.validate_doc_id(json_data, True)
            if not json_data.get('ownerGroups'):
                error_msg += OWNER_GROUPS_REQUIRED
        error_msg += validator_utils.validate_submitting_party(json_data)
        error_msg += validator_utils.validate_mhr_number(json_data.get('mhrNumber', ''), staff)
        owner_count: int = len(json_data.get('ownerGroups')) if json_data.get('ownerGroups') else 0
        error_msg += validate_owner_groups(json_data.get('ownerGroups'), True, None, None, owner_count)
        error_msg += validate_owner_party_type(json_data, json_data.get('ownerGroups'), True, owner_count)
        error_msg += validator_utils.validate_location(json_data.get('location'))
        error_msg += validator_utils.validate_description(json_data.get('description'), staff)
    except Exception as validation_exception:   # noqa: B902; eat all errors
        current_app.logger.error('validate_registration exception: ' + str(validation_exception))
        error_msg += VALIDATOR_ERROR
    return error_msg


def validate_transfer(registration: MhrRegistration,  # pylint: disable=too-many-branches
                      json_data,
                      staff: bool,
                      group: str):
    """Perform all transfer data validation checks not covered by schema validation."""
    error_msg = ''
    try:
        current_app.logger.info(f'Validating transfer staff={staff}, group={group}')
        if not staff and reg_utils.is_transfer_due_to_death_staff(json_data.get('registrationType')):
            return REG_STAFF_ONLY
        if staff:
            error_msg += validator_utils.validate_doc_id(json_data, True)
        elif registration:
            error_msg += validator_utils.validate_ppr_lien(registration.mhr_number, MhrRegistrationTypes.TRANS, staff)
        active_group_count: int = get_active_group_count(json_data, registration)
        error_msg += validator_utils.validate_submitting_party(json_data)
        error_msg += validate_owner_groups(json_data.get('addOwnerGroups'),
                                           False,
                                           registration,
                                           json_data.get('deleteOwnerGroups'),
                                           active_group_count)
        error_msg += validate_owner_party_type(json_data, json_data.get('addOwnerGroups'), False, active_group_count)
        reg_type: str = json_data.get('registrationType', MhrRegistrationTypes.TRANS)
        error_msg += validator_utils.validate_registration_state(registration, staff, reg_type)
        error_msg += validator_utils.validate_draft_state(json_data)
        if registration and json_data.get('deleteOwnerGroups'):
            error_msg += validator_utils.validate_delete_owners(registration, json_data)
        if not staff:
            if not isinstance(json_data.get('declaredValue', 0), int) or not json_data.get('declaredValue') or \
                    json_data.get('declaredValue') < 0:
                error_msg += DECLARED_VALUE_REQUIRED
            if reg_type == MhrRegistrationTypes.TRANS and \
                    (not json_data.get('transferDocumentType') or
                     json_data.get('transferDocumentType') in (MhrDocumentTypes.TRANS_QUIT_CLAIM,
                                                               MhrDocumentTypes.TRANS_RECEIVERSHIP,
                                                               MhrDocumentTypes.TRANS_SEVER_GRANT)):
                if not json_data.get('consideration'):
                    error_msg += CONSIDERATION_REQUIRED
                if not json_data.get('transferDate'):
                    error_msg += TRANSFER_DATE_REQUIRED
            if json_data.get('deleteOwnerGroups') and len(json_data.get('deleteOwnerGroups')) != 1 and \
                    group == QUALIFIED_USER_GROUP and \
                    len(json_data.get('deleteOwnerGroups')) != validator_utils.get_existing_group_count(registration):
                error_msg += TRAN_QUALIFIED_DELETE
        if reg_type != MhrRegistrationTypes.TRANS and json_data.get('transferDocumentType'):
            error_msg += TRANS_DOC_TYPE_INVALID
        if reg_utils.is_transfer_due_to_death(json_data.get('registrationType')):
            error_msg += validate_transfer_death(registration, json_data)
    except Exception as validation_exception:   # noqa: B902; eat all errors
        current_app.logger.error('validate_transfer exception: ' + str(validation_exception))
        error_msg += VALIDATOR_ERROR
    return error_msg


def validate_exemption(registration: MhrRegistration,  # pylint: disable=too-many-branches
                       json_data,
                       staff: bool = False):
    """Perform all exemption data validation checks not covered by schema validation."""
    error_msg = ''
    try:
        current_app.logger.info(f'Validating exemption staff={staff}')
        if staff:
            error_msg += validator_utils.validate_doc_id(json_data)
        elif registration:
            error_msg += validator_utils.validate_ppr_lien(registration.mhr_number,
                                                           MhrRegistrationTypes.EXEMPTION_RES,
                                                           staff)
        location = validator_utils.get_existing_location(registration)
        if location and (location.get('parkName') or location.get('dealerName')):
            error_msg += LOCATION_NOT_ALLOWED
        error_msg += validator_utils.validate_submitting_party(json_data)
        reg_type: str = MhrRegistrationTypes.EXEMPTION_RES
        if json_data.get('nonResidential') or \
                (json_data.get('note') and json_data['note'].get('documentType') == MhrDocumentTypes.EXNR):
            reg_type = MhrRegistrationTypes.EXEMPTION_NON_RES
        error_msg += validator_utils.validate_registration_state(registration, staff, reg_type)
        error_msg += validator_utils.validate_draft_state(json_data)
        if json_data.get('note'):
            if json_data['note'].get('documentType') and \
                    json_data['note'].get('documentType') not in (MhrDocumentTypes.EXRS, MhrDocumentTypes.EXNR):
                error_msg += NOTE_DOC_TYPE_INVALID
            if json_data['note'].get('givingNoticeParty'):
                notice = json_data['note'].get('givingNoticeParty')
                if not notice.get('address'):
                    error_msg += NOTICE_ADDRESS_REQUIRED
                if not notice.get('personName') and not notice.get('businessName'):
                    error_msg += NOTICE_NAME_REQUIRED
            if json_data['note'].get('expiryDateTime'):
                if not json_data.get('nonResidential') or \
                        json_data['note'].get('documentType', '') != MhrDocumentTypes.EXNR:
                    error_msg += DESTROYED_EXRS
                else:
                    expiry = json_data['note'].get('expiryDateTime')
                    expiry_ts = model_utils.ts_from_iso_format(expiry)
                    now = model_utils.now_ts()
                    if expiry_ts > now:
                        error_msg += DESTROYED_FUTURE
    except Exception as validation_exception:   # noqa: B902; eat all errors
        current_app.logger.error('validate_exemption exception: ' + str(validation_exception))
        error_msg += VALIDATOR_ERROR
    return error_msg


def validate_permit(registration: MhrRegistration, json_data, staff: bool = False, group_name: str = None):
    """Perform all transport permit data validation checks not covered by schema validation."""
    error_msg = ''
    try:
        current_app.logger.info(f'Validating permit staff={staff}')
        if staff:
            error_msg += validator_utils.validate_doc_id(json_data, True)
        elif registration:
            error_msg += validator_utils.validate_ppr_lien(registration.mhr_number, MhrRegistrationTypes.PERMIT, staff)
        current_location = validator_utils.get_existing_location(registration)
        if registration and group_name and group_name == MANUFACTURER_GROUP:
            error_msg += validate_manufacturer_permit(registration.mhr_number, json_data.get('submittingParty'),
                                                      current_location)
        if registration and group_name and group_name == DEALERSHIP_GROUP and current_location and \
                current_location.get('locationType', '') != MhrLocationTypes.MANUFACTURER:
            error_msg += MANUFACTURER_DEALER_INVALID
        error_msg += validator_utils.validate_submitting_party(json_data)
        error_msg += validator_utils.validate_registration_state(registration, staff, MhrRegistrationTypes.PERMIT)
        error_msg += validator_utils.validate_draft_state(json_data)
        if json_data.get('newLocation'):
            location = json_data.get('newLocation')
            error_msg += validator_utils.validate_location(location)
            error_msg += validator_utils.validate_location_different(current_location, location)
            error_msg += validator_utils.validate_tax_certificate(location, current_location)
            if not json_data.get('landStatusConfirmation'):
                if location.get('locationType') and \
                        location['locationType'] in (MhrLocationTypes.STRATA,
                                                     MhrLocationTypes.RESERVE,
                                                     MhrLocationTypes.OTHER):
                    error_msg += validator_utils.STATUS_CONFIRMATION_REQUIRED
                elif current_location and location.get('locationType', '') == MhrLocationTypes.MH_PARK:
                    if current_location.get('locationType', '') != MhrLocationTypes.MH_PARK or \
                            current_location.get('parkName', '') != location.get('parkName'):
                        error_msg += validator_utils.STATUS_CONFIRMATION_REQUIRED
            if location.get('pidNumber'):
                error_msg += validator_utils.validate_pid(location.get('pidNumber'))
    except Exception as validation_exception:   # noqa: B902; eat all errors
        current_app.logger.error('validate_transfer exception: ' + str(validation_exception))
        error_msg += VALIDATOR_ERROR
    return error_msg


def existing_owner_added(new_owners, owner) -> bool:
    """Check if the existing owner name matches an owner name in the new group."""
    if owner and new_owners:
        for owner_json in new_owners:
            if owner_json.get('individualName') and owner.get('individualName') and \
                    owner_json['individualName'].get('last') == owner['individualName'].get('last') and \
                    owner_json['individualName'].get('first') == owner['individualName'].get('first'):
                if owner_json['individualName'].get('middle', '') == owner['individualName'].get('middle', ''):
                    return True
            elif owner_json.get('organizationName') and owner.get('organizationName') and \
                    owner_json.get('organizationName') == owner.get('organizationName'):
                return True
    return False


def validate_transfer_death_existing_owners(reg_type: str, modified_group):
    """Apply existing owner validation rules specific to transfer due to death registration types."""
    error_msg: str = ''
    if not modified_group or not modified_group.get('owners'):
        return error_msg
    owners = modified_group.get('owners')
    for owner_json in owners:
        if reg_type == MhrRegistrationTypes.TRAND and \
                owner_json.get('partyType') not in (MhrPartyTypes.OWNER_BUS, MhrPartyTypes.OWNER_IND):
            error_msg += TRAN_DEATH_OWNER_INVALID
    return error_msg


def new_owner_exists(modified_group, owner) -> bool:
    """Check if the new owner name matches an existing group owner name."""
    if owner and modified_group and modified_group.get('owners'):
        for owner_json in modified_group.get('owners'):
            if owner_json.get('individualName') and owner.get('individualName') and \
                    owner_json['individualName'].get('last') == owner['individualName'].get('last') and \
                    owner_json['individualName'].get('first') == owner['individualName'].get('first'):
                if owner_json['individualName'].get('middle', '') == owner['individualName'].get('middle', ''):
                    return True
            elif owner_json.get('organizationName') and owner.get('organizationName') and \
                    owner_json.get('organizationName') == owner.get('organizationName'):
                return True
    return False


def validate_transfer_death_new_owners(reg_type: str, new_owners, modified_group):
    """Apply new owner validation rules specific to transfer due to death registration types."""
    error_msg: str = ''
    if not new_owners:
        return error_msg
    exec_count: int = 0
    for owner in new_owners:
        party_type = owner.get('partyType')
        if reg_type == MhrRegistrationTypes.TRAND and party_type and \
                party_type not in (MhrPartyTypes.OWNER_BUS, MhrPartyTypes.OWNER_IND):
            error_msg += TRAN_DEATH_NEW_OWNER
        elif reg_type == MhrRegistrationTypes.TRANS_ADMIN and \
                (not party_type or party_type != MhrPartyTypes.ADMINISTRATOR):
            error_msg += TRAN_ADMIN_NEW_OWNER
        elif reg_type in (MhrRegistrationTypes.TRANS_WILL, MhrRegistrationTypes.TRANS_AFFIDAVIT) and \
                party_type and party_type == MhrPartyTypes.EXECUTOR:
            exec_count += 1
        if reg_type == MhrRegistrationTypes.TRAND and modified_group and not new_owner_exists(modified_group, owner):
            error_msg += TRAN_DEATH_ADD_OWNER
    if exec_count != len(new_owners) and reg_type == MhrRegistrationTypes.TRANS_AFFIDAVIT:
        error_msg += TRAN_AFFIDAVIT_NEW_OWNER
    elif exec_count != len(new_owners) and reg_type == MhrRegistrationTypes.TRANS_WILL:
        error_msg += TRAN_WILL_NEW_OWNER
    return error_msg


def validate_transfer_death_owners(reg_type: str, new_owners, delete_owners):  # pylint: disable=too-many-branches
    """Apply owner delete/add validation rules specific to transfer due to death registration types."""
    error_msg: str = ''
    probate_count: int = 0
    death_count: int = 0
    party_count: int = 0
    for owner_json in delete_owners:
        if not existing_owner_added(new_owners, owner_json) and reg_type == MhrRegistrationTypes.TRAND:
            if owner_json.get('organizationName') and not owner_json.get('deathCorpNumber'):
                error_msg += TRAN_DEATH_CORP_NUM_MISSING
            elif not owner_json.get('organizationName') and not owner_json.get('deathCertificateNumber'):
                error_msg += TRAN_DEATH_CERT_MISSING
            if not owner_json.get('deathDateTime'):
                error_msg += TRAN_DEATH_DATE_MISSING
            elif not model_utils.date_elapsed(owner_json.get('deathDateTime')):
                error_msg += TRAN_DEATH_DATE_INVALID
        elif reg_type in (MhrRegistrationTypes.TRANS_WILL, MhrRegistrationTypes.TRANS_AFFIDAVIT,
                          MhrRegistrationTypes.TRANS_ADMIN):
            if reg_type == MhrRegistrationTypes.TRANS_WILL and \
                    owner_json.get('partyType', '') == MhrPartyTypes.EXECUTOR:
                party_count += 1
            elif reg_type == MhrRegistrationTypes.TRANS_ADMIN and \
                    owner_json.get('partyType', '') == MhrPartyTypes.ADMINISTRATOR:
                party_count += 1
            elif not owner_json.get('deathCertificateNumber') and not owner_json.get('deathDateTime'):
                probate_count += 1
            elif owner_json.get('deathCertificateNumber') and owner_json.get('deathDateTime'):
                death_count += 1
                if not model_utils.date_elapsed(owner_json.get('deathDateTime')):
                    error_msg += TRAN_DEATH_DATE_INVALID
            if not owner_json.get('deathCertificateNumber') and owner_json.get('deathDateTime'):
                error_msg += TRAN_DEATH_CERT_MISSING
            if not owner_json.get('deathDateTime') and owner_json.get('deathCertificateNumber'):
                error_msg += TRAN_DEATH_DATE_MISSING
    if reg_type in (MhrRegistrationTypes.TRANS_WILL, MhrRegistrationTypes.TRANS_ADMIN) and party_count < 1:
        if probate_count != 1:
            error_msg += TRAN_WILL_PROBATE if reg_type == MhrRegistrationTypes.TRANS_WILL else TRAN_ADMIN_GRANT
        if (death_count + 1) != len(delete_owners) and reg_type == MhrRegistrationTypes.TRANS_WILL:
            error_msg += TRAN_WILL_DEATH_CERT
        elif (death_count + 1) != len(delete_owners):
            error_msg += TRAN_ADMIN_DEATH_CERT
    elif reg_type == MhrRegistrationTypes.TRANS_AFFIDAVIT and death_count != len(delete_owners):
        error_msg += TRAN_EXEC_DEATH_CERT
    return error_msg


def validate_transfer_death(registration: MhrRegistration, json_data):
    """Apply validation rules specific to transfer due to death registration types."""
    error_msg: str = ''
    if not json_data.get('deleteOwnerGroups') or not json_data.get('addOwnerGroups'):
        return error_msg
    reg_type: str = json_data.get('registrationType')
    tenancy_type: str = None
    modified_group: dict = None
    if json_data.get('deleteOwnerGroups'):
        modified_group = validator_utils.get_modified_group(registration,
                                                            json_data['deleteOwnerGroups'][0].get('groupId', 0))
    if len(json_data.get('deleteOwnerGroups')) != 1 or len(json_data.get('addOwnerGroups')) != 1:
        error_msg += TRAN_DEATH_GROUP_COUNT
    if json_data['deleteOwnerGroups'][0].get('type'):
        tenancy_type = json_data['deleteOwnerGroups'][0].get('type')
        if reg_type == MhrRegistrationTypes.TRAND and tenancy_type != MhrTenancyTypes.JOINT:
            error_msg += TRAN_DEATH_JOINT_TYPE
    new_owners = json_data['addOwnerGroups'][0].get('owners')
    # check existing owners.
    error_msg += validate_transfer_death_existing_owners(reg_type, modified_group)
    # check new owners.
    error_msg += validate_transfer_death_new_owners(reg_type, new_owners, modified_group)
    delete_owners = json_data['deleteOwnerGroups'][0].get('owners')
    if new_owners and delete_owners:
        error_msg += validate_transfer_death_owners(reg_type, new_owners, delete_owners)
    if reg_type == MhrRegistrationTypes.TRANS_AFFIDAVIT and json_data.get('declaredValue') and \
            json_data.get('declaredValue') > 25000:
        error_msg += TRAN_AFFIDAVIT_DECLARED_VALUE
    return error_msg


def validate_owner(owner):
    """Verify owner names are valid."""
    error_msg = ''
    if not owner:
        return error_msg
    desc: str = 'owner'
    if owner.get('organizationName'):
        error_msg += validator_utils.validate_text(owner.get('organizationName'), desc + ' organization name')
    elif owner.get('individualName'):
        error_msg += validator_utils.validate_individual_name(owner.get('individualName'), desc)
    return error_msg


def validate_owner_group(group, int_required: bool = False):
    """Verify owner group is valid."""
    error_msg = ''
    if not group:
        return error_msg
    tenancy_type: str = group.get('type', '')
    if tenancy_type == MhrTenancyTypes.COMMON or int_required:
        if not group.get('interestNumerator') or group.get('interestNumerator', 0) < 1:
            error_msg += GROUP_NUMERATOR_MISSING
        if not group.get('interestDenominator') or group.get('interestDenominator', 0) < 1:
            error_msg += GROUP_DENOMINATOR_MISSING
    if tenancy_type == MhrTenancyTypes.NA and group.get('owners') and len(group.get('owners')) > 1:
        owner_count: int = 0
        for owner in group.get('owners'):
            if not owner.get('partyType') or \
                    owner.get('partyType') in (MhrPartyTypes.OWNER_BUS, MhrPartyTypes.OWNER_IND):
                owner_count += 1
        if owner_count != 0:
            error_msg += TENANCY_TYPE_NA_INVALID2
    if tenancy_type == MhrTenancyTypes.JOINT and (not group.get('owners') or len(group.get('owners')) < 2):
        error_msg += OWNERS_JOINT_INVALID
    elif tenancy_type == MhrTenancyTypes.COMMON and (not group.get('owners') or len(group.get('owners')) > 1):
        error_msg += OWNERS_COMMON_INVALID
    elif tenancy_type == MhrTenancyTypes.SOLE and int_required:
        error_msg += OWNERS_COMMON_SOLE_INVALID
    return error_msg


def delete_group(group_id: int, delete_groups):
    """Check if owner group is flagged for deletion."""
    if not delete_groups or group_id < 1:
        return False
    for group in delete_groups:
        if group.get('groupId', 0) == group_id:
            return True
    return False


def common_tenancy(groups, new: bool, active_count: int = 0) -> bool:
    """Determine if the owner groups is a tenants in common scenario."""
    if new and groups and len(groups) == 1:
        return False
    for group in groups:
        group_type = group.get('type', '')
        if group_type and group_type != MhrTenancyTypes.SOLE and active_count > 1:
            return True
    return False


def validate_owner_groups(groups,
                          new: bool,
                          registration: MhrRegistration = None,
                          delete_groups=None,
                          active_count: int = 0):
    """Verify owner groups are valid."""
    error_msg = ''
    if not groups:
        return error_msg
    so_count: int = 0
    if common_tenancy(groups, new, active_count):
        return validate_owner_groups_common(groups, registration, delete_groups)
    for group in groups:
        tenancy_type: str = group.get('type', '')
        if new and tenancy_type == MhrTenancyTypes.COMMON:
            error_msg += GROUP_COMMON_INVALID
        error_msg += validate_owner_group(group, False)
        for owner in group.get('owners'):
            if tenancy_type == MhrTenancyTypes.SOLE:
                so_count += 1
            error_msg += validate_owner(owner)
    if so_count > 1 or (so_count == 1 and len(groups) > 1):
        error_msg += ADD_SOLE_OWNER_INVALID
    if not new and active_count == 1 and tenancy_type == MhrTenancyTypes.COMMON:
        error_msg += GROUP_COMMON_INVALID
    return error_msg


def validate_owner_groups_common(groups, registration: MhrRegistration = None, delete_groups=None):
    """Verify tenants in common owner groups are valid."""
    error_msg = ''
    tc_owner_count_invalid: bool = False
    common_denominator: int = 0
    int_required: bool = validator_utils.interest_required(groups, registration, delete_groups)
    for group in groups:
        if common_denominator == 0:
            common_denominator = group.get('interestDenominator', 0)
        elif group.get('interestDenominator', 0) > common_denominator:
            common_denominator = group.get('interestDenominator', 0)
        if not group.get('owners'):
            tc_owner_count_invalid = True
        error_msg += validate_owner_group(group, int_required)
        for owner in group.get('owners'):
            error_msg += validate_owner(owner)
    error_msg += validator_utils.validate_group_interest(groups, common_denominator, registration, delete_groups)
    if tc_owner_count_invalid:
        error_msg += OWNERS_COMMON_INVALID
    return error_msg


def validate_manufacturer_permit(mhr_number: str, party, current_location):
    """Validate transport permit business rules specific to manufacturers."""
    error_msg = ''
    # Must be located on a dealer's/manufacturer's lot.
    if current_location and not current_location.get('dealerName'):
        error_msg += MANUFACTURER_DEALER_INVALID
    # Permit can only be issued once per home by a manufacturer.
    if mhr_number and party:
        name: str = party.get('businessName')
        if not name and party.get('personName') and party['personName'].get('first') and \
                party['personName'].get('last'):
            name = party['personName'].get('first').strip().upper() + ' '
            if party['personName'].get('middle'):
                name += party['personName'].get('middle').strip().upper() + ' '
            name += party['personName'].get('last').strip().upper()
        if name:
            permit_count: int = validator_utils.get_permit_count(mhr_number, name)
            if permit_count > 0:
                error_msg += MANUFACTURER_PERMIT_INVALID
    return error_msg


def location_address_match(current_location, request_location):
    """Verify the request and current location addresses match."""
    address_1 = current_location.get('address')
    address_2 = request_location.get('address')
    if address_1 and address_2:
        city = address_2.get('city').strip().upper() if address_2.get('city') else ''
        street = address_2.get('street').strip().upper() if address_2.get('street') else ''
        region = address_2.get('region').strip().upper() if address_2.get('region') else ''
        p_code = address_2.get('postalCode').strip().upper() if address_2.get('postalCode') else ''
        if p_code and address_1.get('postalCode'):
            return p_code == address_1.get('postalCode') and city == address_1.get('city') and \
                   street == address_1.get('street') and region == address_1.get('region')
        return city == address_1.get('city') and street == address_1.get('street') and region == address_1.get('region')
    return False


def validate_owner_party_type(json_data,  # pylint: disable=too-many-branches
                              groups, new: bool,
                              active_group_count: int):
    """Verify owner groups are valid."""
    error_msg = ''
    owner_death: bool = reg_utils.is_transfer_due_to_death_staff(json_data.get('registrationType'))
    if not groups:
        return error_msg
    for group in groups:
        if not new and len(groups) > 1 and group_owners_unchanged(json_data, group):
            continue
        party_count: int = 0
        owner_count: int = 0
        group_parties_invalid: bool = False
        first_party_type: str = None
        if group.get('owners'):
            owner_count = len(group.get('owners'))
            for owner in group['owners']:
                party_type = owner.get('partyType', None)
                if party_type and party_type in (MhrPartyTypes.ADMINISTRATOR, MhrPartyTypes.EXECUTOR,
                                                 MhrPartyTypes.TRUSTEE):
                    party_count += 1
                    if not first_party_type:
                        first_party_type = party_type
                    if first_party_type and party_type != first_party_type:
                        group_parties_invalid = True
                if party_type and not owner.get('description') and \
                        party_type in (MhrPartyTypes.ADMINISTRATOR, MhrPartyTypes.EXECUTOR,
                                       MhrPartyTypes.TRUST, MhrPartyTypes.TRUSTEE):
                    error_msg += OWNER_DESCRIPTION_REQUIRED
                if not new and not owner_death and party_type and \
                        party_type in (MhrPartyTypes.ADMINISTRATOR, MhrPartyTypes.EXECUTOR,
                                       MhrPartyTypes.TRUST, MhrPartyTypes.TRUSTEE):
                    error_msg += TRANSFER_PARTY_TYPE_INVALID
        if active_group_count < 2 and group.get('type', '') == MhrTenancyTypes.NA and owner_count == 1:
            error_msg += TENANCY_TYPE_NA_INVALID  # SOLE owner cannot be NA
        elif active_group_count > 1 and party_count > 0 and group.get('type', '') != MhrTenancyTypes.NA:
            error_msg += TENANCY_PARTY_TYPE_INVALID  # COMMON scenario
        elif active_group_count == 1 and owner_count > 1 and party_count > 0 and \
                group.get('type', '') != MhrTenancyTypes.NA:
            error_msg += TENANCY_PARTY_TYPE_INVALID  # JOINT scenario
        if new and group_parties_invalid:
            error_msg += GROUP_PARTY_TYPE_INVALID
    return error_msg


def get_active_group_count(json_data, registration: MhrRegistration) -> int:
    """Count number of active owner groups."""
    group_count: int = 0
    if json_data.get('ownerGroups'):
        group_count += len(json_data.get('ownerGroups'))
    else:
        if json_data.get('addOwnerGroups'):
            group_count += len(json_data.get('addOwnerGroups'))
        if json_data.get('deleteOwnerGroups'):
            group_count -= len(json_data.get('deleteOwnerGroups'))
        group_count += validator_utils.get_existing_group_count(registration)
    return group_count


def group_owners_unchanged(json_data, add_group) -> bool:
    """Check if the owners in an added group are identical to the owners in a deleted group."""
    if not json_data.get('deleteOwnerGroups') or not add_group.get('owners'):
        return False
    for group in json_data.get('deleteOwnerGroups'):
        if group.get('owners') and len(group['owners']) == len(add_group['owners']):
            identical: bool = True
            for add_owner in add_group.get('owners'):
                owner_match: bool = False
                for del_owner in group.get('owners'):
                    if owner_name_address_match(add_owner, del_owner):
                        owner_match = True
                if not owner_match:
                    identical = False
            if identical:
                return True
    return False


def owner_name_address_match(owner1, owner2) -> bool:
    """Check if 2 owner json name and addresses are identical."""
    address_match: bool = False
    name_match: bool = False
    if owner1.get('address') and owner2.get('address') and owner1.get('address') == owner2.get('address'):
        address_match = True
    if owner1.get('organizationName') and owner2.get('organizationName') and \
            owner1.get('organizationName') == owner2.get('organizationName'):
        name_match = True
    elif owner1.get('individualName') and owner2.get('individualName') and \
            owner1.get('individualName') == owner2.get('individualName'):
        name_match = True
    return address_match and name_match
