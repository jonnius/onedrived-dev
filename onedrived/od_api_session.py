import binascii
import pickle
from time import time
import zlib

import keyring
import onedrivesdk.session


def get_keyring_key(account_id):
    return OneDriveAPISession.KEYRING_ACCOUNT_KEY_PREFIX + account_id


class OneDriveAPISession(onedrivesdk.session.Session):

    SESSION_ARG_KEYNAME = 'key'
    KEYRING_SERVICE_NAME = 'onedrived_v2'
    KEYRING_ACCOUNT_KEY_PREFIX = 'user.'
    PICKLE_PROTOCOL = 3
    #
    # def __init__(self,
    #              token_type,
    #              expires_in,
    #              scope_string,
    #              access_token,
    #              client_id,
    #              auth_server_url,
    #              redirect_uri,
    #              refresh_token=None,
    #              client_secret=None):
    #     super().__init__(token_type=token_type, expires_in=expires_in, scope_string=scope_string,
    #                      access_token=access_token, client_id=client_id, auth_server_url=auth_server_url,
    #                      redirect_uri=redirect_uri, refresh_token=refresh_token, client_secret=client_secret)

    @property
    def expires_in_sec(self):
        return self._expires_at - time()

    def save_session(self, **save_session_kwargs):
        if self.SESSION_ARG_KEYNAME not in save_session_kwargs:
            raise ValueError('"%s" must be specified in save_session() argument.' % self.SESSION_ARG_KEYNAME)
        data = binascii.b2a_base64(zlib.compress(pickle.dumps(self, self.PICKLE_PROTOCOL)))
        keyring.set_password(self.KEYRING_SERVICE_NAME, save_session_kwargs['key'], data)

    @staticmethod
    def load_session(**load_session_kwargs):
        keyarg = OneDriveAPISession.SESSION_ARG_KEYNAME
        if keyarg not in load_session_kwargs:
            raise ValueError('"%s" must be specified in load_session() argument.' % keyarg)
        saved_data = keyring.get_password(OneDriveAPISession.KEYRING_SERVICE_NAME, load_session_kwargs[keyarg])
        data = zlib.decompress(binascii.a2b_base64(saved_data))
        return pickle.loads(data)
