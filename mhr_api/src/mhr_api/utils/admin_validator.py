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
"""This module holds staff admin registration validation for rules not covered by the schema.

Validation includes verifying the data combination for various registration document types and timestamps.
"""
from flask import current_app

from mhr_api.models import MhrRegistration, utils as model_utils, registration_utils as reg_utils
from mhr_api.models.type_tables import MhrDocumentTypes, MhrNoteStatusTypes, MhrRegistrationTypes
from mhr_api.models.db2.mhomnote import FROM_LEGACY_STATUS
from mhr_api.models.db2.utils import FROM_LEGACY_DOC_TYPE
from mhr_api.utils import validator_utils


NCAN_DOC_TYPES = ' CAU CAUC CAUE NCON NPUB REGC REST '  # Set of doc types NCAN can cancel.

VALIDATOR_ERROR = 'Error performing admin registration extra validation. '
DOC_ID_REQUIRED = 'Document ID is required for staff registrations. '
DOC_ID_EXISTS = 'Document ID must be unique: provided value already exists. '
DOC_ID_INVALID_CHECKSUM = 'Document ID is invalid: checksum failed. '
REMARKS_REQUIRED = 'Remarks are required with the registration document type. '
REMARKS_NOT_ALLOWED = 'Remarks are not allowed with the registration document type. '
NOTICE_REQUIRED = 'The giving notice party is required with the registration document type. '
NOTICE_NAME_REQUIRED = 'The giving notice party person or business name is required. '
NOTICE_ADDRESS_REQUIRED = 'The giving notice address is required. '
UPDATE_DOCUMENT_ID_REQUIRED = 'The update document ID is required. '
UPDATE_DOCUMENT_ID_INVALID = 'The update document ID is invalid. '
UPDATE_DOCUMENT_ID_STATUS = 'The update document ID is for a note or registration that is not active. '
NRED_INVALID_TYPE = 'Notice of Redemption NRED is only allowed with the TAXN document type. '
NCAN_DOCUMENT_ID_REQUIRED = 'The cancellation update document ID is required. '
NCAN_DOCUMENT_ID_INVALID = 'The cancellation update document ID is invalid. '
NCAN_DOCUMENT_ID_STATUS = 'The cancellation update document ID is for a note that is not active. '
NCAN_NOT_ALLOWED = 'Cancel Notice is not allowed with the registration document type {doc_type}. '
LOCATION_REQUIRED = 'A new location is required with this registration. '


def validate_admin_reg(registration: MhrRegistration, json_data) -> str:
    """Perform all extra manufacturer admin registration data validation checks not covered by schema validation."""
    error_msg: str = ''
    try:
        current_app.logger.info('Validating staff admin registration')
        error_msg += validate_doc_id(json_data)  # Initially required for all document types.
        error_msg += validator_utils.validate_submitting_party(json_data)
        doc_type: str = json_data.get('documentType', '')
        if not doc_type and json_data.get('note') and json_data['note'].get('documentType'):
            doc_type = json_data['note'].get('documentType')
        error_msg += validator_utils.validate_registration_state(registration,
                                                                 True,
                                                                 MhrRegistrationTypes.REG_STAFF_ADMIN,
                                                                 doc_type)
        error_msg += validate_giving_notice(json_data, doc_type)
        if doc_type and doc_type == MhrDocumentTypes.NRED:
            error_msg += validate_nred(registration, json_data)
        elif doc_type and doc_type == MhrDocumentTypes.NCAN:
            error_msg += validate_ncan(registration, json_data)
        elif doc_type and doc_type == MhrDocumentTypes.STAT:
            error_msg += validate_location(registration, json_data, True)
        elif doc_type and doc_type in (MhrDocumentTypes.REGC, MhrDocumentTypes.PUBA):
            error_msg += validate_location(registration, json_data, False)
            if json_data.get('note') and not json_data['note'].get('remarks'):
                error_msg += REMARKS_REQUIRED
    except Exception as validation_exception:   # noqa: B902; eat all errors
        current_app.logger.error('validate_admin exception: ' + str(validation_exception))
        error_msg += VALIDATOR_ERROR
    return error_msg


def validate_doc_id(json_data, check_exists: bool = True) -> str:
    """Validate the registration document id."""
    doc_id: str = ''
    if json_data.get('documentId'):
        doc_id = json_data.get('documentId')
    elif json_data.get('note'):
        doc_id = json_data['note'].get('documentId')
    current_app.logger.debug(f'Validating doc_id={doc_id}.')
    error_msg: str = ''
    if not doc_id:
        error_msg += DOC_ID_REQUIRED
    elif not validator_utils.checksum_valid(doc_id):
        error_msg += DOC_ID_INVALID_CHECKSUM
    if check_exists and doc_id:
        exists_count = MhrRegistration.get_doc_id_count(doc_id)
        if exists_count > 0:
            error_msg += DOC_ID_EXISTS
    return error_msg


def validate_giving_notice(json_data, doc_type: str) -> str:
    """Validate the registration giving notice party."""
    error_msg: str = ''
    if not json_data.get('note'):
        return error_msg
    if doc_type and not json_data['note'].get('givingNoticeParty') and \
            doc_type == MhrDocumentTypes.NRED:
        error_msg += NOTICE_REQUIRED
    elif json_data['note'].get('givingNoticeParty'):
        notice = json_data['note'].get('givingNoticeParty')
        if not notice.get('address'):
            error_msg += NOTICE_ADDRESS_REQUIRED
        if not notice.get('personName') and not notice.get('businessName'):
            error_msg += NOTICE_NAME_REQUIRED
    return error_msg


def validate_nred(registration: MhrRegistration, json_data) -> str:
    """Validate the notice of redemption document id."""
    error_msg: str = ''
    if not json_data.get('updateDocumentId'):
        return UPDATE_DOCUMENT_ID_REQUIRED
    if not registration:
        return error_msg
    status = None
    cancel_type: str = None
    cancel_doc_id = json_data.get('updateDocumentId')
    if model_utils.is_legacy() and registration.manuhome and registration.manuhome.notes:
        for note in registration.manuhome.notes:
            if note.reg_document_id == cancel_doc_id:
                status = FROM_LEGACY_STATUS.get(note.status)
                if FROM_LEGACY_DOC_TYPE.get(note.document_type):
                    cancel_type = FROM_LEGACY_DOC_TYPE.get(note.document_type)
                else:
                    cancel_type = note.document_type
    elif not model_utils.is_legacy():
        note = reg_utils.get_cancel_note(registration, cancel_doc_id)
        if note:
            status = note.status_type
            cancel_type = note.document_type
    if not status:
        error_msg += UPDATE_DOCUMENT_ID_INVALID
    elif status != MhrNoteStatusTypes.ACTIVE:
        error_msg += UPDATE_DOCUMENT_ID_STATUS
    if cancel_type and cancel_type != MhrDocumentTypes.TAXN:
        error_msg += NRED_INVALID_TYPE
    return error_msg


def validate_ncan(registration: MhrRegistration, json_data) -> str:
    """Validate the notice of cancellation document id."""
    error_msg: str = ''
    if not json_data.get('updateDocumentId') and not json_data.get('cancelDocumentId'):
        return NCAN_DOCUMENT_ID_REQUIRED
    if not registration:
        return error_msg
    status = None
    cancel_type: str = None
    cancel_doc_id = json_data.get('updateDocumentId') if json_data.get('updateDocumentId') \
        else json_data.get('cancelDocumentId')
    if model_utils.is_legacy() and registration.manuhome and registration.manuhome.notes:
        for note in registration.manuhome.notes:
            if note.reg_document_id == cancel_doc_id:
                status = FROM_LEGACY_STATUS.get(note.status)
                if FROM_LEGACY_DOC_TYPE.get(note.document_type):
                    cancel_type = FROM_LEGACY_DOC_TYPE.get(note.document_type)
                else:
                    cancel_type = note.document_type
    elif not model_utils.is_legacy():
        note = reg_utils.get_cancel_note(registration, cancel_doc_id)
        if note:
            status = note.status_type
            cancel_type = note.document_type
    if not status:
        error_msg += NCAN_DOCUMENT_ID_INVALID
    elif status != MhrNoteStatusTypes.ACTIVE:
        error_msg += NCAN_DOCUMENT_ID_STATUS
    if cancel_type and NCAN_DOC_TYPES.find(cancel_type) < 0:
        error_msg += NCAN_NOT_ALLOWED.format(doc_type=cancel_type)
    return error_msg


def validate_location(registration: MhrRegistration, json_data, required: bool) -> str:
    """Validate the change of location information."""
    error_msg: str = ''
    if not required and not json_data.get('location'):
        return error_msg
    if not json_data.get('location'):
        return LOCATION_REQUIRED

    current_location = validator_utils.get_existing_location(registration)
    location = json_data.get('location')
    error_msg += validator_utils.validate_location(location)
    error_msg += validator_utils.validate_location_different(current_location, location)
    error_msg += validator_utils.validate_tax_certificate(location, current_location)
    if location.get('pidNumber'):
        error_msg += validator_utils.validate_pid(location.get('pidNumber'))
    return error_msg
