# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

from openstack import exceptions
from openstack import resource
from openstack import utils


class Stack(resource.Resource):
    name_attribute = 'stack_name'
    resource_key = 'stack'
    resources_key = 'stacks'
    base_path = '/stacks'

    # capabilities
    allow_create = True
    allow_list = True
    allow_fetch = True
    allow_commit = True
    allow_delete = True

    # Properties
    #: A list of resource objects that will be added if a stack update
    #  is performed.
    added = resource.Body('added')
    #: Placeholder for AWS compatible template listing capabilities
    #: required by the stack.
    capabilities = resource.Body('capabilities')
    #: Timestamp of the stack creation.
    created_at = resource.Body('creation_time')
    #: A text description of the stack.
    description = resource.Body('description')
    #: A list of resource objects that will be deleted if a stack
    #: update is performed.
    deleted = resource.Body('deleted', type=list)
    #: Whether the stack will support a rollback operation on stack
    #: create/update failures. *Type: bool*
    is_rollback_disabled = resource.Body('disable_rollback', type=bool)
    #: A list of dictionaries containing links relevant to the stack.
    links = resource.Body('links')
    #: Name of the stack.
    name = resource.Body('stack_name')
    stack_name = resource.URI('stack_name')
    #: Placeholder for future extensions where stack related events
    #: can be published.
    notification_topics = resource.Body('notification_topics')
    #: A list containing output keys and values from the stack, if any.
    outputs = resource.Body('outputs')
    #: The ID of the owner stack if any.
    owner_id = resource.Body('stack_owner')
    #: A dictionary containing the parameter names and values for the stack.
    parameters = resource.Body('parameters', type=dict)
    #: The ID of the parent stack if any
    parent_id = resource.Body('parent')
    #: A list of resource objects that will be replaced if a stack update
    #: is performed.
    replaced = resource.Body('replaced')
    #: A string representation of the stack status, e.g. ``CREATE_COMPLETE``.
    status = resource.Body('stack_status')
    #: A text explaining how the stack transits to its current status.
    status_reason = resource.Body('stack_status_reason')
    #: A list of strings used as tags on the stack
    tags = resource.Body('tags')
    #: A dict containing the template use for stack creation.
    template = resource.Body('template', type=dict)
    #: Stack template description text. Currently contains the same text
    #: as that of the ``description`` property.
    template_description = resource.Body('template_description')
    #: A string containing the URL where a stack template can be found.
    template_url = resource.Body('template_url')
    #: Stack operation timeout in minutes.
    timeout_mins = resource.Body('timeout_mins')
    #: A list of resource objects that will remain unchanged if a stack
    #: update is performed.
    unchanged = resource.Body('unchanged')
    #: A list of resource objects that will have their properties updated
    #: in place if a stack update is performed.
    updated = resource.Body('updated')
    #: Timestamp of last update on the stack.
    updated_at = resource.Body('updated_time')
    #: The ID of the user project created for this stack.
    user_project_id = resource.Body('stack_user_project_id')

    def create(self, session, base_path=None):
        # This overrides the default behavior of resource creation because
        # heat doesn't accept resource_key in its request.
        return super(Stack, self).create(session, prepend_key=False,
                                         base_path=base_path)

    def commit(self, session, base_path=None):
        # This overrides the default behavior of resource creation because
        # heat doesn't accept resource_key in its request.
        return super(Stack, self).commit(session, prepend_key=False,
                                         has_body=False, base_path=None)

    def update(self, session, preview=False):
        # This overrides the default behavior of resource update because
        # we need to use other endpoint for update preview.
        request = self._prepare_request(
            prepend_key=False,
            base_path='/stacks/%(stack_name)s/' % {'stack_name': self.name})

        microversion = self._get_microversion_for(session, 'commit')

        request_url = request.url
        if preview:
            request_url = utils.urljoin(request_url, 'preview')

        response = session.put(
            request_url, json=request.body, headers=request.headers,
            microversion=microversion)

        self.microversion = microversion
        self._translate_response(response, has_body=True)
        return self

    def _action(self, session, body):
        """Perform stack actions"""
        url = utils.urljoin(self.base_path, self._get_id(self), 'actions')
        resp = session.post(url, json=body)
        return resp.json()

    def check(self, session):
        return self._action(session, {'check': ''})

    def abandon(self, session):
        url = utils.urljoin(self.base_path, self.name,
                            self._get_id(self), 'abandon')
        resp = session.delete(url)
        return resp.json()

    def fetch(self, session, requires_id=True,
              base_path=None, error_message=None):
        stk = super(Stack, self).fetch(
            session,
            requires_id=requires_id,
            base_path=base_path,
            error_message=error_message)
        if stk and stk.status in ['DELETE_COMPLETE', 'ADOPT_COMPLETE']:
            raise exceptions.ResourceNotFound(
                "No stack found for %s" % stk.id)
        return stk


StackPreview = Stack
