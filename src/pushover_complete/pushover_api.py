from urllib.parse import urljoin

import requests

from .error import BadAPIRequestError

PUSHOVER_API_URL = 'https://api.pushover.net/1/'


class PushoverAPI(object):
    def __init__(self, token):
        self.token = token

    def _send_message(self, user, message, device=None, title=None, url=None, url_title=None,
                      priority=None, retry=None, expire=None, timestamp=None, sound=None, html=False, session=None):
        payload = {
            'token': self.token,
            'user': user,
            'message': message,
            'device': device,
            'title': title,
            'url': url,
            'url_title': url_title,
            'priority': priority,
            'retry': retry,
            'expire': expire,
            'timestamp': timestamp,
            'sound': sound,
            'html': html
        }
        headers = {'Content-type': 'application/x-www-form-urlencoded'}

        if session is None:
            resp = requests.post(
                urljoin(PUSHOVER_API_URL, 'messages.json'),
                data=payload,
                headers=headers
            )
        else:
            resp = session.post(
                urljoin(PUSHOVER_API_URL, 'messages.json'),
                data=payload,
                headers=headers
            )

        resp_body = resp.json()
        if resp_body.get('status', None) != 1:
            raise BadAPIRequestError('HTTP Status {}: {}'.format(resp.status_code, '; '.join(resp_body.get('errors'))))
        elif resp.status_code != 200:
            raise BadAPIRequestError('HTTP Status {}').format(resp.status_code)
        return resp

    def send_message(self, user, message, device=None, title=None, url=None, url_title=None,
                     priority=None, retry=None, expire=None, timestamp=None, sound=None, html=False):
        resp = self._send_message(user, message, device, title, url, url_title, priority, retry, expire, timestamp,
                                  sound, html)
        return resp

    def send_messages(self, messages):
        sess = requests.Session()
        resps = []
        for message in messages:
            resps.append(self._send_message(session=sess, **message))
        return resps

    def get_sounds(self):
        resp = requests.get(
            urljoin(PUSHOVER_API_URL, 'sounds.json'),
            data={'token': self.token}
        )

        resp_body = resp.json()

        if resp_body.get('status', None) != 1:
            raise BadAPIRequestError('{}: {}'.format(resp.status_code, '; '.join(resp_body.get('errors'))))
        return resp_body.get('sounds', None)

    def validate(self, user, device=None):
        payload = {
            'token': self.token,
            'user': user,
            'device': device
        }
        resp = requests.post(
            urljoin(PUSHOVER_API_URL, 'users/validate.json'),
            data=payload
        )
        if resp.json().get('status', None) != 1:
            raise BadAPIRequestError('{}: {}'.format(resp.status_code, '; '.join(resp_body.get('errors'))))
        return resp

    def check_receipt(self, receipt):
        payload = {
            'token': self.token
        }
        resp = requests.get(
            urljoin(PUSHOVER_API_URL, 'receipts/{}.json'.format(receipt)),
            data=payload
        )
        if resp.json().get('status', None) != 1:
            raise BadAPIRequestError('{}: {}'.format(resp.status_code, '; '.join(resp_body.get('errors'))))
        return resp

    def cancel_receipt(self, receipt):
        payload = {
            'token': self.token
        }
        resp = requests.get(
            urljoin(PUSHOVER_API_URL, 'receipts/{}/cancel.json'.format(receipt)),
            data = payload
        )
        if resp.json().get('status', None) != 1:
            raise BadAPIRequestError('{}: {}'.format(resp.status_code, '; '.join(resp_body.get('errors'))))
        return resp
