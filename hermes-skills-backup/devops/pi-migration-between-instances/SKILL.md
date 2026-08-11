---
name: pi-migration-between-instances
description: Migrate complete Pi Framework configuration between separate Linux instances. Package skills, settings, and configuration for transfer via SCP or cloud upload. Tested on Pi v0.65.2+ for Cortex Leman multi-agent systems. See references/package_creation_guide.md for detailed package structure and interactive setup.
---

# Pi Migration Between Instances

Migrate complete Pi Framework configuration between separate Linux instances. Package skills, settings, and configuration for transfer via SCP or cloud upload.

## Use Cases

- Migrating Pi setup from development to production
- Replicating multi-agent configuration across instances
- Backing up Pi skills and settings
- Deploying Cortex Leman agents to new infrastructure

## Prerequisites

- **Source instance**: Pi installed with skills to migrate
- **Target instance**: SSH access or ability to download files
- **Network**: SCP connectivity or internet for cloud upload

## Quick Start (5 minutes)

### On SOURCE instance

1. **Create migration package**:
   ```bash
   cd ~
   # Package directory: ~/cortex-leman-pi-package/
   # Contains: skills/, settings.json, scripts
   ```

2. **Create archive**:
   ```bash
   tar -czf cortex-leman-pi-package-$(date +%Y%m%d-%H%M%S).tar.gz cortex-leman-pi-package/
   ```

3. **Transfer to target**:
   ```bash
   # Option A: SCP (requires SSH)
   scp cortex-leman-pi-package-*.tar.gz user@TARGET_IP:~/
   
   # Option B: Cloud upload (no SSH needed)
   curl --upload-file cortex-leman-pi-package-*.tar.gz https://transfer.sh/cortex-leman-pi-package.tar.gz
   ```

### On TARGET instance

1. **Extract archive**:
   ```bash
   tar -xzf cortex-leman-pi-package-*.tar.gz
   ```

2. **Install Pi**:
   ```bash
   npm install -g @feynman-foundation/pi
   pi --version
   ```

3. **Run migration**:
   ```bash
   cd ~/cortex-leman-pi-package
   ./migrate-pi.sh
   ```

4. **Configure API keys**:
   ```bash
   ./configure-pi-keys.sh
   ```

5. **Verify**:
   ```bash
   pi --config
   # Test a skill
   pi l-architecte-lemanique "Test migration"
   ```

## Package Structure

```
cortex-leman-pi-package/
├── skills/
│   ├── l-architecte-lemanique/     # CSO agent
│   ├── le-gardien-des-normes/       # Compliance agent
│   ├── le-narrateur-augmente/       # Brand/UI agent
│   └── l-oeil-de-cortex/            # Data agent
├── settings.json                    # Pi configuration template
├── migrate-pi.sh                     # Migration script
├── configure-pi-keys.sh             # API key configuration
└── README.md
```

## Migration Script Details

### migrate-pi.sh

Automatically:
- Creates `~/.feynman/` directory structure
- Copies skills to `~/.feynman/agent/skills/`
- Sets correct permissions (755)
- Validates package integrity

### configure-pi-keys.sh

Interactive prompts for:
- **ZAI/GLM API key** (primary models: glm-4.7, glm-5)
- **Kie.ai API key** (images: nano-banana)
- **OpenRouter API key** (fallback: deepseek, claude)

Updates `~/.feynman/settings.json` with provided keys.

## Transfer Methods

### SCP (Recommended for LAN)

```bash
# From SOURCE
scp cortex-leman-pi-package-*.tar.gz user@TARGET_IP:~/

# Example
scp cortex-leman-pi-package-*.tar.gz tars@172.16.1.1:~/
```

### Cloud Upload (No SSH required)

```bash
# Upload to Transfer.sh (14-day retention)
curl --upload-file cortex-leman-pi-package-*.tar.gz https://transfer.sh/cortex-leman-pi-package.tar.gz

# Returns download URL to use on target instance
```

### Alternative Cloud Services

- **Dropbox/Drive**: Upload, share link, `wget` on target
- **S3**: `aws s3 cp` for cloud deployments
- **Internal file server**: Copy to shared mount point

## Verification Checklist

After migration on TARGET:

- [ ] Pi version matches expected
  ```bash
  pi --version
  ```

- [ ] Skills directory populated
  ```bash
  ls -la ~/.feynman/agent/skills/
  ```

- [ ] Configuration valid
  ```bash
  pi --config
  ```

- [ ] Test one skill works
  ```bash
  pi <skill-name> "Test message"
  ```

- [ ] API keys configured (if using provider models)

## Troubleshooting

### Permission denied on scripts

```bash
chmod +x ~/cortex-leman-pi-package/*.sh
```

### Skills not recognized

```bash
chmod -R 755 ~/.feynman/agent/skills/
pi list  # Refresh skill cache
```

### API keys missing

```bash
cd ~/cortex-leman-pi-package
./configure-pi-keys.sh
```

### SCP connection refused

- Check SSH enabled on target: `systemctl status ssh`
- Verify IP address: `ip addr show` on target
- Check firewall: `sudo ufw status`

### Tar extraction fails

- Verify archive integrity: `tar -tzf archive.tar.gz`
- Re-create archive on source if corrupted

## Advanced Usage

### Selective Migration

To migrate only specific skills:

```bash
# Manually copy specific skill directory
scp -r ~/cortex-leman-pi-package/skills/l-architecte-lemanique/ \
  user@TARGET_IP:~/.feynman/agent/skills/
```

### Custom Settings

Edit `settings.json` before running `configure-pi-keys.sh`:

```json
{
  "providers": {
    "zai": {
      "apiKey": "YOUR_KEY_HERE",
      "models": ["glm-4.7", "glm-5"]
    }
  }
}
```

### Multi-Instance Deployment

For deploying to multiple targets:

```bash
# Create archive once
tar -czf cortex-leman-pi-package-$(date +%Y%m%d).tar.gz cortex-leman-pi-package/

# Deploy to multiple instances
for target in target1@192.168.1.10 target2@192.168.1.11; do
  scp cortex-leman-pi-package-*.tar.gz $target:~/
  ssh $target "tar -xzf cortex-leman-pi-package-*.tar.gz && cd ~/cortex-leman-pi-package && ./migrate-pi.sh"
done
```

## Best Practices

1. **Test migration** on non-production instance first
2. **Archive source** before migration: `cp -r ~/.feynman ~/.feynman-backup`
3. **Document API keys** securely (password manager, not code)
4. **Version control** skill configurations in separate repo
5. **Automate** frequent migrations with scripts
6. **Monitor** target instance after migration for errors

## Security Considerations

- **Never commit** API keys to version control
- **Secure transfer**: Use SCP over SSH, avoid unencrypted HTTP
- **Limit permissions**: Skills should be 755, not 777
- **Validate archive**: Check checksum before extraction
- **Isolate instances**: Use different API keys per environment (dev/staging/prod)

## Cortex Leman Specific

For Cortex Leman multi-agent systems:

- **4 core skills**: CSO, Compliance, Brand, Data
- **Optional skill**: L'Ingénieur de Flux (automation)
- **Decision**: Excluded from Pi package to maintain instance separation
- **Testing**: Use `pi l-architecte-lemanique "Test"` to verify

## Related Skills

- `pi-migration-package`: Creates portable Pi migration packages
- `pi-integration-cortex-leman`: Complete Pi Framework integration
- `cortex-leman-docker-infrastructure`: Docker-based deployment
