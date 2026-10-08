"""Load packaged defaults, user configuration and project overrides."""
import json
import math
import os
from pathlib import Path


class ConfigError(ValueError):
    pass


def load_config(path=None):
    defaults = Path(__file__).with_name('defaults.json')
    user = Path(os.environ.get('XDG_CONFIG_HOME', Path.home() / '.config')) / 'karyo' / 'config.json'
    project = Path(path).expanduser() if path else Path.cwd() / 'config.json'
    config = {}
    for source, required in ((defaults, True), (user, False), (project, path is not None)):
        try:
            values = json.loads(source.read_text(encoding='utf-8'))
        except FileNotFoundError:
            if required:
                raise ConfigError(f'Configuration file not found: {source}') from None
            continue
        except (OSError, ValueError):
            raise ConfigError(f'Cannot read valid JSON configuration: {source}') from None
        if not isinstance(values, dict):
            raise ConfigError(f'Configuration must be a JSON object: {source}')
        config.update({key: values[key] for key in ('provider', 'model', 'max_tokens', 'timeout_seconds') if key in values})
    for key in ('provider', 'model'):
        if not isinstance(config.get(key), str) or not config[key].strip():
            raise ConfigError(f'{key} must be a nonempty string')
    if type(config.get('max_tokens')) is not int or config['max_tokens'] <= 0:
        raise ConfigError('max_tokens must be a positive integer')
    timeout = config.get('timeout_seconds')
    if type(timeout) not in (int, float) or not math.isfinite(timeout) or timeout <= 0:
        raise ConfigError('timeout_seconds must be a positive finite number')
    return config
