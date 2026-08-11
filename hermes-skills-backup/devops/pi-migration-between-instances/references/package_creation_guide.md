---
name: pi-migration-package
description: Create portable migration packages for Pi Framework multi-skill configurations between instances
category: pi-cortex-leman-integration
---

# Pi Framework Migration Package

Create portable, self-contained packages for migrating Pi Framework configurations (skills, providers, API keys) between instances.

## When to Use

Use this skill when:
- Moving Pi configuration from one instance to another
- Deploying the same Pi setup across multiple environments (dev, staging, prod)
- Sharing standardized Pi configurations with team members
- Setting up new instances with pre-configured skills and providers

## Key Capabilities

- **Skill Migration**: Package one or multiple Pi skills (SKILL.md files)
- **Provider Configuration**: Template-based settings with masked API keys
- **Automated Setup**: Scripts that create directories, copy files, and validate configuration
- **Interactive Configuration**: Optional interactive prompts for API key setup
- **Validation**: Pre-flight and post-flight validation checks

## File Structure

A complete migration package has this structure:

```
pi-migration-package/
├── skills/                    # Pi skill directories
│   ├── skill-name-1/
│   │   └── SKILL.md
│   └── skill-name-2/
│       └── SKILL.md
├── settings.json              # Pi settings (template with masked keys)
├── migrate-pi.sh              # Main migration script
├── configure-pi-keys.sh       # Interactive API key setup
├── README.md                  # Quick start guide
└── MIGRATION-GUIDE.md         # Detailed migration steps
```

## Workflow

### Step 1: Create Package (Source Instance)

The `prepare-pi-package.sh` script automates package creation:

```bash
#!/bin/bash

PACKAGE_DIR="./pi-migration-package"
PI_DIR="$HOME/.feynman"

# Create package directory
rm -rf "$PACKAGE_DIR"
mkdir -p "$PACKAGE_DIR/skills"

# Copy skills (list specific skills to include)
SKILLS=("skill-name-1" "skill-name-2" "skill-name-3")

for skill in "${SKILLS[@]}"; do
    if [ -d "$PI_DIR/agent/skills/$skill" ]; then
        cp -r "$PI_DIR/agent/skills/$skill" "$PACKAGE_DIR/skills/"
    fi
done

# Create settings.json template with masked API keys
sed 's/"apiKey": "c55159[^"]*"/"apiKey": "VOTRE_CLE_API_ICI"/' \
    "$PI_DIR/settings.json" > "$PACKAGE_DIR/settings.json"

# Create migration and configuration scripts
# (see complete scripts below)

echo "Package created: $PACKAGE_DIR"
```

### Step 2: Transfer Package

```bash
# Option A: SCP
scp -r pi-migration-package/ user@new-instance:~/

# Option B: rsync
rsync -avz pi-migration-package/ user@new-instance:~/pi-migration-package/

# Option C: Archive
tar -czf pi-migration-package.tar.gz pi-migration-package/
```

### Step 3: Execute Migration (Target Instance)

The `migrate-pi.sh` script handles everything:

```bash
#!/bin/bash

# Verify Pi is installed
if ! command -v pi &> /dev/null; then
    echo "❌ Pi not installed. Run: npm install -g @feynman-foundation/pi"
    exit 1
fi

# Create Pi directories
mkdir -p "$HOME/.feynman/agent/skills"
mkdir -p "$HOME/.feynman/memory"
mkdir -p "$HOME/.feynman/sessions"

# Copy skills
cp -r ./skills/* "$HOME/.feynman/agent/skills/"

# Copy settings.json
cp ./settings.json "$HOME/.feynman/settings.json"

# Validate
if [ -f "$HOME/.feynman/settings.json" ]; then
    echo "✅ Migration complete"
    echo "Next: Configure API keys with ./configure-pi-keys.sh"
fi
```

### Step 4: Configure API Keys (Target Instance)

The `configure-pi-keys.sh` script provides interactive setup:

```bash
#!/bin/bash

SETTINGS_FILE="$HOME/.feynman/settings.json"

# Create backup
BACKUP_FILE="$SETTINGS_FILE.backup-$(date +%Y%m%d-%H%M%S)"
cp "$SETTINGS_FILE" "$BACKUP_FILE"

# Prompt for each provider key
echo "1. Provider 1 API Key:"
read -p "   Key: " KEY1
echo ""
echo "2. Provider 2 API Key:"
read -p "   Key: " KEY2

# Update settings.json with actual keys
sed "s/VOTRE_CLE_API_ICI/$KEY1/g" "$SETTINGS_FILE" > "$SETTINGS_FILE.tmp"
mv "$SETTINGS_FILE.tmp" "$SETTINGS_FILE"

echo "✅ API keys configured"
echo "Backup saved to: $BACKUP_FILE"
```

### Step 5: Validate

```bash
# Check Pi configuration
pi --config

# Test a skill
pi --skill skill-name-1 "Test"

# List available skills
pi --skills
```

## Complete Migration Script

**migrate-pi.sh** (full version):

```bash
#!/bin/bash

echo "🚀 Pi Migration"
echo "=============="

# Verify Pi installation
if ! command -v pi &> /dev/null; then
    echo "❌ Pi not installed"
    echo "Install: npm install -g @feynman-foundation/pi"
    exit 1
fi

PI_DIR="$HOME/.feynman"
SKILLS_DIR="$PI_DIR/agent/skills"

# Create directories
echo "📁 Creating directories..."
mkdir -p "$PI_DIR/agent/skills"
mkdir -p "$PI_DIR/memory"
mkdir -p "$PI_DIR/sessions"
mkdir -p "$PI_DIR/npm-global"
mkdir -p "$PI_DIR/.state"

# Copy skills
if [ -d "./skills" ]; then
    echo "📦 Copying skills..."
    cp -r ./skills/* "$SKILLS_DIR/"
    SKILLS_COUNT=$(ls -1 "$SKILLS_DIR" 2>/dev/null | wc -l)
    echo "✅ $SKILLS_COUNT skills copied"
fi

# Copy settings.json
if [ -f "./settings.json" ]; then
    echo "⚙️  Installing settings.json..."
    cp ./settings.json "$PI_DIR/settings.json"
    
    # Check if template
    if grep -q "VOTRE_CLE" "$PI_DIR/settings.json"; then
        echo "⚠️  Template detected - API keys need configuration"
        echo ""
        read -p "Configure API keys now? (y/n) : " CONFIGURE
        if [[ "$CONFIGURE" == "y" ]]; then
            ./configure-pi-keys.sh
        fi
    fi
fi

# Validate
echo ""
echo "🔍 Validating..."

if [ -f "$PI_DIR/settings.json" ]; then
    echo "✅ settings.json: present"
fi

SKILLS_PRESENT=$(find "$SKILLS_DIR" -name "SKILL.md" 2>/dev/null | wc -l)
echo "✅ Skills: $SKILLS_PRESENT installed"

echo ""
echo "✅ Migration complete"
```

## Settings JSON Template

Create a template with placeholders for API keys:

```json
{
  "modelSpec": "provider:model-name",
  "thinkingLevel": "high",
  "modelRegistry": {
    "provider1": {
      "apiKey": "VOTRE_CLE_PROVIDER1_ICI",
      "baseUrl": "https://api.provider1.com",
      "models": ["model-1", "model-2"]
    },
    "provider2": {
      "apiKey": "VOTRE_CLE_PROVIDER2_ICI",
      "baseUrl": "https://api.provider2.com",
      "models": ["model-x", "model-y"]
    }
  },
  "skills": [
    "skill-name-1",
    "skill-name-2"
  ]
}
```

## Validation Script

**validate-pi-package.sh**:

```bash
#!/bin/bash

echo "🔍 Validating Pi Package"
echo "======================"

PACKAGE_DIR="."

# Check skills
echo "📊 Skills:"
find "$PACKAGE_DIR/skills" -name "SKILL.md" | while read skill; do
    echo "  ✅ $(basename $(dirname $skill))"
done

# Check settings.json
echo ""
echo "⚙️  Settings:"
if [ -f "$PACKAGE_DIR/settings.json" ]; then
    if python3 -m json.tool "$PACKAGE_DIR/settings.json" > /dev/null 2>&1; then
        echo "  ✅ settings.json: valid JSON"
    else
        echo "  ❌ settings.json: invalid JSON"
    fi
else
    echo "  ❌ settings.json: missing"
fi

# Check scripts
echo ""
echo "🔧 Scripts:"
for script in "migrate-pi.sh" "configure-pi-keys.sh"; do
    if [ -f "$PACKAGE_DIR/$script" ]; then
        if [ -x "$PACKAGE_DIR/$script" ]; then
            echo "  ✅ $script: executable"
        else
            echo "  ⚠️  $script: not executable (chmod +x $script)"
        fi
    else
        echo "  ❌ $script: missing"
    fi
done

echo ""
echo "✅ Validation complete"
```

## Documentation Templates

**README.md** (Quick Start):

```markdown
# Pi Migration Package

Contains Pi framework configuration for [Project Name].

## Quick Install

1. Transfer package:
   ```bash
   scp -r pi-migration-package/ user@instance:~/
   ```

2. Install Pi:
   ```bash
   npm install -g @feynman-foundation/pi
   ```

3. Run migration:
   ```bash
   cd pi-migration-package
   ./migrate-pi.sh
   ```

4. Configure keys:
   ```bash
   ./configure-pi-keys.sh
   ```

5. Verify:
   ```bash
   pi --config
   ```

## Contents

- Skills: N skills included
- Providers: X providers configured
- Scripts: Automated migration setup
```

## Pitfalls & Lessons Learned

### DO NOT expose real API keys in package

Always mask API keys in `settings.json`:

```bash
# BAD - Real keys in package
cp "$PI_DIR/settings.json" "$PACKAGE_DIR/settings.json"

# GOOD - Masked template
sed 's/"apiKey": "[^"]*"/"apiKey": "VOTRE_CLE_ICI"/g' \
    "$PI_DIR/settings.json" > "$PACKAGE_DIR/settings.json"
```

### DO make scripts executable

Scripts won't run without execute permissions:

```bash
# Set permissions in package
chmod +x "$PACKAGE_DIR"/*.sh

# Document requirement in README
echo "Run: chmod +x pi-migration-package/*.sh"
```

### DO validate before transfer

Run validation on source before transferring:

```bash
./validate-pi-package.sh

# Only transfer if validation passes
scp -r pi-migration-package/ user@instance:~/
```

### DO NOT hardcode paths

Use `$HOME` for portability:

```bash
# BAD - Hardcoded
PI_DIR="/home/tars/.feynman"

# GOOD - Portable
PI_DIR="$HOME/.feynman"
```

### DO verify Pi installation on target

Pi might not be installed on target instance:

```bash
if ! command -v pi &> /dev/null; then
    echo "❌ Pi not installed"
    echo "Install: npm install -g @feynman-foundation/pi"
    exit 1
fi
```

### DO create backups before overwriting

Always backup existing configuration:

```bash
BACKUP_FILE="$SETTINGS_FILE.backup-$(date +%Y%m%d-%H%M%S)"
cp "$SETTINGS_FILE" "$BACKUP_FILE"
echo "Backup saved: $BACKUP_FILE"
```

### DO NOT assume directory structure exists

Create directories first:

```bash
mkdir -p "$PI_DIR/agent/skills"
mkdir -p "$PI_DIR/memory"
mkdir -p "$PI_DIR/sessions"
```

## Real-World Example: Cortex Leman Migration

From this conversation, the Cortex Leman package included:

**Skills (4 agents):**
- `l-architecte-lemanique` (CSO)
- `le-gardien-des-normes` (Compliance Officer)
- `le-narrateur-augmente` (Brand & UI)
- `l-oeil-de-cortex` (Data Visionary)

**Providers (3 providers):**
- ZAI/GLM (glm-4.7, glm-5) - Primary
- Kie.ai (nano-banana) - Image generation
- OpenRouter (deepseek, claude) - Fallback

**Package size:** 96K (9 files)

**Migration time:** ~5 minutes (including interactive key configuration)

## Use Cases

1. **Development to Production Migration**
   - Create package from dev instance
   - Transfer to production server
   - Configure production API keys
   - Deploy to production environment

2. **Team Onboarding**
   - Create standardized package with core skills
   - Share with new team members
   - Each member configures their own API keys
   - Consistent setup across team

3. **Multi-Environment Setup**
   - Package for staging environment
   - Package for production environment
   - Separate API keys per environment
   - Same skills, different providers/keys

4. **Disaster Recovery**
   - Create regular package exports
   - Store in version control or backup system
   - Quick restore to new instance if needed
   - Skills and configuration preserved

## Related Skills

- `pi-cortex-leman-integration` - Complete Pi setup for Cortex Leman
- `landing-page-creation` - Web development and deployment
- `docker-infrastructure` - Container-based deployments

## Commands Reference

```bash
# On source instance
./prepare-pi-package.sh    # Create migration package
./validate-pi-package.sh   # Validate package

# Transfer
scp -r pi-migration-package/ user@target:~/

# On target instance
cd pi-migration-package
./migrate-pi.sh            # Execute migration
./configure-pi-keys.sh     # Setup API keys

# Verify
pi --config                 # Check configuration
pi --skills                 # List skills
pi --skill skill-name       # Test a skill
```

## Support

- Pi Documentation: https://github.com/feynman-foundation/pi
- Pi Settings: `~/.feynman/settings.json`
- Pi Skills: `~/.feynman/agent/skills/`
