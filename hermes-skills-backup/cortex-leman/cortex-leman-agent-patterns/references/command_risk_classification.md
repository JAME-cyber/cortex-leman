---
name: command-risk-classification
category: cortex-leman
description: Command Risk Classification for Cortex Leman - Safety layer preventing dangerous command execution
---

# Command Risk Classification

## OVERVIEW

Safety layer for Cortex Leman agents that classifies command risks BEFORE execution. Prevents dangerous operations, enforces manual approval for critical operations, and provides audit trail.

Inspired by **12 Agentic Harness Patterns** - Command Risk Classification.

---

## WHEN TO USE

Use this skill when:
- Executing terminal commands via agents
- Running scripts with elevated permissions
- Performing destructive operations (rm, dd, format)
- Modifying system configurations
- Accessing sensitive data

---

## RISK LEVELS

### Level 1: LOW RISK (Safe)
- Read-only operations
- File reading (read_file)
- Search operations (search_files)
- Browser snapshots
- Database queries (SELECT)

**Examples:**
```python
read_file("/path/to/file")  # SAFE
search_files("pattern", path=".")  # SAFE
browser_snapshot()  # SAFE
```

### Level 2: MEDIUM RISK (Moderate)
- Write operations
- File creation/modification (write_file)
- File patching (patch)
- Database modifications (INSERT, UPDATE)
- Browser interactions (click, type)

**Examples:**
```python
write_file("/path/to/file", content)  # MEDIUM
patch("/path/to/file", old="X", new="Y")  # MEDIUM
browser_click("@e12")  # MEDIUM
```

### Level 3: HIGH RISK (Dangerous)
- System changes
- Terminal commands (terminal)
- Code execution (execute_code)
- Process management
- API calls with side effects

**Examples:**
```python
terminal("sudo apt-get install package")  # HIGH
execute_code("import os; os.system('rm -rf /')")  # HIGH
process("kill", session_id="12345")  # HIGH
```

### Level 4: CRITICAL RISK (Destructive)
- Irreversible operations
- Destructive commands (rm -rf, dd, mkfs)
- System shutdown/reboot
- Database deletion (DROP TABLE, DROP DATABASE)
- Production environment changes

**Examples:**
```python
terminal("rm -rf /")  # CRITICAL
terminal("dd if=/dev/zero of=/dev/sda")  # CRITICAL
terminal("systemctl poweroff")  # CRITICAL
```

---

## IMPLEMENTATION

### Risk Classification Matrix

```python
# risk_matrix.py

from enum import Enum
from typing import Dict, List

class CommandRisk(Enum):
    LOW = 1
    MEDIUM = 2
    HIGH = 3
    CRITICAL = 4

RISK_MATRIX: Dict[str, CommandRisk] = {
    # Terminal commands
    "terminal": CommandRisk.HIGH,
    "execute_code": CommandRisk.HIGH,
    "process": CommandRisk.HIGH,

    # File operations
    "write_file": CommandRisk.MEDIUM,
    "patch": CommandRisk.MEDIUM,
    "read_file": CommandRisk.LOW,
    "search_files": CommandRisk.LOW,

    # Browser operations
    "browser_click": CommandRisk.MEDIUM,
    "browser_type": CommandRisk.MEDIUM,
    "browser_snapshot": CommandRisk.LOW,
    "browser_navigate": CommandRisk.MEDIUM,

    # Database operations
    "db_query": CommandRisk.MEDIUM,  # INSERT/UPDATE/DELETE
    "db_select": CommandRisk.LOW,     # SELECT only
}

# Critical command patterns (CRITICAL RISK)
CRITICAL_PATTERNS: List[str] = [
    "rm -rf",
    "dd if=/dev/zero",
    "mkfs",
    "format",
    "DROP DATABASE",
    "DROP TABLE",
    "TRUNCATE TABLE",
    "DELETE FROM",
    "shutdown",
    "reboot",
    "systemctl stop",
    "systemctl poweroff",
    "rm -r /",
    "rm -f /",
]

# Dangerous command patterns (HIGH RISK)
DANGEROUS_PATTERNS: List[str] = [
    "sudo",
    "su",
    "chmod 777",
    "chown root",
    "> /dev/sd",
    ":(){ :|:& };:",  # Fork bomb
    "wget | sh",
    "curl | bash",
    "eval $(",
]
```

### Risk Validator

```python
# risk_validator.py

import re
from typing import Tuple
from risk_matrix import CommandRisk, RISK_MATRIX, CRITICAL_PATTERNS, DANGEROUS_PATTERNS

class RiskValidator:
    def __init__(self):
        self.audit_log = []

    def classify_command(self, tool_name: str, command: str) -> CommandRisk:
        """
        Classify command risk level.

        Args:
            tool_name: Name of tool being used
            command: Command string to classify

        Returns:
            CommandRisk enum (LOW, MEDIUM, HIGH, CRITICAL)
        """
        # Check for CRITICAL patterns first
        for pattern in CRITICAL_PATTERNS:
            if pattern in command:
                return CommandRisk.CRITICAL

        # Check for DANGEROUS patterns
        for pattern in DANGEROUS_PATTERNS:
            if pattern in command:
                return CommandRisk.HIGH

        # Use matrix classification
        base_risk = RISK_MATRIX.get(tool_name, CommandRisk.MEDIUM)

        return base_risk

    def validate_command(self, tool_name: str, command: str) -> Tuple[bool, str, CommandRisk]:
        """
        Validate command before execution.

        Args:
            tool_name: Name of tool being used
            command: Command string to validate

        Returns:
            Tuple of (allowed: bool, reason: str, risk: CommandRisk)
        """
        risk = self.classify_command(tool_name, command)

        # CRITICAL RISK - NEVER ALLOW
        if risk == CommandRisk.CRITICAL:
            reason = f"CRITICAL RISK: '{command}' contains destructive pattern. Manual approval required."
            return False, reason, risk

        # HIGH RISK - Manual approval required
        if risk == CommandRisk.HIGH:
            reason = f"HIGH RISK: '{command}' requires manual approval before execution."
            return False, reason, risk

        # MEDIUM RISK - Check for specific restrictions
        if risk == CommandRisk.MEDIUM:
            if self.has_unsafe_dependencies(command):
                reason = f"MEDIUM RISK: '{command}' contains unsafe dependencies."
                return False, reason, risk
            reason = "ALLOWED (MEDIUM RISK): Operation approved."
            return True, reason, risk

        # LOW RISK - Always allow
        reason = "ALLOWED (LOW RISK): Safe operation."
        return True, reason, risk

    def has_unsafe_dependencies(self, command: str) -> bool:
        """
        Check if command has unsafe dependencies.

        Args:
            command: Command string to check

        Returns:
            True if unsafe, False otherwise
        """
        unsafe_patterns = [
            r"rm\s+/",  # rm /
            r">\s*/dev/",  # Write to device
            r"chmod\s+777",  # chmod 777
        ]

        for pattern in unsafe_patterns:
            if re.search(pattern, command, re.IGNORECASE):
                return True

        return False

    def log_validation(self, tool_name: str, command: str, allowed: bool, reason: str, risk: CommandRisk):
        """
        Log validation to audit trail.

        Args:
            tool_name: Name of tool being used
            command: Command string
            allowed: Whether command was allowed
            reason: Validation reason
            risk: Risk level
        """
        log_entry = {
            'timestamp': datetime.now().isoformat(),
            'tool_name': tool_name,
            'command': command,
            'allowed': allowed,
            'reason': reason,
            'risk': risk.name,
        }

        self.audit_log.append(log_entry)

        # Also log to file
        with open('/var/log/cortex-leman/risk_validations.log', 'a') as f:
            f.write(json.dumps(log_entry) + '\n')

    def execute_with_safety(self, tool_name: str, command: str, tool_executor: callable):
        """
        Execute command with safety validation.

        Args:
            tool_name: Name of tool being used
            command: Command string to execute
            tool_executor: Function to execute the command

        Returns:
            Result of command execution

        Raises:
            SecurityError: If command is not allowed
        """
        # Validate before execution
        allowed, reason, risk = self.validate_command(tool_name, command)

        # Log validation
        self.log_validation(tool_name, command, allowed, reason, risk)

        # Check if allowed
        if not allowed:
            raise SecurityError(f"Command not allowed: {reason}")

        # Execute with monitoring
        try:
            result = tool_executor(command)
            return result
        except Exception as e:
            # Log execution error
            self.log_validation(tool_name, command, False, f"EXECUTION ERROR: {str(e)}", risk)
            raise
```

### Usage Example

```python
# example_usage.py

from risk_validator import RiskValidator
from terminal import terminal  # Hermes Agent terminal tool

# Initialize validator
validator = RiskValidator()

# Safe command (LOW RISK)
try:
    result = validator.execute_with_safety(
        tool_name="read_file",
        command="read_file('/path/to/file')",
        tool_executor=read_file
    )
    print(f"✓ Command executed: {result}")
except SecurityError as e:
    print(f"✗ Security error: {e}")

# Medium risk command (MEDIUM RISK)
try:
    result = validator.execute_with_safety(
        tool_name="write_file",
        command="write_file('/path/to/file', content)",
        tool_executor=write_file
    )
    print(f"✓ Command executed: {result}")
except SecurityError as e:
    print(f"✗ Security error: {e}")

# High risk command (HIGH RISK) - Requires manual approval
try:
    result = validator.execute_with_safety(
        tool_name="terminal",
        command="sudo apt-get install package",
        tool_executor=terminal
    )
    print(f"✓ Command executed: {result}")
except SecurityError as e:
    print(f"✗ Security error: {e}")
    # Manual approval workflow would go here
```

---

## BEST PRACTICES

### DO
- Always validate commands before execution
- Log all validations (allowed + blocked)
- Use audit trail for compliance
- Configure approval workflows for HIGH/CRITICAL risk
- Review audit logs regularly

### DON'T
- Skip validation for "trusted" commands
- Allow sudo commands without approval
- Ignore CRITICAL RISK patterns
- Disable logging for performance
- Modify risk matrices without review

---

## SECURITY CONSIDERATIONS

### Attack Vectors

**Command Injection:**
```python
# VULNERABLE
command = f"cat {user_input}"
terminal(command)

# SECURE
command = ["cat", user_input]
terminal(command)
```

**Path Traversal:**
```python
# VULNERABLE
file_path = f"/data/{user_file}"
read_file(file_path)

# SECURE
file_path = os.path.normpath(f"/data/{user_file}")
if not file_path.startswith("/data/"):
    raise SecurityError("Path traversal detected")
read_file(file_path)
```

### Compliance Requirements

**OWASP GenAI:**
- #4: Model Hallucination - Validate outputs
- #5: Model Denial of Service - Rate limit commands
- #7: Data Poisoning - Validate inputs

**AI Act:**
- Article 14: Human Oversight - Manual approval for critical
- Article 15: Accuracy, Robustness, Cybersecurity - Validate commands
- Article 16: Transparency - Log all operations

**GDPR/LPD:**
- Article 32: Security of processing - Implement risk validation
- Article 35: Data protection impact assessment - Audit trail required

---

## TESTING

### Unit Tests

```python
# test_risk_validator.py

import pytest
from risk_validator import RiskValidator, CommandRisk

def test_low_risk_commands():
    validator = RiskValidator()

    allowed, _, risk = validator.validate_command("read_file", "read_file('/path/to/file')")
    assert allowed is True
    assert risk == CommandRisk.LOW

def test_high_risk_commands():
    validator = RiskValidator()

    allowed, reason, risk = validator.validate_command("terminal", "sudo apt-get install package")
    assert allowed is False
    assert "manual approval" in reason.lower()
    assert risk == CommandRisk.HIGH

def test_critical_risk_patterns():
    validator = RiskValidator()

    allowed, reason, risk = validator.validate_command("terminal", "rm -rf /")
    assert allowed is False
    assert "destructive" in reason.lower()
    assert risk == CommandRisk.CRITICAL

def test_audit_logging():
    validator = RiskValidator()

    validator.log_validation("read_file", "read_file('/path/to/file')", True, "ALLOWED", CommandRisk.LOW)

    assert len(validator.audit_log) == 1
    assert validator.audit_log[0]['allowed'] is True
    assert validator.audit_log[0]['risk'] == "LOW"
```

---

## INTEGRATION WITH CORTEX LEMAN

### Le Gardien des Normes

```python
# Integration: le-gardien-des-normes with risk validation

from risk_validator import RiskValidator

class LeGardienDesNormes:
    def __init__(self):
        self.validator = RiskValidator()

    def audit_system(self, system_config: dict) -> AuditResult:
        """
        Audit system with safety validation.
        """
        # Validate system config access (LOW RISK)
        try:
            config = self.validator.execute_with_safety(
                tool_name="read_file",
                command=f"read_file('{system_config['path']}')",
                tool_executor=read_file
            )
        except SecurityError as e:
            return AuditResult(status="FAILED", error=str(e))

        # Run audit checks (MEDIUM RISK)
        try:
            result = self.validator.execute_with_safety(
                tool_name="execute_code",
                command=self.audit_code(system_config),
                tool_executor=execute_code
            )
        except SecurityError as e:
            return AuditResult(status="FAILED", error=str(e))

        return result
```

### L'Ingénieur de Flux

```python
# Integration: l-ingenieur-de-flux with risk validation

class LIngenieurDeFlux:
    def __init__(self):
        self.validator = RiskValidator()

    def deploy_workflow(self, workflow: Workflow) -> DeploymentResult:
        """
        Deploy workflow with safety validation.
        """
        # Validate deployment (HIGH RISK)
        try:
            result = self.validator.execute_with_safety(
                tool_name="terminal",
                command=f"docker-compose up -d {workflow.name}",
                tool_executor=terminal
            )
        except SecurityError as e:
            return DeploymentResult(status="FAILED", error=str(e))

        return result
```

---

## MONITORING & ALERTS

### Key Metrics

**Risk Distribution:**
```python
# Monitor risk distribution

risk_counts = {
    'LOW': 0,
    'MEDIUM': 0,
    'HIGH': 0,
    'CRITICAL': 0,
}

for log in validator.audit_log:
    risk_counts[log['risk']] += 1

# Alert if HIGH/CRITICAL spikes
if risk_counts['HIGH'] > 10 or risk_counts['CRITICAL'] > 0:
    send_alert("HIGH/CRITICAL risk spike detected")
```

**Blocked Commands:**
```python
# Track blocked commands

blocked_commands = [
    log for log in validator.audit_log if not log['allowed']
]

if len(blocked_commands) > 5:
    send_alert(f"{len(blocked_commands)} commands blocked today")
```

---

## VERSION HISTORY

**v1.0 (April 2026):**
- Initial release
- Risk matrix: LOW, MEDIUM, HIGH, CRITICAL
- Audit trail logging
- Command validation
- Integration with Cortex Leman agents

---

**Created by:** Hermes Agent - Cortex Leman Team
**Inspired by:** 12 Agentic Harness Patterns (generativeprogrammer.com)
**Standards:** OWASP GenAI v1.0, AI Act 2026, GDPR, LPD
