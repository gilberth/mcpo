#!/bin/bash

echo "🔧 Setting up automatic upstream synchronization with WebUI preservation..."

# Make scripts executable
chmod +x scripts/preserve-webui-changes.py

# Create the workflows directory if it doesn't exist
mkdir -p .github/workflows

# Verify the workflow file exists
if [ -f ".github/workflows/auto-sync-webui.yml" ]; then
    echo "✅ GitHub Actions workflow is ready"
else
    echo "❌ GitHub Actions workflow not found!"
    echo "Please ensure .github/workflows/auto-sync-webui.yml exists"
    exit 1
fi

# Add upstream remote if not exists
if ! git remote get-url upstream >/dev/null 2>&1; then
    echo "➕ Adding upstream remote..."
    git remote add upstream https://github.com/open-webui/mcpo.git
    git fetch upstream
    echo "✅ Upstream remote added"
else
    echo "✅ Upstream remote already exists"
    git fetch upstream
fi

# Test the WebUI preservation script
echo "🧪 Testing WebUI preservation script..."
if python3 scripts/preserve-webui-changes.py verify; then
    echo "✅ WebUI preservation script works correctly"
else
    echo "⚠️ WebUI integration may need attention"
    echo "Running auto-fix..."
    python3 scripts/preserve-webui-changes.py apply
fi

# Check current status vs upstream
BEHIND=$(git rev-list --count HEAD..upstream/main)
echo "📊 Repository status:"
echo "  Commits behind upstream: $BEHIND"

if [ $BEHIND -gt 0 ]; then
    echo "  ⚠️ There are $BEHIND new commits available from upstream"
    echo "  The GitHub Actions workflow will handle this automatically every Monday"
    echo "  Or you can trigger it manually from the Actions tab"
else
    echo "  ✅ Repository is up to date with upstream"
fi

# Commit the setup files
echo "💾 Committing setup files..."
git add .github/workflows/auto-sync-webui.yml
git add scripts/preserve-webui-changes.py
git add setup-auto-sync.sh

git commit -m "🤖 Add automatic upstream sync with WebUI preservation

- GitHub Actions workflow for weekly upstream sync
- Smart WebUI preservation script
- Automatic conflict resolution
- Docker build and functionality testing
- Automated PR creation with verification

Features:
- Preserves WebUI imports and router integration
- Tests all functionality before creating PR
- Handles merge conflicts intelligently
- Creates detailed PRs with test results
- Falls back to manual intervention if needed" || echo "No changes to commit"

echo ""
echo "🎉 Setup complete! Here's what was configured:"
echo ""
echo "✅ Automatic Sync Features:"
echo "   • Weekly Monday sync with upstream MCPO"
echo "   • Smart preservation of WebUI modifications"  
echo "   • Automatic conflict resolution for main.py"
echo "   • Docker build and functionality testing"
echo "   • Automated PR creation with detailed reports"
echo ""
echo "✅ Manual Tools:"
echo "   • scripts/preserve-webui-changes.py - For manual WebUI fixes"
echo "   • Manual workflow trigger available in GitHub Actions"
echo ""
echo "🔧 How it works:"
echo "   1. Every Monday at 6 AM UTC, GitHub Actions runs"
echo "   2. Fetches latest changes from upstream MCPO"
echo "   3. Intelligently merges while preserving your WebUI changes"
echo "   4. Tests the result (Docker build + WebUI functionality)"
echo "   5. Creates a PR with all verification results"
echo "   6. You review and merge the PR"
echo ""
echo "🚀 Next steps:"
echo "   1. Push these changes: git push origin main"
echo "   2. The workflow will run automatically every Monday"
echo "   3. You can also trigger it manually from GitHub Actions tab"
echo "   4. Check PRs created by github-actions[bot]"
echo ""
echo "🎯 Your WebUI changes are now protected and will be automatically preserved!"