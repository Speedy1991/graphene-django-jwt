from django.dispatch import Signal

refresh_token_revoked = Signal(providing_args=['refresh_token'])
refresh_token_rotated = Signal(providing_args=['refresh_token', 'new_refresh_token'])
refresh_finished = Signal(providing_args=['request', 'user'])
