"""Command line interface for LayerDiet."""

import sys
import os
import argparse
import json
from layerdiet.docker_parser import DockerfileParser
from layerdiet.anti_patterns import DockerLinter
from layerdiet.dep_auditor import DependencyAuditor
from layerdiet.optimizer import DockerOptimizer


def main():
    parser = argparse.ArgumentParser(
        prog="layerdiet",
        description="LayerDiet: Dockerfile layer bloat auditor and dependency slimmer."
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    # audit
    p_audit = subparsers.add_parser("audit", help="Audit Dockerfile and Python dependencies")
    p_audit.add_argument("path", default=".", nargs="?", help="Project root directory or Dockerfile path")
    p_audit.add_argument("--json", action="store_true", help="Output audit report as JSON")

    # optimize
    p_opt = subparsers.add_parser("optimize", help="Generate an optimized multi-stage Dockerfile")
    p_opt.add_argument("--python", default="3.11", help="Target Python version (default: 3.11)")
    p_opt.add_argument("--output", "-o", default="Dockerfile.slim", help="Output path (default: Dockerfile.slim)")

    args = parser.parse_args()

    if args.command == "audit":
        target = args.path
        df_path = target if os.path.isfile(target) else os.path.join(target, "Dockerfile")
        
        findings = []
        if os.path.exists(df_path):
            instructions = DockerfileParser.parse_file(df_path)
            findings = DockerLinter.audit(instructions)

        proj_dir = os.path.dirname(df_path) if os.path.isfile(df_path) else target
        dep_res = DependencyAuditor.audit(proj_dir)

        if args.json:
            data = {
                "dockerfile": df_path if os.path.exists(df_path) else None,
                "anti_patterns": [{
                    "severity": f.severity,
                    "rule": f.rule_id,
                    "message": f.message,
                    "line": f.line_number,
                    "recommendation": f.recommendation
                } for f in findings],
                "declared_deps": list(dep_res.declared_dependencies),
                "unused_deps": list(dep_res.unused_dependencies)
            }
            print(json.dumps(data, indent=2))
        else:
            print("\n" + "=" * 62)
            print("         🐳 LayerDiet - Container & Dependency Audit")
            print("=" * 62)
            
            if findings:
                print(f"\n⚠️  Found {len(findings)} Dockerfile Anti-Pattern(s):")
                for f in findings:
                    print(f"  [{f.severity}] Line {f.line_number}: {f.message}")
                    print(f"      💡 Recommendation: {f.recommendation}")
            else:
                print("\n✅ Dockerfile layers follow slimming best practices.")

            if dep_res.unused_dependencies:
                print(f"\n📦 Unused Dependencies in Manifest ({len(dep_res.unused_dependencies)}):")
                for d in sorted(dep_res.unused_dependencies):
                    print(f"  • {d} (installed but never imported in source)")
            else:
                print("\n✅ All declared dependencies are actively imported.")

    elif args.command == "optimize":
        content = DockerOptimizer.generate_slim_dockerfile(args.python)
        with open(args.output, "w") as f:
            f.write(content)
        print(f"✨ Optimized multi-stage Dockerfile generated at '{args.output}'.")


if __name__ == "__main__":
    main()
