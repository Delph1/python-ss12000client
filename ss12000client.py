"""
SS12000 Python Client Library.

This library provides functions to interact with the SS12000 API
based on the provided OpenAPI specification.
It includes basic HTTP calls and Bearer Token authentication handling.
"""

import requests
import json
from urllib.parse import urljoin

class SS12000Client:
    """
    SS12000 API Client.

    :param base_url: Base URL for the SS12000 API (e.g., "https://some.server.se/v2.0").
    :param auth_token: JWT Bearer Token for authentication.
    """
    def __init__(self, base_url: str, auth_token: str = None):
        if not base_url:
            raise ValueError('Base URL is mandatory for SS12000Client.')

        # Add HTTPS check for base_url
        if not base_url.startswith('https://'):
            print('Warning: Base URL does not use HTTPS. All communication should occur over HTTPS '
                  'in production environments to ensure security.')

        if not auth_token:
            print('Warning: Authentication token is missing. Calls may fail if the API requires authentication.')

        self.base_url = base_url
        self.headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json',
        }
        if auth_token:
            self.headers['Authorization'] = f'Bearer {auth_token}'

    def _request(self, method: str, path: str, params: dict = None, json_data: dict = None):
        """
        Performs a generic HTTP request to the API.
        :param method: HTTP method (GET, POST, DELETE, PATCH).
        :param path: API path (e.g., "/organisations").
        :param params: Query parameters.
        :param json_data: JSON request body.
        :return: Response from the API.
        :raises requests.exceptions.RequestException: If the request fails.
        """
        url = urljoin(self.base_url, path)
        try:
            response = requests.request(
                method,
                url,
                params=params,
                json=json_data,
                headers=self.headers,
                timeout=30 # Add a timeout for requests
            )
            response.raise_for_status()  # Raise HTTPError for bad responses (4xx or 5xx)
            if response.status_code == 204: # No Content
                return None
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Error during {method} call to {url}: {e}")
            if hasattr(e, 'response') and e.response is not None:
                try:
                    error_body = e.response.json()
                    print(f"API Error Response: {json.dumps(error_body, indent=2)}")
                except json.JSONDecodeError:
                    print(f"API Error Response (non-JSON): {e.response.text}")
            raise

    # --- Organisation Endpoints ---

    def get_organisations(self, **params):
        """
        Get a list of organizations.
        :param params: Filter parameters.
        :return: A list of organizations.
        """
        mapped_params = {
            'parent': params.get('parent'),
            'schoolUnitCode': params.get('school_unit_code'),
            'organisationCode': params.get('organisation_code'),
            'municipalityCode': params.get('municipality_code'),
            'type': params.get('type'),
            'schoolTypes': params.get('school_types'),
            'startDate.onOrBefore': params.get('start_date_on_or_before'),
            'startDate.onOrAfter': params.get('start_date_on_or_after'),
            'endDate.onOrBefore': params.get('end_date_on_or_before'),
            'endDate.onOrAfter': params.get('end_date_on_or_after'),
            'meta.created.before': params.get('meta_created_before'),
            'meta.created.after': params.get('meta_created_after'),
            'meta.modified.before': params.get('meta_modified_before'),
            'meta.modified.after': params.get('meta_modified_after'),
            'expandReferenceNames': params.get('expand_reference_names'),
            'sortkey': params.get('sortkey'),
            'limit': params.get('limit'),
            'pageToken': params.get('page_token'),
        }
        # Filter out None values from mapped_params
        filtered_params = {k: v for k, v in mapped_params.items() if v is not None}
        return self._request('GET', '/organisations', params=filtered_params)

    def lookup_organisations(self, ids: list = None, school_unit_codes: list = None,
                             organisation_codes: list = None, expand_reference_names: bool = False):
        """
        Get multiple organizations based on a list of IDs.
        :param ids: List of organization IDs.
        :param school_unit_codes: List of school unit codes.
        :param organisation_codes: List of organization codes.
        :param expand_reference_names: Return `displayName` for all referenced objects.
        :return: A list of organizations.
        """
        body = {}
        if ids:
            body['ids'] = ids
        if school_unit_codes:
            body['schoolUnitCodes'] = school_unit_codes
        if organisation_codes:
            body['organisationCodes'] = organisation_codes

        params = {'expandReferenceNames': expand_reference_names} if expand_reference_names else {}
        return self._request('POST', '/organisations/lookup', params=params, json_data=body)

    def get_organisation_by_id(self, org_id: str, expand_reference_names: bool = False):
        """
        Get an organization by ID.
        :param org_id: ID of the organization.
        :param expand_reference_names: Return `displayName` for all referenced objects.
        :return: The organization object.
        """
        params = {'expandReferenceNames': expand_reference_names} if expand_reference_names else {}
        return self._request('GET', f'/organisations/{org_id}', params=params)

    # --- Person Endpoints ---

    def get_persons(self, **params):
        """
        Get a list of persons.
        :param params: Filter parameters.
        :return: A list of persons.
        """
        mapped_params = {
            'nameContains': params.get('name_contains'),
            'civicNo': params.get('civic_no'),
            'eduPersonPrincipalName': params.get('edu_person_principal_name'),
            'identifier.value': params.get('identifier_value'),
            'identifier.context': params.get('identifier_context'),
            'relationship.entity.type': params.get('relationship_entity_type'),
            'relationship.organisation': params.get('relationship_organisation'),
            'relationship.startDate.onOrBefore': params.get('relationship_start_date_on_or_before'),
            'relationship.startDate.onOrAfter': params.get('relationship_start_date_on_or_after'),
            'relationship.endDate.onOrBefore': params.get('relationship_end_date_on_or_before'),
            'relationship.endDate.onOrAfter': params.get('relationship_end_date_on_or_after'),
            'meta.created.before': params.get('meta_created_before'),
            'meta.created.after': params.get('meta_created_after'),
            'meta.modified.before': params.get('meta_modified_before'),
            'meta.modified.after': params.get('meta_modified_after'),
            'expand': params.get('expand'),
            'expandReferenceNames': params.get('expand_reference_names'),
            'sortkey': params.get('sortkey'),
            'limit': params.get('limit'),
            'pageToken': params.get('page_token'),
        }
        filtered_params = {k: v for k, v in mapped_params.items() if v is not None}
        return self._request('GET', '/persons', params=filtered_params)

    def lookup_persons(self, ids: list = None, civic_nos: list = None, expand: list = None, expand_reference_names: bool = False):
        """
        Get multiple persons based on a list of IDs or civic numbers.
        :param ids: List of person IDs.
        :param civic_nos: List of civic numbers.
        :param expand: Describes if expanded data should be fetched.
        :param expand_reference_names: Return `displayName` for all referenced objects.
        :return: A list of persons.
        """
        body = {}
        if ids:
            body['ids'] = ids
        if civic_nos:
            body['civicNos'] = civic_nos

        params = {}
        if expand:
            params['expand'] = expand
        if expand_reference_names:
            params['expandReferenceNames'] = expand_reference_names

        return self._request('POST', '/persons/lookup', params=params, json_data=body)

    def get_person_by_id(self, person_id: str, expand: list = None, expand_reference_names: bool = False):
        """
        Get a person by person ID.
        :param person_id: ID of the person.
        :param expand: Describes if expanded data should be fetched.
        :param expand_reference_names: Return `displayName` for all referenced objects.
        :return: The person object.
        """
        params = {}
        if expand:
            params['expand'] = expand
        if expand_reference_names:
            params['expandReferenceNames'] = expand_reference_names
        return self._request('GET', f'/persons/{person_id}', params=params)

    # --- Placements Endpoints ---

    def get_placements(self, **params):
        """
        Get a list of placements.
        :param params: Filter parameters.
        :return: A list of placements.
        """
        mapped_params = {
            'child': params.get('child'),
            'group': params.get('group'),
            'owner': params.get('owner'),
            'placedAt': params.get('placed_at'),
            'schoolType': params.get('school_type'),
            'startDate.onOrBefore': params.get('start_date_on_or_before'),
            'startDate.onOrAfter': params.get('start_date_on_or_after'),
            'endDate.onOrBefore': params.get('end_date_on_or_before'),
            'endDate.onOrAfter': params.get('end_date_on_or_after'),
            'meta.created.before': params.get('meta_created_before'),
            'meta.created.after': params.get('meta_created_after'),
            'meta.modified.before': params.get('meta_modified_before'),
            'meta.modified.after': params.get('meta_modified_after'),
            'expand': params.get('expand'),
            'expandReferenceNames': params.get('expand_reference_names'),
            'sortkey': params.get('sortkey'),
            'limit': params.get('limit'),
            'pageToken': params.get('page_token'),
        }
        filtered_params = {k: v for k, v in mapped_params.items() if v is not None}
        return self._request('GET', '/placements', params=filtered_params)

    def lookup_placements(self, ids: list = None, expand: list = None, expand_reference_names: bool = False):
        """
        Get multiple placements based on a list of IDs.
        :param ids: List of placement IDs.
        :param expand: Describes if expanded data should be fetched.
        :param expand_reference_names: Return `displayName` for all referenced objects.
        :return: A list of placements.
        """
        body = {'ids': ids} if ids else {}
        params = {}
        if expand:
            params['expand'] = expand
        if expand_reference_names:
            params['expandReferenceNames'] = expand_reference_names
        return self._request('POST', '/placements/lookup', params=params, json_data=body)

    def get_placement_by_id(self, placement_id: str, expand: list = None, expand_reference_names: bool = False):
        """
        Get a placement by ID.
        :param placement_id: ID of the placement.
        :param expand: Describes if expanded data should be fetched.
        :param expand_reference_names: Return `displayName` for all referenced objects.
        :return: The placement object.
        """
        params = {}
        if expand:
            params['expand'] = expand
        if expand_reference_names:
            params['expandReferenceNames'] = expand_reference_names
        return self._request('GET', f'/placements/{placement_id}', params=params)

    # --- Duties Endpoints ---

    def get_duties(self, **params):
        """
        Get a list of duties.
        :param params: Filter parameters.
        :return: A list of duties.
        """
        mapped_params = {
            'person': params.get('person'),
            'dutyAt': params.get('duty_at'),
            'dutyRole': params.get('duty_role'),
            'signature': params.get('signature'),
            'startDate.onOrBefore': params.get('start_date_on_or_before'),
            'startDate.onOrAfter': params.get('start_date_on_or_after'),
            'endDate.onOrBefore': params.get('end_date_on_or_before'),
            'endDate.onOrAfter': params.get('end_date_on_or_after'),
            'meta.created.before': params.get('meta_created_before'),
            'meta.created.after': params.get('meta_created_after'),
            'meta.modified.before': params.get('meta_modified_before'),
            'meta.modified.after': params.get('meta_modified_after'),
            'expand': params.get('expand'),
            'expandReferenceNames': params.get('expand_reference_names'),
            'sortkey': params.get('sortkey'),
            'limit': params.get('limit'),
            'pageToken': params.get('page_token'),
        }
        filtered_params = {k: v for k, v in mapped_params.items() if v is not None}
        return self._request('GET', '/duties', params=filtered_params)

    def lookup_duties(self, ids: list = None, expand: list = None, expand_reference_names: bool = False):
        """
        Get multiple duties based on a list of IDs.
        :param ids: List of duty IDs.
        :param expand: Describes if expanded data should be fetched.
        :param expand_reference_names: Return `displayName` for all referenced objects.
        :return: A list of duties.
        """
        body = {'ids': ids} if ids else {}
        params = {}
        if expand:
            params['expand'] = expand
        if expand_reference_names:
            params['expandReferenceNames'] = expand_reference_names
        return self._request('POST', '/duties/lookup', params=params, json_data=body)

    def get_duty_by_id(self, duty_id: str, expand: list = None, expand_reference_names: bool = False):
        """
        Get a duty by ID.
        :param duty_id: ID of the duty.
        :param expand: Describes if expanded data should be fetched.
        :param expand_reference_names: Return `displayName` for all referenced objects.
        :return: The duty object.
        """
        params = {}
        if expand:
            params['expand'] = expand
        if expand_reference_names:
            params['expandReferenceNames'] = expand_reference_names
        return self._request('GET', f'/duties/{duty_id}', params=params)

    # --- Groups Endpoints ---

    def get_groups(self, **params):
        """
        Get a list of groups.
        :param params: Filter parameters.
        :return: A list of groups.
        """
        mapped_params = {
            'groupType': params.get('group_type'),
            'schoolType': params.get('school_type'),
            'organisation': params.get('organisation'),
            'startDate.onOrBefore': params.get('start_date_on_or_before'),
            'startDate.onOrAfter': params.get('start_date_on_or_after'),
            'endDate.onOrBefore': params.get('end_date_on_or_before'),
            'endDate.onOrAfter': params.get('end_date_on_or_after'),
            'meta.created.before': params.get('meta_created_before'),
            'meta.created.after': params.get('meta_created_after'),
            'meta.modified.before': params.get('meta_modified_before'),
            'meta.modified.after': params.get('meta_modified_after'),
            'expand': params.get('expand'),
            'expandReferenceNames': params.get('expand_reference_names'),
            'sortkey': params.get('sortkey'),
            'limit': params.get('limit'),
            'pageToken': params.get('page_token'),
        }
        filtered_params = {k: v for k, v in mapped_params.items() if v is not None}
        return self._request('GET', '/groups', params=filtered_params)

    def lookup_groups(self, ids: list = None, expand: list = None, expand_reference_names: bool = False):
        """
        Get multiple groups based on a list of IDs.
        :param ids: List of group IDs.
        :param expand: Describes if expanded data should be fetched.
        :param expand_reference_names: Return `displayName` for all referenced objects.
        :return: A list of groups.
        """
        body = {'ids': ids} if ids else {}
        params = {}
        if expand:
            params['expand'] = expand
        if expand_reference_names:
            params['expandReferenceNames'] = expand_reference_names
        return self._request('POST', '/groups/lookup', params=params, json_data=body)

    def get_group_by_id(self, group_id: str, expand: list = None, expand_reference_names: bool = False):
        """
        Get a group by ID.
        :param group_id: ID of the group.
        :param expand: Describes if expanded data should be fetched.
        :param expand_reference_names: Return `displayName` for all referenced objects.
        :return: The group object.
        """
        params = {}
        if expand:
            params['expand'] = expand
        if expand_reference_names:
            params['expandReferenceNames'] = expand_reference_names
        return self._request('GET', f'/groups/{group_id}', params=params)

    # --- Programmes Endpoints ---

    def get_programmes(self, **params):
        """
        Get a list of programmes.
        :param params: Filter parameters.
        :return: A list of programmes.
        """
        mapped_params = {
            'nameContains': params.get('name_contains'),
            'type': params.get('type'),
            'parentProgramme': params.get('parent_programme'),
            'schoolType': params.get('school_type'),
            'code': params.get('code'),
            'meta.created.before': params.get('meta_created_before'),
            'meta.created.after': params.get('meta_created_after'),
            'meta.modified.before': params.get('meta_modified_before'),
            'meta.modified.after': params.get('meta_modified_after'),
            'expand': params.get('expand'),
            'expandReferenceNames': params.get('expand_reference_names'),
            'sortkey': params.get('sortkey'),
            'limit': params.get('limit'),
            'pageToken': params.get('page_token'),
        }
        filtered_params = {k: v for k, v in mapped_params.items() if v is not None}
        return self._request('GET', '/programmes', params=filtered_params)

    def lookup_programmes(self, ids: list = None, expand: list = None, expand_reference_names: bool = False):
        """
        Get multiple programmes based on a list of IDs.
        :param ids: List of programme IDs.
        :param expand: Describes if expanded data should be fetched.
        :param expand_reference_names: Return `displayName` for all referenced objects.
        :return: A list of programmes.
        """
        body = {'ids': ids} if ids else {}
        params = {}
        if expand:
            params['expand'] = expand
        if expand_reference_names:
            params['expandReferenceNames'] = expand_reference_names
        return self._request('POST', '/programmes/lookup', params=params, json_data=body)

    def get_programme_by_id(self, programme_id: str, expand: list = None, expand_reference_names: bool = False):
        """
        Get a programme by ID.
        :param programme_id: ID of the programme.
        :param expand: Describes if expanded data should be fetched.
        :param expand_reference_names: Return `displayName` for all referenced objects.
        :return: The programme object.
        """
        params = {}
        if expand:
            params['expand'] = expand
        if expand_reference_names:
            params['expandReferenceNames'] = expand_reference_names
        return self._request('GET', f'/programmes/{programme_id}', params=params)

    # --- StudyPlans Endpoints ---

    def get_study_plans(self, **params):
        """
        Get a list of study plans.
        :param params: Filter parameters.
        :return: A list of study plans.
        """
        mapped_params = {
            'student': params.get('student'),
            'startDate.onOrBefore': params.get('start_date_on_or_before'),
            'startDate.onOrAfter': params.get('start_date_on_or_after'),
            'endDate.onOrBefore': params.get('end_date_on_or_before'),
            'endDate.onOrAfter': params.get('end_date_on_or_after'),
            'meta.created.before': params.get('meta_created_before'),
            'meta.created.after': params.get('meta_created_after'),
            'meta.modified.before': params.get('meta_modified_before'),
            'meta.modified.after': params.get('meta_modified_after'),
            'expand': params.get('expand'),
            'expandReferenceNames': params.get('expand_reference_names'),
            'sortkey': params.get('sortkey'),
            'limit': params.get('limit'),
            'pageToken': params.get('page_token'),
        }
        filtered_params = {k: v for k, v in mapped_params.items() if v is not None}
        return self._request('GET', '/studyplans', params=filtered_params)

    def lookup_study_plans(self, ids: list = None, expand: list = None, expand_reference_names: bool = False):
        """
        Get multiple study plans based on a list of IDs.
        :param ids: List of study plan IDs.
        :param expand: Describes if expanded data should be fetched.
        :param expand_reference_names: Return `displayName` for all referenced objects.
        :return: A list of study plans.
        """
        body = {'ids': ids} if ids else {}
        params = {}
        if expand:
            params['expand'] = expand
        if expand_reference_names:
            params['expandReferenceNames'] = expand_reference_names
        return self._request('POST', '/studyplans/lookup', params=params, json_data=body)

    def get_study_plan_by_id(self, study_plan_id: str, expand: list = None, expand_reference_names: bool = False):
        """
        Get a study plan by ID.
        :param study_plan_id: ID of the study plan.
        :param expand: Describes if expanded data should be fetched.
        :param expand_reference_names: Return `displayName` for all referenced objects.
        :return: The study plan object.
        """
        params = {}
        if expand:
            params['expand'] = expand
        if expand_reference_names:
            params['expandReferenceNames'] = expand_reference_names
        return self._request('GET', f'/studyplans/{study_plan_id}', params=params)

    # --- Syllabuses Endpoints ---

    def get_syllabuses(self, **params):
        """
        Get a list of syllabuses.
        :param params: Filter parameters.
        :return: A list of syllabuses.
        """
        mapped_params = {
            'schoolType': params.get('school_type'),
            'subjectCode': params.get('subject_code'),
            'subjectNameContains': params.get('subject_name_contains'),
            'subjectDesignation': params.get('subject_designation'),
            'courseCode': params.get('course_code'),
            'courseNameContains': params.get('course_name_contains'),
            'startSchoolYear.onOrBefore': params.get('start_school_year_on_or_before'),
            'startSchoolYear.onOrAfter': params.get('start_school_year_on_or_after'),
            'endSchoolYear.onOrBefore': params.get('end_school_year_on_or_before'),
            'endSchoolYear.onOrAfter': params.get('end_school_year_on_or_after'),
            'points.onOrBefore': params.get('points_on_or_before'),
            'points.onOrAfter': params.get('points_on_or_after'),
            'curriculum': params.get('curriculum'),
            'languageCode': params.get('language_code'),
            'official': params.get('official'),
            'meta.created.before': params.get('meta_created_before'),
            'meta.created.after': params.get('meta_created_after'),
            'meta.modified.before': params.get('meta_modified_before'),
            'meta.modified.after': params.get('meta_modified_after'),
            'expandReferenceNames': params.get('expand_reference_names'),
            'sortkey': params.get('sortkey'),
            'limit': params.get('limit'),
            'pageToken': params.get('page_token'),
        }
        filtered_params = {k: v for k, v in mapped_params.items() if v is not None}
        return self._request('GET', '/syllabuses', params=filtered_params)

    def lookup_syllabuses(self, ids: list = None, expand_reference_names: bool = False):
        """
        Get multiple syllabuses based on a list of IDs.
        :param ids: List of syllabus IDs.
        :param expand_reference_names: Return `displayName` for all referenced objects.
        :return: A list of syllabuses.
        """
        body = {'ids': ids} if ids else {}
        params = {'expandReferenceNames': expand_reference_names} if expand_reference_names else {}
        return self._request('POST', '/syllabuses/lookup', params=params, json_data=body)

    def get_syllabus_by_id(self, syllabus_id: str, expand_reference_names: bool = False):
        """
        Get a syllabus by ID.
        :param syllabus_id: ID of the syllabus.
        :param expand_reference_names: Return `displayName` for all referenced objects.
        :return: The syllabus object.
        """
        params = {'expandReferenceNames': expand_reference_names} if expand_reference_names else {}
        return self._request('GET', f'/syllabuses/{syllabus_id}', params=params)

    # --- SchoolUnitOfferings Endpoints ---

    def get_school_unit_offerings(self, **params):
        """
        Get a list of school unit offerings.
        :param params: Filter parameters.
        :return: A list of school unit offerings.
        """
        mapped_params = {
            'offeredAt': params.get('offered_at'),
            'offeredSyllabuses': params.get('offered_syllabuses'),
            'offeredProgrammes': params.get('offered_programmes'),
            'startDate.onOrBefore': params.get('start_date_on_or_before'),
            'startDate.onOrAfter': params.get('start_date_on_or_after'),
            'endDate.onOrBefore': params.get('end_date_on_or_before'),
            'endDate.onOrAfter': params.get('end_date_on_or_after'),
            'meta.created.before': params.get('meta_created_before'),
            'meta.created.after': params.get('meta_created_after'),
            'meta.modified.before': params.get('meta_modified_before'),
            'meta.modified.after': params.get('meta_modified_after'),
            'expand': params.get('expand'),
            'expandReferenceNames': params.get('expand_reference_names'),
            'sortkey': params.get('sortkey'),
            'limit': params.get('limit'),
            'pageToken': params.get('page_token'),
        }
        filtered_params = {k: v for k, v in mapped_params.items() if v is not None}
        return self._request('GET', '/schoolUnitOfferings', params=filtered_params)

    def lookup_school_unit_offerings(self, ids: list = None, expand: list = None, expand_reference_names: bool = False):
        """
        Get multiple school unit offerings based on a list of IDs.
        :param ids: List of school unit offering IDs.
        :param expand: Describes if expanded data should be fetched.
        :param expand_reference_names: Return `displayName` for all referenced objects.
        :return: A list of school unit offerings.
        """
        body = {'ids': ids} if ids else {}
        params = {}
        if expand:
            params['expand'] = expand
        if expand_reference_names:
            params['expandReferenceNames'] = expand_reference_names
        return self._request('POST', '/schoolUnitOfferings/lookup', params=params, json_data=body)

    def get_school_unit_offering_by_id(self, offering_id: str, expand: list = None, expand_reference_names: bool = False):
        """
        Get a school unit offering by ID.
        :param offering_id: ID of the school unit offering.
        :param expand: Describes if expanded data should be fetched.
        :param expand_reference_names: Return `displayName` for all referenced objects.
        :return: The school unit offering object.
        """
        params = {}
        if expand:
            params['expand'] = expand
        if expand_reference_names:
            params['expandReferenceNames'] = expand_reference_names
        return self._request('GET', f'/schoolUnitOfferings/{offering_id}', params=params)

    # --- Activities Endpoints ---

    def get_activities(self, **params):
        """
        Get a list of activities.
        :param params: Filter parameters.
        :return: A list of activities.
        """
        mapped_params = {
            'organisation': params.get('organisation'),
            'syllabus': params.get('syllabus'),
            'activityType': params.get('activity_type'),
            'calendarEventsRequired': params.get('calendar_events_required'),
            'startDate.onOrBefore': params.get('start_date_on_or_before'),
            'startDate.onOrAfter': params.get('start_date_on_or_after'),
            'endDate.onOrBefore': params.get('end_date_on_or_before'),
            'endDate.onOrAfter': params.get('end_date_on_or_after'),
            'meta.created.before': params.get('meta_created_before'),
            'meta.created.after': params.get('meta_created_after'),
            'meta.modified.before': params.get('meta_modified_before'),
            'meta.modified.after': params.get('meta_modified_after'),
            'expand': params.get('expand'),
            'expandReferenceNames': params.get('expand_reference_names'),
            'sortkey': params.get('sortkey'),
            'limit': params.get('limit'),
            'pageToken': params.get('page_token'),
        }
        filtered_params = {k: v for k, v in mapped_params.items() if v is not None}
        return self._request('GET', '/activities', params=filtered_params)

    def lookup_activities(self, ids: list = None, expand: list = None, expand_reference_names: bool = False):
        """
        Get multiple activities based on a list of IDs.
        :param ids: List of activity IDs.
        :param expand: Describes if expanded data should be fetched.
        :param expand_reference_names: Return `displayName` for all referenced objects.
        :return: A list of activities.
        """
        body = {'ids': ids} if ids else {}
        params = {}
        if expand:
            params['expand'] = expand
        if expand_reference_names:
            params['expandReferenceNames'] = expand_reference_names
        return self._request('POST', '/activities/lookup', params=params, json_data=body)

    def get_activity_by_id(self, activity_id: str, expand: list = None, expand_reference_names: bool = False):
        """
        Get an activity by ID.
        :param activity_id: ID of the activity.
        :param expand: Describes if expanded data should be fetched.
        :param expand_reference_names: Return `displayName` for all referenced objects.
        :return: The activity object.
        """
        params = {}
        if expand:
            params['expand'] = expand
        if expand_reference_names:
            params['expandReferenceNames'] = expand_reference_names
        return self._request('GET', f'/activities/{activity_id}', params=params)

    # --- CalendarEvents Endpoints ---

    def get_calendar_events(self, **params):
        """
        Get a list of calendar events.
        :param params: Filter parameters.
        :return: A list of calendar events.
        """
        mapped_params = {
            'activity': params.get('activity'),
            'startTime.onOrBefore': params.get('start_time_on_or_before'),
            'startTime.onOrAfter': params.get('start_time_on_or_after'),
            'endTime.onOrBefore': params.get('end_time_on_or_before'),
            'endTime.onOrAfter': params.get('end_time_on_or_after'),
            'cancelled': params.get('cancelled'),
            'room': params.get('room'),
            'resource': params.get('resource'),
            'meta.created.before': params.get('meta_created_before'),
            'meta.created.after': params.get('meta_created_after'),
            'meta.modified.before': params.get('meta_modified_before'),
            'meta.modified.after': params.get('meta_modified_after'),
            'expand': params.get('expand'),
            'expandReferenceNames': params.get('expand_reference_names'),
            'sortkey': params.get('sortkey'),
            'limit': params.get('limit'),
            'pageToken': params.get('page_token'),
        }
        filtered_params = {k: v for k, v in mapped_params.items() if v is not None}
        return self._request('GET', '/calendarEvents', params=filtered_params)

    def lookup_calendar_events(self, ids: list = None, expand: list = None, expand_reference_names: bool = False):
        """
        Get multiple calendar events based on a list of IDs.
        :param ids: List of calendar event IDs.
        :param expand: Describes if expanded data should be fetched.
        :param expand_reference_names: Return `displayName` for all referenced objects.
        :return: A list of calendar events.
        """
        body = {'ids': ids} if ids else {}
        params = {}
        if expand:
            params['expand'] = expand
        if expand_reference_names:
            params['expandReferenceNames'] = expand_reference_names
        return self._request('POST', '/calendarEvents/lookup', params=params, json_data=body)

    def get_calendar_event_by_id(self, event_id: str, expand: list = None, expand_reference_names: bool = False):
        """
        Get a calendar event by ID.
        :param event_id: ID of the calendar event.
        :param expand: Describes if expanded data should be fetched.
        :param expand_reference_names: Return `displayName` for all referenced objects.
        :return: The calendar event object.
        """
        params = {}
        if expand:
            params['expand'] = expand
        if expand_reference_names:
            params['expandReferenceNames'] = expand_reference_names
        return self._request('GET', f'/calendarEvents/{event_id}', params=params)

    # --- Attendances Endpoints ---

    def get_attendances(self, **params):
        """
        Get a list of attendances.
        :param params: Filter parameters.
        :return: A list of attendances.
        """
        mapped_params = {
            'calendarEvent': params.get('calendar_event'),
            'student': params.get('student'),
            'reporter': params.get('reporter'),
            'isReported': params.get('is_reported'),
            'reportedTimestamp.onOrBefore': params.get('reported_timestamp_on_or_before'),
            'reportedTimestamp.onOrAfter': params.get('reported_timestamp_on_or_after'),
            'meta.created.before': params.get('meta_created_before'),
            'meta.created.after': params.get('meta_created_after'),
            'meta.modified.before': params.get('meta_modified_before'),
            'meta.modified.after': params.get('meta_modified_after'),
            'expand': params.get('expand'),
            'expandReferenceNames': params.get('expand_reference_names'),
            'sortkey': params.get('sortkey'),
            'limit': params.get('limit'),
            'pageToken': params.get('page_token'),
        }
        filtered_params = {k: v for k, v in mapped_params.items() if v is not None}
        return self._request('GET', '/attendances', params=filtered_params)

    def lookup_attendances(self, ids: list = None, expand: list = None, expand_reference_names: bool = False):
        """
        Get multiple attendances based on a list of IDs.
        :param ids: List of attendance IDs.
        :param expand: Describes if expanded data should be fetched.
        :param expand_reference_names: Return `displayName` for all referenced objects.
        :return: A list of attendances.
        """
        body = {'ids': ids} if ids else {}
        params = {}
        if expand:
            params['expand'] = expand
        if expand_reference_names:
            params['expandReferenceNames'] = expand_reference_names
        return self._request('POST', '/attendances/lookup', params=params, json_data=body)

    def get_attendance_by_id(self, attendance_id: str, expand: list = None, expand_reference_names: bool = False):
        """
        Get an attendance by ID.
        :param attendance_id: ID of the attendance.
        :param expand: Describes if expanded data should be fetched.
        :param expand_reference_names: Return `displayName` for all referenced objects.
        :return: The attendance object.
        """
        params = {}
        if expand:
            params['expand'] = expand
        if expand_reference_names:
            params['expandReferenceNames'] = expand_reference_names
        return self._request('GET', f'/attendances/{attendance_id}', params=params)

    def delete_attendance(self, attendance_id: str):
        """
        Delete an attendance by ID.
        :param attendance_id: ID of the attendance to delete.
        """
        return self._request('DELETE', f'/attendances/{attendance_id}')

    # --- AttendanceEvents Endpoints ---

    def get_attendance_events(self, **params):
        """
        Get a list of attendance events.
        :param params: Filter parameters.
        :return: A list of attendance events.
        """
        mapped_params = {
            'person': params.get('person'),
            'registeredBy': params.get('registered_by'),
            'group': params.get('group'),
            'room': params.get('room'),
            'time.onOrBefore': params.get('time_on_or_before'),
            'time.onOrAfter': params.get('time_on_or_after'),
            'eventType': params.get('event_type'),
            'meta.created.before': params.get('meta_created_before'),
            'meta.created.after': params.get('meta_created_after'),
            'meta.modified.before': params.get('meta_modified_before'),
            'meta.modified.after': params.get('meta_modified_after'),
            'expand': params.get('expand'),
            'expandReferenceNames': params.get('expand_reference_names'),
            'sortkey': params.get('sortkey'),
            'limit': params.get('limit'),
            'pageToken': params.get('page_token'),
        }
        filtered_params = {k: v for k, v in mapped_params.items() if v is not None}
        return self._request('GET', '/attendanceEvents', params=filtered_params)

    def lookup_attendance_events(self, ids: list = None, expand: list = None, expand_reference_names: bool = False):
        """
        Get multiple attendance events based on a list of IDs.
        :param ids: List of attendance event IDs.
        :param expand: Describes if expanded data should be fetched.
        :param expand_reference_names: Return `displayName` for all referenced objects.
        :return: A list of attendance events.
        """
        body = {'ids': ids} if ids else {}
        params = {}
        if expand:
            params['expand'] = expand
        if expand_reference_names:
            params['expandReferenceNames'] = expand_reference_names
        return self._request('POST', '/attendanceEvents/lookup', params=params, json_data=body)

    def get_attendance_event_by_id(self, event_id: str, expand: list = None, expand_reference_names: bool = False):
        """
        Get an attendance event by ID.
        :param event_id: ID of the attendance event.
        :param expand: Describes if expanded data should be fetched.
        :param expand_reference_names: Return `displayName` for all referenced objects.
        :return: The attendance event object.
        """
        params = {}
        if expand:
            params['expand'] = expand
        if expand_reference_names:
            params['expandReferenceNames'] = expand_reference_names
        return self._request('GET', f'/attendanceEvents/{event_id}', params=params)

    # --- AttendanceSchedules Endpoints ---

    def get_attendance_schedules(self, **params):
        """
        Get a list of attendance schedules.
        :param params: Filter parameters.
        :return: A list of attendance schedules.
        """
        mapped_params = {
            'placement': params.get('placement'),
            'numberOfWeeks.onOrBefore': params.get('number_of_weeks_on_or_before'),
            'numberOfWeeks.onOrAfter': params.get('number_of_weeks_on_or_after'),
            'startDate.onOrBefore': params.get('start_date_on_or_before'),
            'startDate.onOrAfter': params.get('start_date_on_or_after'),
            'endDate.onOrBefore': params.get('end_date_on_or_before'),
            'endDate.onOrAfter': params.get('end_date_on_or_after'),
            'temporary': params.get('temporary'),
            'state': params.get('state'),
            'meta.created.before': params.get('meta_created_before'),
            'meta.created.after': params.get('meta_created_after'),
            'meta.modified.before': params.get('meta_modified_before'),
            'meta.modified.after': params.get('meta_modified_after'),
            'expand': params.get('expand'),
            'expandReferenceNames': params.get('expand_reference_names'),
            'sortkey': params.get('sortkey'),
            'limit': params.get('limit'),
            'pageToken': params.get('page_token'),
        }
        filtered_params = {k: v for k, v in mapped_params.items() if v is not None}
        return self._request('GET', '/attendanceSchedules', params=filtered_params)

    def lookup_attendance_schedules(self, ids: list = None, expand: list = None, expand_reference_names: bool = False):
        """
        Get multiple attendance schedules based on a list of IDs.
        :param ids: List of attendance schedule IDs.
        :param expand: Describes if expanded data should be fetched.
        :param expand_reference_names: Return `displayName` for all referenced objects.
        :return: A list of attendance schedules.
        """
        body = {'ids': ids} if ids else {}
        params = {}
        if expand:
            params['expand'] = expand
        if expand_reference_names:
            params['expandReferenceNames'] = expand_reference_names
        return self._request('POST', '/attendanceSchedules/lookup', params=params, json_data=body)

    def get_attendance_schedule_by_id(self, schedule_id: str, expand: list = None, expand_reference_names: bool = False):
        """
        Get an attendance schedule by ID.
        :param schedule_id: ID of the attendance schedule.
        :param expand: Describes if expanded data should be fetched.
        :param expand_reference_names: Return `displayName` for all referenced objects.
        :return: The attendance schedule object.
        """
        params = {}
        if expand:
            params['expand'] = expand
        if expand_reference_names:
            params['expandReferenceNames'] = expand_reference_names
        return self._request('GET', f'/attendanceSchedules/{schedule_id}', params=params)

    # --- Grades Endpoints ---

    def get_grades(self, **params):
        """
        Get a list of grades.
        :param params: Filter parameters.
        :return: A list of grades.
        """
        mapped_params = {
            'student': params.get('student'),
            'schoolUnit': params.get('school_unit'),
            'registeredBy': params.get('registered_by'),
            'gradingTeacher': params.get('grading_teacher'),
            'group': params.get('group'),
            'registeredDate.onOrBefore': params.get('registered_date_on_or_before'),
            'registeredDate.onOrAfter': params.get('registered_date_on_or_after'),
            'gradeValue': params.get('grade_value'),
            'finalGrade': params.get('final_grade'),
            'trial': params.get('trial'),
            'adaptedStudyPlan': params.get('adapted_study_plan'),
            'correctionType': params.get('correction_type'),
            'converted': params.get('converted'),
            'semester': params.get('semester'),
            'year.onOrBefore': params.get('year_on_or_before'),
            'year.onOrAfter': params.get('year_on_or_after'),
            'syllabus': params.get('syllabus'),
            'meta.created.before': params.get('meta_created_before'),
            'meta.created.after': params.get('meta_created_after'),
            'meta.modified.before': params.get('meta_modified_before'),
            'meta.modified.after': params.get('meta_modified_after'),
            'expand': params.get('expand'),
            'expandReferenceNames': params.get('expand_reference_names'),
            'sortkey': params.get('sortkey'),
            'limit': params.get('limit'),
            'pageToken': params.get('page_token'),
        }
        filtered_params = {k: v for k, v in mapped_params.items() if v is not None}
        return self._request('GET', '/grades', params=filtered_params)

    def lookup_grades(self, ids: list = None, expand: list = None, expand_reference_names: bool = False):
        """
        Get multiple grades based on a list of IDs.
        :param ids: List of grade IDs.
        :param expand: Describes if expanded data should be fetched.
        :param expand_reference_names: Return `displayName` for all referenced objects.
        :return: A list of grades.
        """
        body = {'ids': ids} if ids else {}
        params = {}
        if expand:
            params['expand'] = expand
        if expand_reference_names:
            params['expandReferenceNames'] = expand_reference_names
        return self._request('POST', '/grades/lookup', params=params, json_data=body)

    def get_grade_by_id(self, grade_id: str, expand: list = None, expand_reference_names: bool = False):
        """
        Get a grade by ID.
        :param grade_id: ID of the grade.
        :param expand: Describes if expanded data should be fetched.
        :param expand_reference_names: Return `displayName` for all referenced objects.
        :return: The grade object.
        """
        params = {}
        if expand:
            params['expand'] = expand
        if expand_reference_names:
            params['expandReferenceNames'] = expand_reference_names
        return self._request('GET', f'/grades/{grade_id}', params=params)

    # --- AggregatedAttendance Endpoints ---

    def get_aggregated_attendances(self, **params):
        """
        Get a list of aggregated attendances.
        :param params: Filter parameters.
        :return: A list of aggregated attendances.
        """
        mapped_params = {
            'activity': params.get('activity'),
            'student': params.get('student'),
            'startDate.onOrBefore': params.get('start_date_on_or_before'),
            'startDate.onOrAfter': params.get('start_date_on_or_after'),
            'endDate.onOrBefore': params.get('end_date_on_or_before'),
            'endDate.onOrAfter': params.get('end_date_on_or_after'),
            'meta.created.before': params.get('meta_created_before'),
            'meta.created.after': params.get('meta_created_after'),
            'meta.modified.before': params.get('meta_modified_before'),
            'meta.modified.after': params.get('meta_modified_after'),
            'expand': params.get('expand'),
            'expandReferenceNames': params.get('expand_reference_names'),
            'sortkey': params.get('sortkey'),
            'limit': params.get('limit'),
            'pageToken': params.get('page_token'),
        }
        filtered_params = {k: v for k, v in mapped_params.items() if v is not None}
        return self._request('GET', '/aggregatedAttendance', params=filtered_params)

    def lookup_aggregated_attendances(self, ids: list = None, expand: list = None, expand_reference_names: bool = False):
        """
        Get multiple aggregated attendances based on a list of IDs.
        :param ids: List of aggregated attendance IDs.
        :param expand: Describes if expanded data should be fetched.
        :param expand_reference_names: Return `displayName` for all referenced objects.
        :return: A list of aggregated attendances.
        """
        body = {'ids': ids} if ids else {}
        params = {}
        if expand:
            params['expand'] = expand
        if expand_reference_names:
            params['expandReferenceNames'] = expand_reference_names
        return self._request('POST', '/aggregatedAttendance/lookup', params=params, json_data=body)

    def get_aggregated_attendance_by_id(self, attendance_id: str, expand: list = None, expand_reference_names: bool = False):
        """
        Get an aggregated attendance by ID.
        :param attendance_id: ID of the aggregated attendance.
        :param expand: Describes if expanded data should be fetched.
        :param expand_reference_names: Return `displayName` for all referenced objects.
        :return: The aggregated attendance object.
        """
        params = {}
        if expand:
            params['expand'] = expand
        if expand_reference_names:
            params['expandReferenceNames'] = expand_reference_names
        return self._request('GET', f'/aggregatedAttendance/{attendance_id}', params=params)

    # --- Resources Endpoints ---

    def get_resources(self, **params):
        """
        Get a list of resources.
        :param params: Filter parameters.
        :return: A list of resources.
        """
        mapped_params = {
            'owner': params.get('owner'),
            'nameContains': params.get('name_contains'),
            'meta.created.before': params.get('meta_created_before'),
            'meta.created.after': params.get('meta_created_after'),
            'meta.modified.before': params.get('meta_modified_before'),
            'meta.modified.after': params.get('meta_modified_after'),
            'expandReferenceNames': params.get('expand_reference_names'),
            'sortkey': params.get('sortkey'),
            'limit': params.get('limit'),
            'pageToken': params.get('page_token'),
        }
        filtered_params = {k: v for k, v in mapped_params.items() if v is not None}
        return self._request('GET', '/resources', params=filtered_params)

    def lookup_resources(self, ids: list = None, expand_reference_names: bool = False):
        """
        Get multiple resources based on a list of IDs.
        :param ids: List of resource IDs.
        :param expand_reference_names: Return `displayName` for all referenced objects.
        :return: A list of resources.
        """
        body = {'ids': ids} if ids else {}
        params = {'expandReferenceNames': expand_reference_names} if expand_reference_names else {}
        return self._request('POST', '/resources/lookup', params=params, json_data=body)

    def get_resource_by_id(self, resource_id: str, expand_reference_names: bool = False):
        """
        Get a resource by ID.
        :param resource_id: ID of the resource.
        :param expand_reference_names: Return `displayName` for all referenced objects.
        :return: The resource object.
        """
        params = {'expandReferenceNames': expand_reference_names} if expand_reference_names else {}
        return self._request('GET', f'/resources/{resource_id}', params=params)

    # --- Rooms Endpoints ---

    def get_rooms(self, **params):
        """
        Get a list of rooms.
        :param params: Filter parameters.
        :return: A list of rooms.
        """
        mapped_params = {
            'owner': params.get('owner'),
            'nameContains': params.get('name_contains'),
            'meta.created.before': params.get('meta_created_before'),
            'meta.created.after': params.get('meta_created_after'),
            'meta.modified.before': params.get('meta_modified_before'),
            'meta.modified.after': params.get('meta_modified_after'),
            'expandReferenceNames': params.get('expand_reference_names'),
            'sortkey': params.get('sortkey'),
            'limit': params.get('limit'),
            'pageToken': params.get('page_token'),
        }
        filtered_params = {k: v for k, v in mapped_params.items() if v is not None}
        return self._request('GET', '/rooms', params=filtered_params)

    def lookup_rooms(self, ids: list = None, expand_reference_names: bool = False):
        """
        Get multiple rooms based on a list of IDs.
        :param ids: List of room IDs.
        :param expand_reference_names: Return `displayName` for all referenced objects.
        :return: A list of rooms.
        """
        body = {'ids': ids} if ids else {}
        params = {'expandReferenceNames': expand_reference_names} if expand_reference_names else {}
        return self._request('POST', '/rooms/lookup', params=params, json_data=body)

    def get_room_by_id(self, room_id: str, expand_reference_names: bool = False):
        """
        Get a room by ID.
        :param room_id: ID of the room.
        :param expand_reference_names: Return `displayName` for all referenced objects.
        :return: The room object.
        """
        params = {'expandReferenceNames': expand_reference_names} if expand_reference_names else {}
        return self._request('GET', f'/rooms/{room_id}', params=params)

    # --- Subscriptions (Webhooks) Endpoints ---

    def get_subscriptions(self, **params):
        """
        Get a list of subscriptions.
        :param params: Filter parameters.
        :return: A list of subscriptions.
        """
        mapped_params = {
            'limit': params.get('limit'),
            'pageToken': params.get('page_token'),
        }
        filtered_params = {k: v for k, v in mapped_params.items() if v is not None}
        return self._request('GET', '/subscriptions', params=filtered_params)

    def create_subscription(self, name: str, target: str, resource_types: list):
        """
        Create a subscription.
        :param name: A descriptive name for the webhook.
        :param target: The URL to which the webhook will post.
        :param resource_types: List of resource types to subscribe to.
        :return: The created subscription object.
        """
        body = {
            'name': name,
            'target': target,
            'resourceTypes': [{'resource': rt} for rt in resource_types] # Assumes resource_types is a list of strings
        }
        return self._request('POST', '/subscriptions', json_data=body)

    def delete_subscription(self, subscription_id: str):
        """
        Delete a subscription.
        :param subscription_id: ID of the subscription to delete.
        """
        return self._request('DELETE', f'/subscriptions/{subscription_id}')

    def get_subscription_by_id(self, subscription_id: str):
        """
        Get a subscription by ID.
        :param subscription_id: ID of the subscription.
        :return: The subscription object.
        """
        return self._request('GET', f'/subscriptions/{subscription_id}')

    def update_subscription(self, subscription_id: str, expires: str):
        """
        Update the expire time of a subscription by ID.
        :param subscription_id: ID of the subscription to update.
        :param expires: Expiry timestamp (RFC 3339 format).
        :return: The updated subscription object.
        """
        body = {'expires': expires}
        return self._request('PATCH', f'/subscriptions/{subscription_id}', json_data=body)

    # --- DeletedEntities Endpoint ---

    def get_deleted_entities(self, entities: list, meta_modified_after: str = None):
        """
        Get a list of deleted entities.
        :param entities: List of entity types to query for deleted IDs.
        :param meta_modified_after: Only return entities deleted after this timestamp (RFC 3339 format).
        :return: A list of deleted entities.
        """
        params = {'entities': entities}
        if meta_modified_after:
            params['meta.modified.after'] = meta_modified_after
        return self._request('GET', '/deletedEntities', params=params)

    # --- Log Endpoint ---

    def get_log(self, **params):
        """
        Get a list of log entries.
        :param params: Filter parameters.
        :return: A list of log entries.
        """
        mapped_params = {
            'source': params.get('source'),
            'target': params.get('target'),
            'eventType': params.get('event_type'),
            'timestamp.onOrBefore': params.get('timestamp_on_or_before'),
            'timestamp.onOrAfter': params.get('timestamp_on_or_after'),
            'meta.created.before': params.get('meta_created_before'),
            'meta.created.after': params.get('meta_created_after'),
            'meta.modified.before': params.get('meta_modified_before'),
            'meta.modified.after': params.get('meta_modified_after'),
            'sortkey': params.get('sortkey'),
            'limit': params.get('limit'),
            'pageToken': params.get('page_token'),
        }
        filtered_params = {k: v for k, v in mapped_params.items() if v is not None}
        return self._request('GET', '/log', params=filtered_params)

    # --- Statistics Endpoint ---

    def get_statistics(self, **params):
        """
        Get a list of statistics.
        :param params: Filter parameters.
        :return: A list of statistics.
        """
        mapped_params = {
            'source': params.get('source'),
            'target': params.get('target'),
            'statisticType': params.get('statistic_type'),
            'timestamp.onOrBefore': params.get('timestamp_on_or_before'),
            'timestamp.onOrAfter': params.get('timestamp_on_or_after'),
            'meta.created.before': params.get('meta_created_before'),
            'meta.created.after': params.get('meta_created_after'),
            'meta.modified.before': params.get('meta_modified_before'),
            'meta.modified.after': params.get('meta_modified_after'),
            'sortkey': params.get('sortkey'),
            'limit': params.get('limit'),
            'pageToken': params.get('page_token'),
        }
        filtered_params = {k: v for k, v in mapped_params.items() if v is not None}
        return self._request('GET', '/statistics', params=filtered_params)

# --- Example Usage ---
if __name__ == "__main__":
    # Replace with your actual test server URL and JWT token
    BASE_URL = "https://some.server.se/v2.0"
    AUTH_TOKEN = "YOUR_JWT_TOKEN_HERE"

    client = SS12000Client(BASE_URL, AUTH_TOKEN)

    async def run_example():
        try:
            # Example: Get Organizations
            print("\nFetching organizations...")
            organizations = client.get_organisations(limit=2)
            print("Fetched organizations:", json.dumps(organizations, indent=2))

            if organizations and organizations.get('data'):
                first_org_id = organizations['data'][0]['id']
                print(f"\nFetching organization with ID: {first_org_id}...")
                org_by_id = client.get_organisation_by_id(first_org_id, expand_reference_names=True)
                print("Fetched organization by ID:", json.dumps(org_by_id, indent=2))

            # Example: Get Persons
            print("\nFetching persons...")
            persons = client.get_persons(limit=2, expand=['duties'])
            print("Fetched persons:", json.dumps(persons, indent=2))

            if persons and persons.get('data'):
                first_person_id = persons['data'][0]['id']
                print(f"\nFetching person with ID: {first_person_id}...")
                person_by_id = client.get_person_by_id(first_person_id, expand=['duties', 'responsibleFor'], expand_reference_names=True)
                print("Fetched person by ID:", json.dumps(person_by_id, indent=2))

            # Example: Manage Subscriptions (Webhooks)
            print("\nFetching subscriptions...")
            subscriptions = client.get_subscriptions()
            print("Fetched subscriptions:", json.dumps(subscriptions, indent=2))

            # Example: Create a subscription (requires a publicly accessible webhook URL)
            # print("\nCreating a subscription...")
            # new_subscription = client.create_subscription(
            #     name="My Python Test Subscription",
            #     target="http://your-public-webhook-url.com/ss12000-webhook", # Replace with your public URL
            #     resource_types=["Person", "Activity"]
            # )
            # print("Created subscription:", json.dumps(new_subscription, indent=2))

            # Example: Delete a subscription
            # if subscriptions and subscriptions.get('data'):
            #     sub_to_delete_id = subscriptions['data'][0]['id']
            #     print(f"\nDeleting subscription with ID: {sub_to_delete_id}...")
            #     client.delete_subscription(sub_to_delete_id)
            #     print("Subscription deleted successfully.")

        except requests.exceptions.RequestException as e:
            print(f"An error occurred during API call: {e}")
        except Exception as e:
            print(f"An unexpected error occurred: {e}")

    # To run the example, uncomment the following lines and execute this script:
    # import asyncio
    # asyncio.run(run_example())

# webhook_server.py (FastAPI example)
"""
Example of a simple FastAPI server to receive SS12000 webhooks.
This is a separate file and is not part of the client library.
It demonstrates how to set up an endpoint to receive POST calls from the SS12000 API.
"""

# To run this example, install FastAPI and Uvicorn:
# pip install fastapi uvicorn

# from fastapi import FastAPI, Request, HTTPException
# import uvicorn
# import json

# webhook_app = FastAPI()

# @webhook_app.post("/ss12000-webhook")
# async def ss12000_webhook(request: Request):
#     """
#     Webhook endpoint for SS12000 notifications.
#     """
#     print("Received a webhook from SS12000!")
#     print("Headers:", request.headers)

#     try:
#         body = await request.json()
#         print("Body:", json.dumps(body, indent=2))

#         # Implement your logic to handle the webhook message here.
#         # E.g., save the information to a database, trigger an update, etc.

#         if body and body.get('modifiedEntites'):
#             for resource_type in body['modifiedEntites']:
#                 print(f"Changes for resource type: {resource_type}")
#                 # You can call the SS12000Client here to fetch updated information
#                 # depending on the resource type.
#                 # Example: if resource_type == 'Person': client.get_persons(...)
#         if body and body.get('deletedEntities'):
#             print("There are deleted entities to fetch from /deletedEntities.")
#             # Call client.get_deleted_entities(...) to fetch the deleted IDs.

#         return {"message": "Webhook received successfully!"}
#     except json.JSONDecodeError:
#         raise HTTPException(status_code=400, detail="Invalid JSON body")
#     except Exception as e:
#         print(f"Error processing webhook: {e}")
#         raise HTTPException(status_code=500, detail=f"Internal server error: {e}")

# # To run the FastAPI webhook server:
# # Save the above code as e.g., `webhook_server.py`
# # Then run from your terminal: `uvicorn webhook_server:webhook_app --host 0.0.0.0 --port 3001`
