"""Independent POC verification manifest validation, NOT production conformance."""
from mt_iam.poc.platform import POCRegistry
from mt_iam.poc.quality_gate import check_evidence


def sample():
    return dict(poc_id="POC-G10-01",schema_version=1,verification_status="PASS",
                runner_status="LOCAL_CHECK_PASS",external_or_scope_evidence="VERIFIED",
                source_sha="a"*40,environment="Python 3.13 Linux isolated test",
                command="python -m pytest",owner="engineer",reviewer="independent-reviewer",
                review_decision="ACCEPT", resource_cleanup="VERIFIED",
                cases=[{"kind":"positive","status":"PASS"},{"kind":"negative","status":"PASS"}],
                artifacts=[{"sha256":"a"*64}])


def test_approved_evidence_is_structurally_accepted():
    assert check_evidence(sample(), POCRegistry.from_toml()).accepted


def test_local_check_does_not_self_certify():
    doc=sample();doc.pop("external_or_scope_evidence")
    assert not check_evidence(doc, POCRegistry.from_toml()).accepted


def test_missing_independent_review_rejected():
    doc=sample();doc["reviewer"]="engineer"
    assert not check_evidence(doc, POCRegistry.from_toml()).accepted


def test_missing_negative_case_rejected():
    doc=sample();doc["cases"]=[{"kind":"positive","status":"PASS"}]
    assert not check_evidence(doc, POCRegistry.from_toml()).accepted


def test_external_needs_external_evidence():
    doc=sample();doc["poc_id"]="POC-G05-06";doc["external_or_scope_evidence"]="NOT_RUN"
    assert not check_evidence(doc, POCRegistry.from_toml()).accepted


def test_unknown_poc_rejected():
    doc=sample();doc["poc_id"]="POC-G99-99"
    assert not check_evidence(doc, POCRegistry.from_toml()).accepted


def test_fail_is_not_accepted():
    doc=sample();doc["verification_status"]="FAIL"
    assert not check_evidence(doc, POCRegistry.from_toml()).accepted


def test_artifact_hash_required():
    doc=sample();doc["artifacts"]=[{"sha256":"oops"}]
    assert not check_evidence(doc, POCRegistry.from_toml()).accepted
