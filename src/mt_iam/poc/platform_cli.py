"""POC Registry/Orchestrator CLI. Only trusted built-in handlers can execute."""
from argparse import ArgumentParser
from pathlib import Path
from mt_iam.poc.platform import POCRegistry, POCOrchestrator, IsolatedPOCOrchestrator, report, write_report
from mt_iam.poc.settings import PlatformSettings


def main(argv: list[str] | None = None) -> int:
    parser = ArgumentParser(description="MT-IAM expandable POC platform")
    parser.add_argument("--config", type=Path, default=None, help="Validated platform TOML")
    parser.add_argument("--registry", type=Path, default=None, help="TOML entries/overrides")
    parser.add_argument("--id", action="append", dest="ids", help="Selected ID, repeatable")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--report", type=Path, default=None, help="Write JSON evidence")
    parser.add_argument("--strict", action="store_true", help="Nonzero unless every check locally passes")
    args = parser.parse_args(argv)
    settings = None
    registry_path = args.registry
    if args.config:
        settings = PlatformSettings.load(args.config)
        if registry_path is None:
            registry_path = settings.registry_path(args.config)
    registry = POCRegistry.from_toml(registry_path)
    if settings and settings.orchestrator.get("execution_mode") == "isolated":
        orch = IsolatedPOCOrchestrator(
            registry,
            max_workers=settings.orchestrator.get("max_parallel", 1),
            timeout_seconds=settings.orchestrator.get("timeout_seconds", 15),
            fail_fast=settings.orchestrator.get("fail_fast", False),
        )
    else:
        orch = POCOrchestrator(registry)
    outputs = orch.run(args.ids, dry_run=args.dry_run)
    evidence = report(outputs, config_path=registry_path)
    if args.report:
        write_report(args.report, evidence)
    print(f"POCs={len(outputs)}: {evidence['summary']} (full POC verification NOT_CERTIFIED)")
    for item in outputs:
        print(f"{item.id}: {item.status}: {item.detail}")
    if any(item.status in ("FAIL", "TIMEOUT", "CANCELLED") for item in outputs):
        return 1
    if args.strict and any(item.status != "LOCAL_CHECK_PASS" for item in outputs):
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
