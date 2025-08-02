#!/bin/bash

# GitHub Repository Setup Script
# Creates a new GitHub repository and pushes local commits

set -e  # Exit on any error

REPO_NAME="mcp-dev-resources"
COMMIT_MESSAGE="Add MCP Developer Resources Database"

echo "🚀 Setting up GitHub repository..."

# Check if gh CLI is installed and authenticated
if ! command -v gh &> /dev/null; then
    echo "❌ GitHub CLI not found. Install with: brew install gh"
    exit 1
fi

# Check if authenticated
if ! gh auth status &> /dev/null; then
    echo "🔐 Please authenticate with GitHub CLI first:"
    echo "   gh auth login"
    exit 1
fi

# Stage and commit if there are changes
if [[ -n $(git status --porcelain) ]]; then
    echo "📝 Staging and committing changes..."
    git add README.md
    git commit -m "$COMMIT_MESSAGE"
else
    echo "✅ No changes to commit"
fi

# Create GitHub repository and set remote
echo "🌐 Creating GitHub repository: $REPO_NAME"
if gh repo create "$REPO_NAME" --public --source=. --remote=origin 2>/dev/null; then
    echo "✅ Repository created successfully"
else
    echo "⚠️  Repository might already exist, setting remote..."
    git remote add origin "https://github.com/$(gh api user --jq .login)/$REPO_NAME.git" 2>/dev/null || true
fi

# Set remote URL to HTTPS (avoids SSH key issues)
git remote set-url origin "https://github.com/$(gh api user --jq .login)/$REPO_NAME.git"

# Push to GitHub
echo "📤 Pushing to GitHub..."
git push -u origin master

echo ""
echo "🎉 Success! Repository is live at:"
echo "   https://github.com/$(gh api user --jq .login)/$REPO_NAME"