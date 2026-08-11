---
name: single-purpose-tool-design
category: cortex-leman
description: Single-Purpose Tool Design pattern for Cortex Leman - Decompose monolithic skills into focused micro-tools
---

# Single-Purpose Tool Design

## OVERVIEW

Design pattern that decomposes monolithic skills into single-purpose micro-tools. Each tool does ONE thing well, making code maintainable, testable, and composable.

Inspired by **12 Agentic Harness Patterns** - Single-Purpose Tool Design.

---

## PROBLEM STATEMENT

### Before: Monolithic Skills

**Problem: Skills with too many responsibilities**

```python
# MONOLITHIC SKILL (BAD)
class LeGardienDesNormes:
    def __init__(self):
        self.tools = []

    def audit_system(self, system):
        """
        Audits entire system - does EVERYTHING:
        - Validates GDPR
        - Checks OWASP GenAI
        - Verifies AI Act
        - Audits LPD
        - Tests prompt injection
        - Generates report
        - Sends email
        - Updates database
        """
        # 500+ lines of mixed responsibilities
        gdpr_result = self.validate_gdpr(system)
        owasp_result = self.check_owasp_genai(system)
        aifact_result = self.verify_aifact(system)
        lpd_result = self.audit_lpd(system)
        prompt_result = self.test_prompts(system)
        report = self.generate_report([gdpr_result, owasp_result, ...])
        self.send_email(report)
        self.update_database(report)
        return report
```

**Problems:**
- ❌ Hard to test (too many responsibilities)
- ❌ Hard to maintain (500+ lines mixed)
- ❌ Hard to reuse (can't use just GDPR validation)
- ❌ Hard to understand (what does this do?)
- ❌ Hard to replace (if OWASP check breaks, everything breaks)

---

## SOLUTION: SINGLE-PURPOSE TOOLS

### After: Single-Purpose Tools

```python
# SINGLE-PURPOSE TOOLS (GOOD)

# Tool 1: Validate GDPR ONLY
class GDPRValidator:
    """Single responsibility: Validate GDPR compliance"""
    def validate(self, data: dict) -> ComplianceResult:
        # GDPR validation logic ONLY
        pass

# Tool 2: Check OWASP GenAI ONLY
class OWASPChecker:
    """Single responsibility: Check OWASP GenAI"""
    def check(self, ai_system: dict) -> OWASPResult:
        # OWASP GenAI check ONLY
        pass

# Tool 3: Verify AI Act ONLY
class AIActVerifier:
    """Single responsibility: Verify AI Act compliance"""
    def verify(self, system: dict) -> ComplianceResult:
        # AI Act verification ONLY
        pass

# Tool 4: Audit LPD ONLY
class LPDAuditor:
    """Single responsibility: Audit LPD compliance"""
    def audit(self, data: dict) -> ComplianceResult:
        # LPD audit ONLY
        pass

# Tool 5: Test Prompt Injection ONLY
class PromptInjector:
    """Single responsibility: Test prompt injection"""
    def test(self, ai_system: dict) -> InjectionResult:
        # Prompt injection testing ONLY
        pass

# Tool 6: Generate Report ONLY
class ReportGenerator:
    """Single responsibility: Generate compliance report"""
    def generate(self, results: list[ComplianceResult]) -> Report:
        # Report generation ONLY
        pass

# Tool 7: Send Email ONLY
class EmailSender:
    """Single responsibility: Send email"""
    def send(self, email: Email) -> SendResult:
        # Email sending ONLY
        pass

# Tool 8: Update Database ONLY
class DatabaseUpdater:
    """Single responsibility: Update database"""
    def update(self, report: Report) -> UpdateResult:
        # Database update ONLY
        pass
```

### Orchestration (NOT a tool, but COMPOSER)

```python
# COMPOSER (not a tool, but orchestrates tools)
class ComplianceAuditor:
    """
    Composes single-purpose tools into workflows.
    NOT a tool itself - just orchestrates.
    """
    def __init__(self):
        # Inject single-purpose tools
        self.gdpr = GDPRValidator()
        self.owasp = OWASPChecker()
        self.aifact = AIActVerifier()
        self.lpd = LPDAuditor()
        self.injector = PromptInjector()
        self.reporter = ReportGenerator()
        self.emailer = EmailSender()
        self.updater = DatabaseUpdater()

    def full_audit(self, system: dict) -> AuditResult:
        """
        Full audit - COMPOSES tools, doesn't implement them.
        """
        # Use tools (not implement them)
        gdpr_result = self.gdpr.validate(system)
        owasp_result = self.owasp.check(system)
        aifact_result = self.aifact.verify(system)
        lpd_result = self.lpd.audit(system)
        prompt_result = self.injector.test(system)

        # Compose results
        report = self.reporter.generate([gdpr_result, owasp_result, ...])

        # Send notification
        email = Email(to="client@cortex-leman.ch", body=report)
        self.emailer.send(email)

        # Update database
        self.updater.update(report)

        return AuditResult(report=report, results=[gdpr_result, ...])
```

---

## BENEFITS

### ✅ Testable

```python
# EASY TO TEST EACH TOOL

# Test GDPR validator ONLY
def test_gdpr_validator():
    validator = GDPRValidator()
    result = validator.validate({"data_processing": "legal_basis"})
    assert result.compliant is True

# Test OWASP checker ONLY
def test_owasp_checker():
    checker = OWASPChecker()
    result = checker.check({"has_prompt_injection": False})
    assert result.vulnerable is False

# Test EACH tool independently
```

### ✅ Maintainable

```python
# EASY TO MAINTAIN EACH TOOL

# If GDPR validation breaks:
# - ONLY update GDPRValidator
# - NO need to touch OWASPChecker, AIActVerifier, etc.
# - CLEAR what needs fixing

# Example:
class GDPRValidator:
    def validate(self, data: dict) -> ComplianceResult:
        # 20 lines of GDPR validation ONLY
        # Easy to understand
        # Easy to fix
        # Easy to replace
        pass
```

### ✅ Reusable

```python
# EASY TO REUSE TOOLS

# Reuse GDPR validator in ANOTHER agent
class AnotherAgent:
    def __init__(self):
        # REUSE existing tool
        self.gdpr = GDPRValidator()

    def do_something_else(self):
        # Use GDPR validator here too
        result = self.gdpr.validate(some_data)
        return result
```

### ✅ Composable

```python
# EASY TO COMPOSE TOOLS DIFFERENTLY

# Compose tools for DIFFERENT workflows
class FastAudit:
    """Fast audit - only GDPR + OWASP"""
    def __init__(self):
        self.gdpr = GDPRValidator()  # Reuse tool
        self.owasp = OWASPChecker()  # Reuse tool

    def fast_audit(self, system: dict) -> AuditResult:
        # COMPOSE differently
        gdpr_result = self.gdpr.validate(system)
        owasp_result = self.owasp.check(system)
        return AuditResult(gdpr=gdpr_result, owasp=owasp_result)

class CompleteAudit:
    """Complete audit - all tools"""
    def __init__(self):
        # COMPOSE ALL tools
        self.gdpr = GDPRValidator()
        self.owasp = OWASPChecker()
        self.aifact = AIActVerifier()
        self.lpd = LPDAuditor()

    def complete_audit(self, system: dict) -> AuditResult:
        # COMPOSE differently
        gdpr_result = self.gdpr.validate(system)
        owasp_result = self.owasp.check(system)
        aifact_result = self.aifact.verify(system)
        lpd_result = self.lpd.audit(system)
        return AuditResult(all_results=[...])
```

### ✅ Replaceable

```python
# EASY TO REPLACE TOOLS

# If OWASP checker is outdated, REPLACE ONLY that tool
class NewOWASPChecker:
    """New OWASP GenAI checker (better version)"""
    def check(self, ai_system: dict) -> OWASPResult:
        # New implementation
        pass

# Update composer - NO need to change other tools
class ComplianceAuditor:
    def __init__(self):
        self.gdpr = GDPRValidator()  # Same
        self.owasp = NewOWASPChecker()  # REPLACED
        self.aifact = AIActVerifier()  # Same
        # ... rest same
```

---

## DESIGN PRINCIPLES

### 1. Single Responsibility Principle (SRP)

**Rule:** Each tool does ONE thing well.

```python
# BAD: Tool does multiple things
class MultiTool:
    def validate_gdpr(self): ...  # GDPR
    def check_owasp(self): ...   # OWASP
    def verify_aifact(self): ...  # AI Act

# GOOD: Each tool does one thing
class GDPRValidator:
    def validate(self): ...  # GDPR ONLY

class OWASPChecker:
    def check(self): ...  # OWASP ONLY

class AIActVerifier:
    def verify(self): ...  # AI Act ONLY
```

### 2. Open/Closed Principle (OCP)

**Rule:** Open for extension, closed for modification.

```python
# Extend WITHOUT modifying existing tools
# Create new tool for new requirement
class NewRequirementTool:
    """New requirement tool"""
    def do_something_new(self): ...

# Compose with existing tools
class EnhancedAuditor:
    def __init__(self):
        self.gdpr = GDPRValidator()  # Existing
        self.owasp = OWASPChecker()   # Existing
        self.new = NewRequirementTool()  # NEW
```

### 3. Dependency Injection (DI)

**Rule:** Inject tools, don't instantiate them inside.

```python
# BAD: Tool instantiates dependencies
class BadAuditor:
    def __init__(self):
        self.gdpr = GDPRValidator()  # Hard-coded dependency

# GOOD: Tools injected from outside
class GoodAuditor:
    def __init__(self, gdpr_validator, owasp_checker):
        self.gdpr = gdpr_validator  # Injected
        self.owasp = owasp_checker  # Injected

# Easy to test with mocks
def test_good_auditor():
    mock_gdpr = MockGDPRValidator()
    mock_owasp = MockOWASPChecker()
    auditor = GoodAuditor(mock_gdpr, mock_owasp)
    # Test with mocks
```

### 4. Interface Segregation (ISP)

**Rule:** Clients shouldn't depend on methods they don't use.

```python
# BAD: Large interface
class LargeToolInterface:
    def validate_gdpr(self): ...
    def check_owasp(self): ...
    def verify_aifact(self): ...
    def audit_lpd(self): ...
    # ... 20 more methods

# Client only needs GDPR validation, but depends on LARGE interface
class Client:
    def __init__(self, tool: LargeToolInterface):
        self.tool = tool
    def use_only_gdpr(self):
        self.tool.validate_gdpr()  # Only uses 1 method

# GOOD: Small interfaces
class GDPRValidatorInterface:
    def validate(self): ...  # ONLY GDPR

class Client:
    def __init__(self, gdpr_validator: GDPRValidatorInterface):
        self.gdpr = gdpr_validator
    def use_only_gdpr(self):
        self.gdpr.validate()  # Small interface
```

---

## CORTEX LEMAN REFACTORING

### Step 1: Identify Monolithic Skills

**Current Skills to Refactor:**

1. **le-gardien-des-normes** - Multiple compliance checks
2. **l-oeil-de-cortex** - Multiple data processing tasks
3. **l-ingenieur-de-flux** - Multiple automation tasks
4. **l-narrateur-augmente** - Multiple reporting tasks

### Step 2: Decompose into Single-Purpose Tools

**Example: Le Gardien des Normes Refactoring**

```python
# BEFORE: Monolithic
# ~/.hermes/skills/cortex-leman/le-gardien-des-normes/SKILL.md

class LeGardienDesNormes:
    def audit(self, system: dict) -> AuditResult:
        # 500+ lines of mixed responsibilities
        gdpr = self.validate_gdpr(system)
        owasp = self.check_owasp(system)
        aifact = self.verify_aifact(system)
        lpd = self.audit_lpd(system)
        # ... more mixed responsibilities
        return result

# AFTER: Single-Purpose Tools
# ~/.hermes/skills/cortex-leman/le-gardien-des-normes/tools/

# Tool 1: GDPR Validator
# ~/.hermes/skills/cortex-leman/le-gardien-des-normes/tools/gdpr-validator/SKILL.md
class GDPRValidator:
    def validate(self, data: dict) -> ComplianceResult:
        # GDPR validation ONLY (20 lines)
        pass

# Tool 2: OWASP GenAI Checker
# ~/.hermes/skills/cortex-leman/le-gardien-des-normes/tools/owasp-checker/SKILL.md
class OWASPChecker:
    def check(self, ai_system: dict) -> OWASPResult:
        # OWASP GenAI check ONLY (30 lines)
        pass

# Tool 3: AI Act Verifier
# ~/.hermes/skills/cortex-leman/le-gardien-des-normes/tools/aifact-verifier/SKILL.md
class AIActVerifier:
    def verify(self, system: dict) -> ComplianceResult:
        # AI Act verification ONLY (25 lines)
        pass

# Tool 4: LPD Auditor
# ~/.hermes/skills/cortex-leman/le-gardien-des-normes/tools/lpd-auditor/SKILL.md
class LPDAuditor:
    def audit(self, data: dict) -> ComplianceResult:
        # LPD audit ONLY (20 lines)
        pass

# Composer (orchestrates tools)
# ~/.hermes/skills/cortex-leman/le-gardien-des-normes/SKILL.md
class ComplianceAuditor:
    """
    Orchestrates single-purpose tools.
    NOT a tool itself.
    """
    def __init__(self):
        # Inject single-purpose tools
        self.gdpr = GDPRValidator()
        self.owasp = OWASPChecker()
        self.aifact = AIActVerifier()
        self.lpd = LPDAuditor()

    def full_audit(self, system: dict) -> AuditResult:
        """Composes tools - doesn't implement them."""
        # Use tools (not implement)
        gdpr_result = self.gdpr.validate(system)
        owasp_result = self.owasp.check(system)
        aifact_result = self.aifact.verify(system)
        lpd_result = self.lpd.audit(system)

        # Compose results
        return AuditResult(gdpr=gdpr_result, owasp=owasp_result, ...)
```

### Step 3: Directory Structure

```
~/.hermes/skills/cortex-leman/le-gardien-des-normes/
├── SKILL.md                           # Composer (orchestrator)
├── tools/
│   ├── gdpr-validator/
│   │   └── SKILL.md                 # Tool: GDPR ONLY
│   ├── owasp-checker/
│   │   └── SKILL.md                 # Tool: OWASP ONLY
│   ├── aifact-verifier/
│   │   └── SKILL.md                 # Tool: AI Act ONLY
│   └── lpd-auditor/
│       └── SKILL.md                 # Tool: LPD ONLY
└── tests/
    ├── test_gdpr_validator.py        # Test tool independently
    ├── test_owasp_checker.py        # Test tool independently
    ├── test_aifact_verifier.py      # Test tool independently
    └── test_lpd_auditor.py         # Test tool independently
```

---

## TESTING SINGLE-PURPOSE TOOLS

### Unit Tests (Test Each Tool)

```python
# Test GDPR validator ONLY
def test_gdpr_validator():
    validator = GDPRValidator()
    result = validator.validate({
        "data_processing": "legal_basis",
        "data_minimization": True,
    })
    assert result.compliant is True
    assert result.gaps == []

# Test OWASP checker ONLY
def test_owasp_checker():
    checker = OWASPChecker()
    result = checker.check({
        "has_prompt_injection_protection": True,
        "has_data_inference_protection": True,
    })
    assert result.vulnerable is False
    assert result.risks == []

# Test AI Act verifier ONLY
def test_aifact_verifier():
    verifier = AIActVerifier()
    result = verifier.verify({
        "is_high_risk": False,
        "has_human_oversight": True,
    })
    assert result.compliant is True
```

### Integration Tests (Test Composer)

```python
# Test composer (orchestrates tools)
def test_compliance_auditor():
    auditor = ComplianceAuditor()

    # Test full audit
    result = auditor.full_audit({
        "gdpr": {"legal_basis": True},
        "owasp": {"protection": True},
        "aifact": {"high_risk": False},
        "lpd": {"consent": True},
    })

    # Check all tools were used
    assert result.gdpr_result is not None
    assert result.owasp_result is not None
    assert result.aifact_result is not None
    assert result.lpd_result is not None
```

---

## COMPOSABILITY EXAMPLES

### Fast Audit (GDPR + OWASP)

```python
# Compose tools for fast audit
class FastAuditor:
    """Fast audit - only GDPR + OWASP"""
    def __init__(self):
        self.gdpr = GDPRValidator()
        self.owasp = OWASPChecker()

    def fast_audit(self, system: dict) -> AuditResult:
        gdpr_result = self.gdpr.validate(system)
        owasp_result = self.owasp.check(system)
        return AuditResult(gdpr=gdpr_result, owasp=owasp_result)
```

### Complete Audit (All Tools)

```python
# Compose tools for complete audit
class CompleteAuditor:
    """Complete audit - all compliance tools"""
    def __init__(self):
        self.gdpr = GDPRValidator()
        self.owasp = OWASPChecker()
        self.aifact = AIActVerifier()
        self.lpd = LPDAuditor()
        self.injector = PromptInjector()

    def complete_audit(self, system: dict) -> AuditResult:
        gdpr_result = self.gdpr.validate(system)
        owasp_result = self.owasp.check(system)
        aifact_result = self.aifact.verify(system)
        lpd_result = self.lpd.audit(system)
        prompt_result = self.injector.test(system)
        return AuditResult(all_results=[...])
```

### AI-Focused Audit (OWASP + AI Act)

```python
# Compose tools for AI-focused audit
class AIAuditor:
    """AI-focused audit - OWASP + AI Act"""
    def __init__(self):
        self.owasp = OWASPChecker()
        self.aifact = AIActVerifier()

    def ai_audit(self, system: dict) -> AuditResult:
        owasp_result = self.owasp.check(system)
        aifact_result = self.aifact.verify(system)
        return AuditResult(owasp=owasp_result, aifact=aifact_result)
```

---

## BEST PRACTICES

### DO
- ✅ Each tool does ONE thing well
- ✅ Test each tool independently
- ✅ Inject dependencies (DI)
- ✅ Use small interfaces
- ✅ Compose tools into workflows
- ✅ Replace tools when outdated

### DON'T
- ❌ Create monolithic tools
- ❌ Mix responsibilities
- ❌ Hard-code dependencies
- ❌ Skip unit tests
- ❌ Duplicate code across tools
- ❌ Break tools to fix composer

---

## MIGRATION CHECKLIST

### For Each Monolithic Skill:

1. **Identify Responsibilities**
   - List all responsibilities
   - Group related responsibilities
   - Identify single-purpose tools

2. **Extract Tools**
   - Create tool for each responsibility
   - Move implementation to tool
   - Test each tool independently

3. **Create Composer**
   - Extract orchestration logic
   - Inject tools via DI
   - Test composer with mocks

4. **Update Integration**
   - Update skill to use composer
   - Update tests
   - Update documentation

5. **Cleanup**
   - Delete old monolithic code
   - Update imports
   - Verify all tests pass

---

## VERSION HISTORY

**v1.0 (April 2026):**
- Initial release
- Single-Purpose Tool Design pattern
- Cortex Leman refactoring guide
- Testing strategies
- Composability examples

---

**Created by:** Hermes Agent - Cortex Leman Team
**Inspired by:** 12 Agentic Harness Patterns (generativeprogrammer.com)
**Standards:** SOLID principles, Clean Architecture, Microservices
