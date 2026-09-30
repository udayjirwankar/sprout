"""Keep Flask's signing secret stable across local app restarts."""
import os
import secrets
import tempfile
from pathlib import Path


def get_session_key():
    configured = os.environ.get('SPROUT_SESSION_SECRET')
    if configured:
        return configured
    path = Path(__file__).with_name('session.key')
    if not path.exists():
        # Publish a complete file atomically, including when workers start together.
        descriptor, temporary = tempfile.mkstemp(prefix='.session-', dir=path.parent)
        try:
            with os.fdopen(descriptor, 'w', encoding='utf-8') as key_file:
                key_file.write(secrets.token_hex(32))
            try:
                os.link(temporary, path)
            except FileExistsError:
                pass
        finally:
            os.unlink(temporary)
    key = path.read_text(encoding='utf-8').strip()
    if not key:
        raise ValueError('The saved session secret is empty. Configure SPROUT_SESSION_SECRET.')
    return key
