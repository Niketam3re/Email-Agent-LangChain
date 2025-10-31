"""
Setup script for Email AI Agent
Helps verify environment and dependencies
"""

import os
import sys
from pathlib import Path


def check_python_version():
    """Check if Python version is 3.11 or higher"""
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 11):
        print(f"❌ Python 3.11+ required. You have {version.major}.{version.minor}")
        return False
    print(f"✅ Python version: {version.major}.{version.minor}.{version.micro}")
    return True


def check_env_file():
    """Check if .env file exists"""
    env_path = Path(".env")
    if not env_path.exists():
        print("⚠️  .env file not found")
        print("   Creating from .env.example...")

        example_path = Path(".env.example")
        if example_path.exists():
            with open(example_path, 'r') as src:
                with open(env_path, 'w') as dst:
                    dst.write(src.read())
            print("✅ Created .env file - please edit with your credentials")
        else:
            print("❌ .env.example not found")
            return False
    else:
        print("✅ .env file exists")
    return True


def check_required_env_vars():
    """Check if required environment variables are set"""
    from dotenv import load_dotenv
    load_dotenv()

    required_vars = [
        "ANTHROPIC_API_KEY",
        "SUPABASE_OAUTH_TOKEN",
        "SUPABASE_URL"
    ]

    optional_vars = [
        "LANGSMITH_API_KEY",
        "GMAIL_MCP_COMMAND"
    ]

    all_good = True

    print("\n🔍 Checking required environment variables:")
    for var in required_vars:
        value = os.getenv(var)
        if not value or value.startswith("sk-ant-xxx") or value.startswith("sbp_xxx") or value.startswith("https://your"):
            print(f"   ❌ {var} - not set or using example value")
            all_good = False
        else:
            # Show partial value for security
            masked = value[:8] + "..." + value[-4:] if len(value) > 12 else "***"
            print(f"   ✅ {var} - {masked}")

    print("\n🔍 Checking optional environment variables:")
    for var in optional_vars:
        value = os.getenv(var)
        if value and not value.startswith("lsv2_pt_xxx"):
            print(f"   ✅ {var} - configured")
        else:
            print(f"   ⚠️  {var} - not set (optional)")

    return all_good


def check_dependencies():
    """Check if key dependencies are installed"""
    print("\n🔍 Checking dependencies:")

    dependencies = {
        "langgraph": "langgraph",
        "langchain": "langchain",
        "langchain_anthropic": "langchain-anthropic",
        "deepagents": "deepagents",
        "langchain_mcp_adapters": "langchain-mcp-adapters",
        "supabase": "supabase",
        "dotenv": "python-dotenv"
    }

    all_installed = True

    for module, package in dependencies.items():
        try:
            __import__(module)
            print(f"   ✅ {package}")
        except ImportError:
            print(f"   ❌ {package} - not installed")
            all_installed = False

    if not all_installed:
        print("\n💡 Install missing dependencies with:")
        print("   pip install -r requirements.txt")

    return all_installed


def check_directories():
    """Check if required directories exist"""
    print("\n🔍 Checking directory structure:")

    directories = ["tools", "supabase"]

    for directory in directories:
        path = Path(directory)
        if path.exists():
            print(f"   ✅ {directory}/")
        else:
            print(f"   ❌ {directory}/ - missing")
            return False

    return True


def check_files():
    """Check if required files exist"""
    print("\n🔍 Checking required files:")

    files = [
        "agent.py",
        "langgraph.json",
        "requirements.txt",
        "tools/mermaid_generator.py",
        "supabase/schema.sql"
    ]

    all_exist = True

    for file in files:
        path = Path(file)
        if path.exists():
            print(f"   ✅ {file}")
        else:
            print(f"   ❌ {file} - missing")
            all_exist = False

    return all_exist


def main():
    """Run all setup checks"""
    print("=" * 80)
    print("Email AI Agent - Setup Verification")
    print("=" * 80)

    checks = [
        ("Python Version", check_python_version),
        ("Environment File", check_env_file),
        ("Directory Structure", check_directories),
        ("Required Files", check_files),
        ("Dependencies", check_dependencies),
        ("Environment Variables", check_required_env_vars),
    ]

    results = []

    for name, check_func in checks:
        print(f"\n📋 {name}:")
        print("-" * 80)
        result = check_func()
        results.append((name, result))

    print("\n" + "=" * 80)
    print("Setup Summary:")
    print("=" * 80)

    all_passed = True
    for name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} - {name}")
        if not result:
            all_passed = False

    print("=" * 80)

    if all_passed:
        print("\n🎉 All checks passed! You're ready to run the agent.")
        print("\n💡 Next steps:")
        print("   1. Review your .env file and add credentials")
        print("   2. Run the Supabase schema: supabase/schema.sql")
        print("   3. Test the agent: python agent.py")
        print("   4. Or start dev server: langgraph dev")
    else:
        print("\n⚠️  Some checks failed. Please fix the issues above.")
        print("\n💡 Common fixes:")
        print("   - Run: pip install -r requirements.txt")
        print("   - Edit .env with your API keys")
        print("   - Ensure all files are present")

    return 0 if all_passed else 1


if __name__ == "__main__":
    sys.exit(main())
