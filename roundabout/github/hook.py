import hashlib
import hmac
import json
import urlparse

from roundabout import log
from roundabout import models
from roundabout.github import request


def _handle_callback(cfg, mode, opener=None):
    base = 'https://github.com'
    username, password = cfg['github']['auth'].values()

    with request.gh_request(username, password) as github:
        topics = ('/events/pull_request', '/events/issue_comment')

        for t in topics:
            topic = urlparse.urljoin(base, cfg['github']['repo'] + t)
            post_data = {'hub.mode': mode,
                         'hub.topic': topic,
                         'hub.callback': cfg['github']['callback_url'],}
            secret = cfg['github'].get('secret')
            if secret:
                post_data['hub.secret'] = secret

            try:
                github.post('https://api.github.com/hub', encode=False,
                            **post_data)
            except request.urllib2.URLError, e:
                log.error("Error trying to register: %s" % e.read())


def register_callback(config, opener=None):
    return _handle_callback(config, 'subscribe', opener)


def unregister_callback(config, opener=None):
    return _handle_callback(config, 'unsubscribe', opener)


def build_callback(cfg):
    def _check_signature(secret, body, sig):
        _hmac = hmac.new(secret, body, hashlib.sha1).hexdigest()
        _sig = sig.split('=')[1]

        if _hmac == _sig:
            return True
        return False

    def _callback(env, start_response):
        body = env['wsgi.input'].read(int(env.get('CONTENT_LENGTH', 0)))

        secret = cfg.get('secret')
        sig = env.get('HTTP_X_HUB_SIGNATURE')

        if (secret or sig) and not _check_signature(secret, body, sig):
            start_response('500 Error', [('Content-type', 'text/plain')])
            log.error("Signature did not match local HMAC from secret"
                      "(%s, %s)" % (sig, secret))
            
            return ["Signature did not match local HMAC"]

        body = urlparse.parse_qs(body)
        payload = json.loads(body.get('payload', '[{}]')[0])

        if models.handle_model(env['HTTP_X_GITHUB_EVENT'], payload):
            start_response('200 OK', [('Content-type', 'text/plain')])
            return ['THANKS!']
        
        start_response('500 Error', ['Content-type', 'text/plain'])
        log.error("Error building the model")
        return ['Error!']
    return _callback
