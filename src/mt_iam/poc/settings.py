"""Validated user-editable non-secret TOML sections for POC management."""
from dataclasses import dataclass
from pathlib import Path
from typing import Any
from mt_iam.poc.platform import RegistryError, _read_toml

_FIELDS = {
    'project': {'name': str, 'environment': str},
    'poc.registry': {'path': str, 'allow_new': bool},
    'poc.orchestrator': {'execution_mode': str, 'max_parallel': int,
                         'fail_fast': bool, 'include_dependencies': bool,
                         'timeout_seconds': int},
    'poc.evidence': {'output_directory': str, 'redact_secrets': bool},
    'database': {'provider': str, 'pool_size': int, 'max_overflow': int,
                 'pool_timeout_seconds': int},
    'security': {'allow_remote_execution': bool, 'allow_dynamic_plugins': bool,
                 'require_review_for_new_handlers': bool},
    'cloud': {'enabled': bool, 'max_instances': int},
    'testing': {'require_negative_tests': bool, 'require_cleanup_tests': bool},
}

@dataclass(frozen=True)
class PlatformSettings:
    project: dict
    registry: dict
    orchestrator: dict
    evidence: dict
    database: dict
    security: dict
    cloud: dict
    testing: dict

    @classmethod
    def load(cls, path: Path) -> 'PlatformSettings':
        data = _read_toml(path)
        flattened: dict[str, dict[str, Any]] = {
            'project': data.get('project', {}),
            'poc.registry': data.get('poc', {}).get('registry', {}),
            'poc.orchestrator': data.get('poc', {}).get('orchestrator', {}),
            'poc.evidence': data.get('poc', {}).get('evidence', {}),
            'database': data.get('database', {}), 'security': data.get('security', {}),
            'cloud': data.get('cloud', {}), 'testing': data.get('testing', {}),
        }
        if set(data) - {'project', 'poc', 'database', 'security', 'cloud', 'testing'}:
            raise RegistryError('Unexpected config section')
        if set(data.get('poc', {})) - {'registry', 'orchestrator', 'evidence'}:
            raise RegistryError('Unexpected POC config section')
        for section, content in flattened.items():
            if not isinstance(content, dict) or set(content) - set(_FIELDS[section]):
                raise RegistryError(f'Unexpected key in {section}')
            for key, value in content.items():
                expected = _FIELDS[section][key]
                if type(value) is not expected:
                    raise RegistryError(f'Expected {expected.__name__} at {section}.{key}')
        if flattened['poc.orchestrator'].get('execution_mode', 'sequential') not in ('sequential', 'isolated'):
            raise RegistryError('Parallel execution requires isolated mode; valid modes: sequential, isolated')
        limit = flattened['poc.orchestrator'].get('max_parallel', 1)
        mode = flattened['poc.orchestrator'].get('execution_mode', 'sequential')
        if not 1 <= limit <= (4 if mode == 'isolated' else 1):
            raise RegistryError('Invalid bounded worker limit')
        if not 1 <= flattened['poc.orchestrator'].get('timeout_seconds', 15) <= 300:
            raise RegistryError('Timeout outside bounded range')
        if flattened['security'].get('allow_remote_execution', False):
            raise RegistryError('Remote execution must remain disabled in this lab')
        if flattened['security'].get('allow_dynamic_plugins', False):
            raise RegistryError('Dynamic plugin import is forbidden in this lab')
        if flattened['poc.evidence'].get('redact_secrets', True) is False:
            raise RegistryError('Evidence secret redaction cannot be disabled')
        for section, keys in [('database', ('pool_size','pool_timeout_seconds')),
                              ('cloud', ('max_instances',))]:
            if any(flattened[section].get(k, 1) < 1 for k in keys):
                raise RegistryError('Resource budgets must be positive')
        if flattened['database'].get('max_overflow', 0) < 0:
            raise RegistryError('max_overflow must be nonnegative')
        return cls(*(flattened[key] for key in _FIELDS))

    def registry_path(self, config_file: Path) -> Path:
        relative = Path(self.registry.get('path', 'configs/poc_registry.toml'))
        if relative.is_absolute() or '..' in relative.parts:
            raise RegistryError('Registry path must stay within project')
        root = config_file.parent.parent.resolve()
        path = (root / relative).resolve()
        if not path.is_relative_to(root):
            raise RegistryError('Registry path escape')
        return path
