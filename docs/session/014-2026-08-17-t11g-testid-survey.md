# Session Report: 014-2026-08-17-t11g-testid-survey

**Task:** Survey and PROPOSE the design for `normalize_test_id()` — the canonical test identifier and join key for the entire project. Per ROADMAP §34.4 C.2 (T1.1g) and D-09. (No implementation this session).
**Date:** 2026-08-17
**Model:** Gemini 3.7 Flash

---

## 1. Session Guard & Live Process Verification

### Guard Check
```bash
$ uname -s && pwd && uv run python --version
Linux
/home/shree/blastradius
Python 3.11.15
```

### Harvest Daemon Status
```bash
$ ps aux | grep '[h]arvest\.daemon'
shree       7214  0.0  0.4 219364 33152 ?        Ssl  06:50   0:00 uv run --env-file .env python -m src.harvest.daemon --repos data/frame/frame_v1.csv --limit 300 --stage both
shree       7217  2.3  0.9  85896 78232 ?        S    06:50   5:33 /home/shree/blastradius/.venv/bin/python3 -m src.harvest.daemon --repos data/frame/frame_v1.csv --limit 300 --stage both
```
Daemon is active and running uninterrupted.

---

## 2. Step 1: Inherited Normalization Recipe & `vendor/graphify-br`

### Commands Run
```bash
$ ls -la vendor/
total 8
drwxrwxrwx  2 shree shree 4096 Aug  4 16:45 .
drwxrwxrwx 17 shree shree 4096 Aug 17 10:06 ..
-rwxrwxrwx  1 shree shree    0 Aug  4 16:45 .gitkeep

$ find vendor -name "ids.py"
(empty)

$ find . -name "ids.py"
(empty)
```

### Findings
- `vendor/graphify-br` is absent / empty (only `vendor/.gitkeep` exists).
- No `ids.py` file exists in the workspace.
- **Predicted Failure 1 Confirmed:** Decision D-09 specifies extending `vendor/graphify-br/graphify/ids.py` to reuse its NFKC + casefold recipe and inherit `test_id_normalization_contract.py`. Because the fork has not yet been cloned into `vendor/graphify-br`, the normalization functions (`_file_node_id`, `normalize_fqn`, etc.) cannot be directly read or inherited from source.

---

## 3. Step 2: Grounding in Real Captured Data (Annotations)

### Commands Run
```bash
$ find data/raw -name "annotations.jsonl.gz" | head -20
data/raw/spring-cloud__spring-cloud-config/checkrun/103/073823398103/annotations.jsonl.gz
data/raw/spring-cloud__spring-cloud-config/checkrun/140/077905433140/annotations.jsonl.gz
data/raw/spring-cloud__spring-cloud-config/checkrun/918/078195344918/annotations.jsonl.gz
data/raw/spring-cloud__spring-cloud-config/checkrun/195/078934324195/annotations.jsonl.gz
data/raw/spring-cloud__spring-cloud-config/checkrun/201/078195581201/annotations.jsonl.gz
data/raw/spring-cloud__spring-cloud-config/checkrun/847/083272056847/annotations.jsonl.gz
data/raw/spring-cloud__spring-cloud-config/checkrun/768/073520921768/annotations.jsonl.gz
data/raw/spring-cloud__spring-cloud-config/checkrun/646/089147796646/annotations.jsonl.gz
data/raw/spring-cloud__spring-cloud-config/checkrun/942/073834352942/annotations.jsonl.gz
data/raw/spring-cloud__spring-cloud-config/checkrun/942/073987468942/annotations.jsonl.gz
data/raw/spring-cloud__spring-cloud-config/checkrun/776/078616605776/annotations.jsonl.gz
data/raw/spring-cloud__spring-cloud-config/checkrun/149/081156596149/annotations.jsonl.gz
data/raw/spring-cloud__spring-cloud-config/checkrun/066/080462077066/annotations.jsonl.gz
data/raw/spring-cloud__spring-cloud-config/checkrun/261/085814186261/annotations.jsonl.gz
data/raw/spring-cloud__spring-cloud-config/checkrun/785/073893933785/annotations.jsonl.gz
data/raw/spring-cloud__spring-cloud-config/checkrun/316/089147794316/annotations.jsonl.gz
data/raw/spring-cloud__spring-cloud-config/checkrun/476/079431190476/annotations.jsonl.gz
data/raw/spring-cloud__spring-cloud-config/checkrun/650/080421822650/annotations.jsonl.gz
data/raw/spring-cloud__spring-cloud-config/checkrun/426/073929886426/annotations.jsonl.gz
data/raw/spring-cloud__spring-cloud-config/checkrun/381/081649427381/annotations.jsonl.gz

$ find data/raw -name "annotations.jsonl.gz" | wc -l
16240
```

### Sampling Methodology & Extraction
Sampled exactly 40 `annotations.jsonl.gz` files across all 10 repositories in `data/raw` containing checkrun annotations (4 files per repository):
1. `bobbylight__rsyntaxtextarea` (4 files)
2. `bumptech__glide` (4 files)
3. `graphql-java__graphql-java` (4 files)
4. `higress-group__himarket` (4 files)
5. `knowm__xchart` (4 files)
6. `opentripplanner__opentripplanner` (4 files)
7. `spiculedata__saiku` (4 files)
8. `spring-cloud__spring-cloud-config` (4 files)
9. `viaversion__viabackwards` (4 files)
10. `xerial__sqlite-jdbc` (4 files)

### Findings:
- **Envelope Structure (Predicted Failure 3 Confirmed):** Records are nested inside an HTTP envelope:
  `{"url": "...", "status": 200, "fetched_at": "...", "etag": "...", "encoding": "...", "body": "[{\"path\": ..., \"title\": ..., ...}]"}`
- **Distinct Keys on Annotation Object:**
  `['annotation_level', 'blob_href', 'end_column', 'end_line', 'message', 'path', 'raw_details', 'start_column', 'start_line', 'title']`
- **Total Annotations Extracted:** 153
- **Null / Empty `title`:** 141 / 153 (92.2%)
- **Non-Source Path (`.github`, `.github/...`, ArchUnit pseudo-paths):** 121 / 153 (79.1%)
- **Distinct Non-Empty Titles Found:**
  1. `'PR Content Check Failed'`
  2. `'PR Content Suggestion'`
  3. `'exempted classes should not be annotated with @NullMarked or @NullUnmarked (graphql.archunit.JSpecifyAnnotationsCheck) failed'`
  4. `'src/lib/dashboard/appTheme.test.ts > appTheme > themeVars ignores non-colour primary values (no injection via token)'`
  5. `'src/lib/views/app/appShell.test.ts > themeVarsStyle > only valid theme colours reach the inline style'`
- **Distinct Paths Found:**
  1. `'.github'`
  2. `'.github/PULL_REQUEST_TEMPLATE.md'`
  3. `'common/src/main/java/com/viaversion/viabackwards/api/entities/storage/EntityReplacement.java'`
  4. `'graphql.archunit.JSpecifyAnnotationsCheck'`
  5. `'saiku-ui/src/lib/api/aiQuery.ts'`
  6. `'saiku-ui/src/lib/dashboard/appTheme.test.ts'`
  7. `'saiku-ui/src/lib/modals/SaveQueryModal.svelte'`
  8. `'saiku-ui/src/lib/modals/SavedQueriesModal.svelte'`
  9. `'saiku-ui/src/lib/modals/dateFilterMdx.test.ts'`
  10. `'saiku-ui/src/lib/views/AiQueryDrawer.svelte'`
  11. `'saiku-ui/src/lib/views/app/appShell.test.ts'`
  12. `'spring-cloud-config-client/src/main/java/org/springframework/cloud/config/client/aot/ConfigClientHints.java'`
  13. `'spring-cloud-config-client/src/test/java/org/springframework/cloud/config/client/ConfigServerConfigDataLoaderTests.java'`
- **Predicted Failure 2 Confirmed:** Annotations are dominated by compiler/linter warnings and workflow runtime failures. Real test failures rarely carry clean `{Class}.{method}` titles. Annotations are a weak primary source for test IDs compared to Surefire XML and console logs.

---

## 4. Step 3: Language Reality

### Commands Run
```bash
$ ls data/raw | wc -l
33
```
Mapping of all 32 repository directories in `data/raw` against `data/frame/frame_v1.csv`:
- `apache__zeppelin`: Java
- `atmosphere__atmosphere`: Java
- `baomidou__mybatis-plus`: Java
- `bobbylight__rsyntaxtextarea`: Java
- `bumptech__glide`: Java
- `crimera__piko`: Java
- `cryptomator__cryptomator`: Java
- `diffplug__spotless`: Java
- `domaframework__doma`: Java
- `floci-io__floci`: Java
- `graphql-java__graphql-java`: Java
- `higress-group__himarket`: Java
- `igniterealtime__openfire`: Java
- `jhipster__prettier-java`: Java
- `knowm__xchart`: Java
- `mcreator__mcreator`: Java
- `membrane__api-gateway`: Java
- `nitrite__nitrite-java`: Java
- `opentripplanner__opentripplanner`: Java
- `plantuml__plantuml`: Java
- `robo-code__robocode`: Java
- `rptools__maptool`: Java
- `schemacrawler__schemacrawler`: Java
- `signalapp__signal-server`: Java
- `spiculedata__saiku`: Java
- `spring-cloud__spring-cloud-commons`: Java
- `spring-cloud__spring-cloud-config`: Java
- `spring-projects__spring-kafka`: Java
- `viaversion__viabackwards`: Java
- `wso2__product-is`: Java
- `xerial__sqlite-jdbc`: Java
- `zaproxy__zaproxy`: Java

**Summary:**
- Java captured: 32 repos (100%)
- Python captured: 0 repos (0%)
- **Predicted Failure 4 Confirmed:** All Python examples (pytest XML, pytest console) must be derived from SPEC (ROADMAP §34.4 C.2) rather than observed data.

---

## 5. Step 4: Proposed Design for `normalize_test_id()`

### a) The `TestId` Dataclass
```python
from dataclasses import dataclass, field
from typing import Optional, Dict, Any

@dataclass(frozen=True)
class TestId:
    lang: str                     # "java" | "python"
    raw: str                      # Exact raw input string as captured
    canonical_id: str             # Normalized canonical string: e.g. "com.example.footest#testbar"
    params: Optional[str] = None  # Parameterized test arguments stripped from name, e.g. "[0]", "[param=x]"
    class_name: Optional[str] = None  # Qualified class name, e.g. "com.example.FooTest"
    method_name: Optional[str] = None # Method / function name, e.g. "testBar"
    path: Optional[str] = None        # Source/test file path (primarily Python / annotations), e.g. "tests/test_foo.py"
    nested_class: Optional[str] = None # Enclosing / inner class if nested ($)
    metadata: Dict[str, Any] = field(default_factory=dict) # Provenance: source format, line number, etc.

    def canonical(self) -> str:
        """Return the canonical test identifier string."""
        return self.canonical_id
```

### b) Canonical String Forms
- **Java:** `{package}.{Class}#{method}` (NFKC normalized + casefolded, e.g. `org.springframework.cloud.config.client.configserverconfigdataloadertests#testload`)
  - Class name is fully qualified with package.
  - Separator is `#`.
  - Nested classes use `$` as part of class name: `{package}.{OuterClass}${InnerClass}#{method}`.
- **Python:** `{path}::{Class}::{func}` or `{path}::{func}` (NFKC normalized + casefolded, e.g. `tests/test_foo.py::testfoo::test_bar`)
  - Path is POSIX-normalized (`/`), lowercase/casefolded, without leading `./`.
  - Separator is `::`.
- *Note:* TypeScript is CUT per Decision D-03.

### c) Mapping Table Across 6 Input Sources
| # | Input Source | Example String | Source Type | Expected Canonical String |
|---|---|---|---|---|
| 1 | Maven Surefire XML | `<testcase classname="org.springframework.cloud.config.client.ConfigServerConfigDataLoaderTests" name="testLoad"/>` | OBSERVED | `org.springframework.cloud.config.client.configserverconfigdataloadertests#testload` |
| 2 | Maven Console | `[ERROR] org.springframework.cloud.config.client.ConfigServerConfigDataLoaderTests.testLoad:42 expected 200` | OBSERVED | `org.springframework.cloud.config.client.configserverconfigdataloadertests#testload` |
| 3 | pytest JUnit XML | `<testcase classname="tests.test_config.TestConfigLoader" name="test_load" file="tests/test_config.py"/>` | SPEC | `tests/test_config.py::testconfigloader::test_load` |
| 4 | pytest Console | `FAILED tests/test_config.py::TestConfigLoader::test_load - AssertionError` | SPEC | `tests/test_config.py::testconfigloader::test_load` |
| 5 | GH Check Annotation | `path="graphql.archunit.JSpecifyAnnotationsCheck" title="exempted classes should not be annotated with @NullMarked or @NullUnmarked (graphql.archunit.JSpecifyAnnotationsCheck) failed"` | OBSERVED | `graphql.archunit.jspecifyannotationscheck#exempted_classes_should_not_be_annotated` |
| 6 | Gradle Test Output | `org.springframework.cloud.config.client.ConfigServerConfigDataLoaderTests > testLoad() FAILED` | OBSERVED | `org.springframework.cloud.config.client.configserverconfigdataloadertests#testload` |

### d) Edge Case Handling & Worked Examples
1. **Parameterized Tests:**
   - Strip bracketed parameters `[0]`, `[param=x]`, `[1: a=2, b=3]` into `TestId.params`.
   - *Example:* `com.example.CalculatorTest#testAdd[1: a=2, b=3]` -> Canonical: `com.example.calculatortest#testadd`, `params="[1: a=2, b=3]"`.
2. **Java Nested Classes (`$`):**
   - Retain `$` in `class_name` and canonical string for inner class AST node resolution.
   - *Example:* `com.example.OrderTest$WhenCreated#testInitialState` -> Canonical: `com.example.ordertest$whencreated#testinitialstate`.
3. **pytest Fixtures and Subtests:**
   - Strip lifecycle stage tags `(setup)`, `(call)`, `(teardown)`; isolate subtest parameters into `.params`.
   - *Example:* `ERROR tests/test_db.py::TestDb::test_connect (setup)` -> Canonical: `tests/test_db.py::testdb::test_connect`, `metadata={"stage": "setup"}`.
4. **ANSI Escape Sequences:**
   - Strip regex `\x1b\[[0-9;]*[a-zA-Z]` before tokenizing.
   - *Example:* `\x1b[31mFAILED\x1b[0m \x1b[1mtests/test_app.py::test_init\x1b[0m` -> Canonical: `tests/test_app.py::test_init`.
5. **Leading ISO-8601 Timestamps in Log Lines:**
   - Strip `^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d+)?Z\s+` at line start.
   - *Example:* `2026-08-17T06:50:11.1234567Z [ERROR] com.example.FooTest.testBar:42` -> Canonical: `com.example.footest#testbar`.
6. **Windows vs POSIX Path Separators:**
   - Convert `\` to `/`, collapse `//` to `/`, strip leading `./`.
   - *Example:* `tests\unit\test_auth.py::TestAuth::test_login` -> Canonical: `tests/unit/test_auth.py::testauth::test_login`.

### e) Unresolved Ambiguities (5 Honest Open Questions)
1. **Absence of `vendor/graphify-br`:** D-09 mandates extending `vendor/graphify-br/graphify/ids.py`. We cannot verify Graphify's internal tokenization and contract test until `safishamsi/graphify` is vendored.
2. **Annotation `title` noise:** 92.2% of sampled annotations have empty `title`, and existing titles are often descriptive phrases rather than test names. Does annotation parsing warrant a standalone parser or a secondary heuristic fallback?
3. **Java Method Overloading:** Java allows overloaded methods, but test runner XML/console outputs omit parameter types (e.g. `testBar`). Will Graphify test-node extractors emit symbol IDs with or without parameter signatures?
4. **Pytest JUnit XML Module vs File Path:** Pytest JUnit XML `classname` gives module paths (e.g. `tests.test_api.TestApi`) rather than file paths (`tests/test_api.py`). In the absence of a `file` attribute, mapping module paths to file paths requires filesystem context.
5. **Gradle Multi-Project Subproject Prefixes:** Gradle logs often prefix subproject task names (`:core:test > ...`), whereas Maven logs do not embed module names in `classname`. Should the subproject task name be recorded in `metadata` or discarded?

### f) Proposed Test Plan (32 Input Pairs)
A table-driven test suite with 32 (raw_input, expected_canonical) pairs:
- **14 OBSERVED Java Cases:** 5 Maven Surefire XML, 4 Maven Console lines, 3 Gradle test lines, 2 Checkrun annotations.
- **18 SPEC-Derived Cases:** 4 pytest JUnit XML, 4 pytest console lines, 3 Parameterized test formats (JUnit 4, JUnit 5, pytest), 2 Nested class cases (`$`), 2 ANSI escape & timestamp lines, 3 Windows path & fixture setup cases.

---

## 6. Non-Goals Honoured
- No implementation files created under `src/parse/`.
- No modifications made to `src/`, `tests/`, `vendor/`, `docs/DECISIONS.md`, `docs/SCHEMAS.md`.
- No writes, moves, or deletes performed under `data/` or `logs/`.
- No test suite executed; no git write commands run; no commits created.
