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

# pylint: disable=too-few-public-methods

"""This module holds methods to support registration model mapping to dict/json."""
from flask import current_app

from mhr_api.models import utils as model_utils
from mhr_api.models.registration_utils import include_caution_note, find_cancelled_note, get_document_description
from mhr_api.models.type_tables import (
    MhrDocumentTypes,
    MhrNoteStatusTypes,
    MhrOwnerStatusTypes,
    MhrPartyTypes,
    MhrRegistrationTypes,
    MhrStatusTypes
)

from .mhr_note import MhrNote


def set_payment_json(registration, reg_json):
    """Add registration payment info json if payment exists."""
    if registration.pay_invoice_id and registration.pay_path:
        payment = {
            'invoiceId': str(registration.pay_invoice_id),
            'receipt': registration.pay_path
        }
        reg_json['payment'] = payment
    return reg_json


def set_submitting_json(registration, reg_json) -> dict:
    """Build the submitting party JSON if available."""
    if reg_json and registration.parties:
        for party in registration.parties:
            if party.party_type == MhrPartyTypes.SUBMITTING:
                reg_json['submittingParty'] = party.json
                break
    return reg_json


def set_location_json(registration, reg_json, current: bool) -> dict:
    """Build the location JSON conditional on current."""
    location = None
    if registration.locations:
        loc = registration.locations[0]
        if (current or registration.current_view) and loc.status_type == MhrStatusTypes.ACTIVE:
            location = loc
        elif not (current or registration.current_view) and loc.registration_id == registration.id:
            location = loc
    if not location and current and registration.change_registrations:
        for reg in registration.change_registrations:
            if reg.locations:
                loc = reg.locations[0]
                if loc.status_type == MhrStatusTypes.ACTIVE:
                    location = loc
    if location:
        if reg_json.get('registrationType', '') in (MhrRegistrationTypes.PERMIT,
                                                    MhrRegistrationTypes.PERMIT_EXTENSION):
            reg_json['newLocation'] = location.json
        else:
            reg_json['location'] = location.json
    return reg_json


def get_sections_json(registration, reg_id) -> dict:
    """Build the description sections JSON from the registration id."""
    sections = []
    desc_reg = None
    if registration.id == reg_id:
        desc_reg = registration
    elif registration.change_registrations:
        for reg in registration.change_registrations:
            if reg.id == reg_id:
                desc_reg = reg
                break
    if desc_reg and desc_reg.sections:
        for section in desc_reg.sections:
            sections.append(section.json)
    return sections


def set_description_json(registration, reg_json, current: bool) -> dict:
    """Build the description JSON conditional on current."""
    description = None
    if registration.descriptions:
        desc = registration.descriptions[0]
        if (current or registration.current_view) and desc.status_type == MhrStatusTypes.ACTIVE:
            description = desc
        elif not (current or registration.current_view) and desc.registration_id == registration.id:
            description = desc
    if not description and current and registration.change_registrations:
        for reg in registration.change_registrations:
            if reg.descriptions:
                desc = reg.descriptions[0]
                if desc.status_type == MhrStatusTypes.ACTIVE:
                    description = desc
    if description:
        description_json = description.json
        description_json['sections'] = get_sections_json(registration, description.registration_id)
        reg_json['description'] = description_json
    return reg_json


def set_group_json(registration, reg_json, current: bool) -> dict:
    """Build the owner group JSON conditional on current."""
    owner_groups = []
    if registration.owner_groups:
        for group in registration.owner_groups:
            if (current or registration.current_view) and group.status_type in (MhrOwnerStatusTypes.ACTIVE,
                                                                                MhrOwnerStatusTypes.EXEMPT):
                owner_groups.append(group.json)
            elif not (current or registration.current_view) and group.registration_id == registration.id:
                owner_groups.append(group.json)
    if current and registration.change_registrations:
        for reg in registration.change_registrations:
            if reg.owner_groups:
                for group in reg.owner_groups:
                    if group.status_type in (MhrOwnerStatusTypes.ACTIVE, MhrOwnerStatusTypes.EXEMPT):
                        owner_groups.append(group.json)
    reg_json['ownerGroups'] = owner_groups
    return reg_json


def set_transfer_group_json(registration, reg_json) -> dict:
    """Build the transfer registration owner groups JSON."""
    add_groups = []
    delete_groups = []
    if reg_json and registration.owner_groups:
        for group in registration.owner_groups:
            if group.registration_id == registration.id:
                add_groups.append(group.json)
            elif group.change_registration_id == registration.id:
                delete_groups.append(group.json)
    reg_json['addOwnerGroups'] = add_groups
    if registration.change_registrations:
        for reg in registration.change_registrations:
            for existing in reg.owner_groups:
                if existing.registration_id != registration.id and existing.change_registration_id == registration.id:
                    delete_groups.append(existing.json)
    reg_json['deleteOwnerGroups'] = delete_groups
    return reg_json


def update_notes_search_json(notes_json: dict, staff: bool) -> dict:
    """Build the search version of the registration as a json object."""
    if not notes_json:
        return notes_json
    updated_notes = []
    for note in notes_json:
        include: bool = True
        doc_type = note.get('documentType', '')
        if doc_type in ('REG_103', 'REG_103E', 'STAT', 'EXRE', 'NCAN'):  # Always exclude
            include = False
        elif not staff and doc_type in ('REG_102', 'NCON'):  # Always exclude for non-staff
            include = False
        elif not staff and doc_type == 'FZE':  # Only staff can see remarks.
            note['remarks'] = ''
        elif not staff and doc_type == 'REGC' and note.get('remarks') and \
                note['remarks'] != 'MANUFACTURED HOME REGISTRATION CANCELLED':
            # Only staff can see remarks if not default.
            note['remarks'] = 'MANUFACTURED HOME REGISTRATION CANCELLED'
        elif doc_type in ('TAXN', 'EXNR', 'EXRS', 'NPUB', 'REST', 'CAU', 'CAUC', 'CAUE') and \
                note.get('status') != MhrNoteStatusTypes.ACTIVE:  # Exclude if not active.
            include = False
        elif doc_type in ('CAU', 'CAUC', 'CAUE') and note.get('expiryDateTime') and \
                model_utils.date_elapsed(note.get('expiryDateTime')):  # Exclude if expiry elapsed.
            include = include_caution_note(notes_json, note.get('documentId'))
        if doc_type == 'FZE':  # Do not display contact info.
            if note.get('givingNoticeParty'):
                del note['givingNoticeParty']
        if include:
            updated_notes.append(note)
    return updated_notes


def get_notes_json(registration, search: bool, staff: bool = False):
    """Fetch all the unit notes for the manufactured home. Search has special conditions on what is included."""
    notes = []
    if not registration.change_registrations:
        return notes
    cancel_notes = []
    for reg in registration.change_registrations:
        if reg.notes and (not search or reg.notes[0].status_type == MhrNoteStatusTypes.ACTIVE):
            note = reg.notes[0]
            if note.document_type in (MhrDocumentTypes.NCAN, MhrDocumentTypes.NRED, MhrDocumentTypes.EXRE):
                cnote = find_cancelled_note(registration, note.registration_id)
                if cnote:
                    cancel_note = cnote.json
                    cancel_note['ncan'] = note.json
                    cancel_notes.append(cancel_note)
            notes.append(note)
    if not notes:
        return notes
    notes_json = []
    for note in reversed(notes):
        note_json = note.json
        if note_json.get('documentType') in (MhrDocumentTypes.NCAN, MhrDocumentTypes.NRED, MhrDocumentTypes.EXRE) and \
                cancel_notes:
            for cnote in cancel_notes:
                if cnote['ncan'].get('documentId') == note_json.get('documentId'):
                    note_json['cancelledDocumentType'] = cnote.get('documentType')
                    note_json['cancelledDocumentDescription'] = cnote.get('documentDescription')
                    note_json['cancelledDocumentRegistrationNumber'] = cnote.get('documentRegistrationNumber')
        notes_json.append(note_json)
    if search:
        return update_notes_search_json(notes_json, staff)
    return notes_json


def get_non_staff_notes_json(registration, search: bool):
    """Build the non-BC Registries staff version of the active unit notes as JSON."""
    if search:
        return get_notes_json(registration, search)
    notes = get_notes_json(registration, search)
    if not notes:
        return notes
    updated_notes = []
    for note in notes:
        include: bool = True
        doc_type = note.get('documentType', '')
        if doc_type in ('STAT', '102'):  # Always exclude for non-staff
            include = False
        elif doc_type in ('TAXN', 'EXNR', 'EXRS', 'NPUB', 'REST', 'CAU', 'CAUC', 'CAUE', 'NCON') and \
                note.get('status') != MhrNoteStatusTypes.ACTIVE:  # Exclude if not active.
            include = False
        elif doc_type in ('CAU', 'CAUC', 'CAUE') and note.get('expiryDateTime') and \
                model_utils.date_elapsed(note.get('expiryDateTime')):  # Exclude if expiry elapsed.
            include = include_caution_note(notes, note.get('documentId'))
        elif doc_type in ('REG_103', 'REG_103E') and note.get('expiryDateTime') and \
                model_utils.date_elapsed(note.get('expiryDateTime')):  # Exclude if expiry elapsed.
            include = False
        if include:
            minimal_note = {
                'createDateTime': note.get('createDateTime'),
                'documentType': doc_type,
                'documentDescription':  note.get('documentDescription'),
                'status': note.get('status', '')
            }
            if doc_type in ('REG_103', 'REG_103E') and note.get('expiryDateTime'):
                minimal_note['expiryDateTime'] = note.get('expiryDateTime')
            updated_notes.append(minimal_note)
    return updated_notes


def set_note_json(registration, reg_json) -> dict:
    """Build the note JSON for an individual registration that has a unit note."""
    if reg_json and registration.notes:  # pylint: disable=too-many-nested-blocks; only 1 more.
        reg_note = registration.notes[0].json
        if reg_note.get('documentType') in (MhrDocumentTypes.NCAN,
                                            MhrDocumentTypes.NRED,
                                            MhrDocumentTypes.EXRE):
            cnote: MhrNote = find_cancelled_note(registration, registration.id)
            if cnote:
                current_app.logger.debug(f'Found cancelled note {cnote.document_type}')
                cnote_json = cnote.json
                reg_note['cancelledDocumentType'] = cnote_json.get('documentType')
                reg_note['cancelledDocumentDescription'] = cnote_json.get('documentDescription')
                reg_note['cancelledDocumentRegistrationNumber'] = cnote_json.get('documentRegistrationNumber')
            elif model_utils.is_legacy() and registration.manuhome:
                doc_id: str = registration.documents[0].document_id
                for note in registration.manuhome.reg_notes:
                    if doc_id == note.can_document_id:
                        reg_note['cancelledDocumentType'] = note.document_type
                        reg_note['cancelledDocumentDescription'] = \
                            get_document_description(note.document_type)
                        for doc in registration.manuhome.reg_documents:
                            if doc.id == note.reg_document_id:
                                reg_note['cancelledDocumentRegistrationNumber'] = doc.document_reg_id

        reg_json['note'] = reg_note
    return reg_json
