from cnpos.core.orchestrators.code_automation_pipeline_v1_2 import run_code_automation_pipeline_v1_2
import argparse

def main():
    parser = argparse.ArgumentParser(description="CNPOS v1_2 Code Automation CLI")
    parser.add_argument("command", help="Command to run (e.g., codegen)")
    parser.add_argument("--module", help="Module name to generate", default=None)
    args = parser.parse_args()

    if args.command == "codegen":
        if not args.module:
            raise SystemExit("Error: --module is required for codegen")
        result = run_code_automation_pipeline_v1_2(args.module)
        print("=== CODEGEN RESULT ===")
        print(result)
    else:
        raise SystemExit(f"Unknown command: {args.command}")

if __name__ == "__main__":
    main()
