# Copyright 2010, 2011 Christopher MacGown
# Copyright 2011, Piston Cloud Computing, Inc.
# All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import os


from roundabout import exc
from roundabout import models
from roundabout.models import comment

# TODO(chris): flags

class PullRequest(models.Model):
    __file__ = "pull.js"

    def __init__(self, pr_dict, path="pull_request_path"):
        self._pull_request = pr_dict
        if path.endswith(str(self._pull_request['number'])):
            self.filename = os.path.join(path, self.__file__)
        else:
            self.filename = os.path.join(path,
                                         str(self._pull_request['number']),
                                         self.__file__)
        #super(PullRequest, self).__init__(config)
        #self.id = pr_dict['number']
        #self.status = pr_dict['pull_request']['state']
        #self.merge_source = pr_dict['pull_request']['head']
        #self.merge_target = pr_dict['pull_request']['base']

    def __getattr__(self, key):
        if key in self._pull_request.keys():
            return self._pull_request[key]

        try:
            return object.__getattribute__(self, key)
        except ValueError:
            raise AttributeError("%r object has no attribute %r" %
                                 (type(self).__name__, key))

    def save(self):
        super(PullRequest, self).save(self._pull_request)

    @property
    def comments(self):
        try:
            return comment.Comments.load(os.path.dirname(self.filename))
        except IOError:
            c = comment.Comments(comments=[],
                                 path=os.path.dirname(self.filename))
            c.save()
            return c

    def looks_good_to_a_robot(self):
        return self.approved('robots')

    def looks_good_to_a_human(self):
        return self.approved('humans')

    def _approved(self, kind):
        if not kind in ('humans', 'robots'):
            raise exc.UnknownApproverType("We don't serve droids here.")

        approver_kind = self.config['lgtm'].get(kind, {})
        if not approver_kind:
            return None

        for c in self.comments:
            c = {'user': c['user']['login'],
                 'msg': c.get('body', ''),}

            if c['user'] in approver_kind['approvers'] and \
               c['msg'].lower() is approver_kind['lgtm'].lower():
                   return True
        return None
