"""POC registry extensibility and orchestrator contracts (no external calls)."""
from pathlib import Path
import pytest
from mt_iam.poc.platform import POCRegistry, POCOrchestrator, RegistryError, report, write_report
from mt_iam.poc.settings import PlatformSettings


def toml(tmp_path, content):
    path = tmp_path / 'cases.toml'
    path.write_text(content, encoding='utf-8')
    return path


def test_canonical_baseline_52():
    registry = POCRegistry.from_toml()
    assert len(registry.by_id) == 52
    assert len(registry.plan()) == 52


def test_add_new_item_defaults_to_blocked(tmp_path):
    registry = POCRegistry.from_toml(toml(tmp_path, '''
[[poc]]
id = "POC-G99-01"
title = "New experimental POC"
priority = "P2"
'''))
    assert len(registry.by_id) == 53
    item = POCOrchestrator(registry).run(['POC-G99-01'])[0]
    assert item.status == 'BLOCKED'


def test_builtin_external_cannot_be_promoted_by_config(tmp_path):
    with pytest.raises(RegistryError):
        POCRegistry.from_toml(toml(tmp_path, '''
[[poc]]
id = "POC-G05-06"
mode = "local"
'''))


def test_unknown_plugin_handler_cannot_run(tmp_path):
    with pytest.raises(RegistryError):
        POCRegistry.from_toml(toml(tmp_path, '''
[[poc]]
id = "POC-G99-02"
title = "unsafe"
mode = "local"
'''))


def test_duplicate_entries_and_unknown_fields_rejected(tmp_path):
    with pytest.raises(RegistryError):
        POCRegistry.from_toml(toml(tmp_path, '''
[[poc]]
id = "POC-G99-01"
title = "one"
[[poc]]
id = "POC-G99-01"
title = "two"
'''))
    with pytest.raises(RegistryError):
        POCRegistry.from_toml(toml(tmp_path, '''
[[poc]]
id = "POC-G99-02"
title = "test"
command = "rm -rf /"
'''))


def test_cycle_and_missing_dependencies_rejected(tmp_path):
    with pytest.raises(RegistryError, match='Cyclic'):
        POCRegistry.from_toml(toml(tmp_path, '''
[[poc]]
id = "POC-G99-01"
title = "one"
depends_on = ["POC-G99-02"]
[[poc]]
id = "POC-G99-02"
title = "two"
depends_on = ["POC-G99-01"]
'''))
    with pytest.raises(RegistryError, match='Unknown prerequisite'):
        POCRegistry.from_toml(toml(tmp_path, '''
[[poc]]
id = "POC-G99-01"
title = "one"
depends_on = ["POC-G99-05"]
'''))


def test_topological_order_and_blocking(tmp_path):
    registry = POCRegistry.from_toml(toml(tmp_path, '''
[[poc]]
id = "POC-G99-01"
title = "depends"
depends_on = ["POC-G05-06"]
'''))
    results = POCOrchestrator(registry).run(['POC-G99-01'])
    assert [r.id for r in results] == ['POC-G05-06','POC-G99-01']
    assert [r.status for r in results] == ['BLOCKED', 'BLOCKED']


def test_dry_run_never_executes_handler():
    registry = POCRegistry.from_toml()
    def forbidden():
        raise AssertionError('must not execute')
    result = POCOrchestrator(registry, {'POC-G01-01': forbidden}).run(['POC-G01-01'], dry_run=True)
    assert result[0].status == 'NOT_RUN'


def test_exceptions_are_fail_closed():
    registry = POCRegistry.from_toml()
    def failing():
        raise RuntimeError('synthetic failure')
    results = POCOrchestrator(registry, {'POC-G01-01': failing}).run(['POC-G01-01'])
    assert results[0].status == 'FAIL'
    assert 'synthetic failure' not in results[0].detail


def test_disable_prevents_execution(tmp_path):
    registry = POCRegistry.from_toml(toml(tmp_path, '''
[[poc]]
id = "POC-G01-01"
enabled = false
'''))
    result = POCOrchestrator(registry).run(['POC-G01-01'])
    assert result[0].status == 'SKIPPED'


def test_report_atomic_write_and_no_full_pass(tmp_path):
    registry = POCRegistry.from_toml()
    outcomes = POCOrchestrator(registry).run(['POC-G05-06'])
    payload = report(outcomes)
    output = tmp_path / 'report.json'
    write_report(output,payload)
    assert output.is_file()
    assert 'NOT_CERTIFIED' in output.read_text()
    assert not output.with_suffix('.json.tmp').exists()


def test_platform_sections_validated():
    root = Path(__file__).parent.parent
    config = PlatformSettings.load(root/'configs'/'platform.toml')
    registry_path = config.registry_path(root/'configs'/'platform.toml')
    assert registry_path.exists()
    assert len(POCRegistry.from_toml(registry_path).by_id) == 53


def test_remote_execution_setting_refused(tmp_path):
    with pytest.raises(RegistryError, match='Remote execution'):
        PlatformSettings.load(toml(tmp_path, '[security]\nallow_remote_execution = true'))


def test_parallel_execution_setting_refused(tmp_path):
    with pytest.raises(RegistryError, match='Parallel execution'):
        PlatformSettings.load(toml(tmp_path, '[poc.orchestrator]\nexecution_mode = "parallel"'))
