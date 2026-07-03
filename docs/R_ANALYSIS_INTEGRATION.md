# R-Analysis Integration: Enhancing the MCP Server with R Package Insights

## Table of Contents

1. [Executive Summary](#executive-summary)
2. [Key Findings from R-Analysis](#key-findings-from-r-analysis)
3. [Analytical Framework and Questions](#analytical-framework-and-questions)
4. [Data Reshaping Architecture](#data-reshaping-architecture)
5. [Visualization Patterns (Chart Library)](#visualization-patterns-chart-library)
6. [AI-Powered Report Generation](#ai-powered-report-generation)
7. [Code Tables and Reference Data](#code-tables-and-reference-data)
8. [Recommendations for MCP Server Integration](#recommendations-for-mcp-server-integration)
9. [Implementation Priority Matrix](#implementation-priority-matrix)
10. [Technical Appendices](#technical-appendices)

---

## Executive Summary

The R-analysis package (`unhcr-americas/iati`) provides a **mature, production-ready analytical framework** for UNHCR IATI data that the MCP server can leverage. This document extracts the key insights, patterns, and methodologies from the R implementation and translates them into actionable recommendations for the Python MCP server.

### Key Value Propositions from R-Analysis

| Component | Description | MCP Server Application |
|-----------|-------------|------------------------|
| **Data Reshaping** | XML to tabular transformation with 14 specialized extractors | Enhance data preprocessing, add bulk extraction tools |
| **Chart Library** | 30+ standardized ggplot2 visualizations for UNHCR questions | Add visualization endpoints, export chart data |
| **AI Reports** | Quarto templates with "human-in-the-loop ready" AI narratives | Enhance export tools, add report generation |
| **Code Tables** | 30+ IATI code lookup tables (RData files) | Embed as MCP resources, enable code resolution |
| **Analytical Questions** | 7 standardized key questions across all operations | Create pre-built tool combinations |

### Rationale Alignment

The R-analysis package's philosophy aligns perfectly with the MCP server's goals:

> "Using AI to generate narrative on top of a **standardized set of charts and indicators** introduces a level of methodological consistency that simple chat-based prompting cannot achieve. This framework ensures that every operation is analyzed through the same **structured lens**, enabling comparability across countries, time periods, and thematic areas."

This is exactly what the MCP server should provide to AI agents: **structured, consistent access to UNHCR IATI data with standardized analytical frameworks.**

---

## Key Findings from R-Analysis

### 1. Package Structure

```
R-analysis/
├── README.md                      # Objectives, rationale, scope
├── dev_data_reshape.Rmd          # XML → Tabular transformation (14 extractors)
├── dev_unhcr_programme.Rmd       # Chart library (~30 visualization functions)
├── dev_report.Rmd                # AI-powered report generation (Quarto)
├── build.R                       # Package build configuration
├── data.R                        # Pre-processed IATI data
├── *.RData                       # 30+ code lookup tables
└── mapping_*.RData                # Indicator, result, SDG mappings
```

### 2. Design Philosophy

**Core Principles:**
1. **Standardized Analytical Lens** - Every operation analyzed through the same framework
2. **Human-in-the-Loop Ready** - AI generates drafts, humans refine
3. **Methodological Consistency** - Reduces variance, improves coherence
4. **Reproducibility** - Same questions, same metrics across all analyses

**Key Insight:** The R package solves the "chat-based analysis problem" where each LLM interaction produces different framings. By providing **pre-defined analytical questions** and **standardized visualizations**, the AI can anchor its analysis in a stable framework.

### 3. What Makes This Production-Ready

✅ **Proven in Production**: Used by UNHCR Americas for real operational analysis
✅ **Comprehensive Code Coverage**: 30+ IATI code tables embedded
✅ **Standardized Visualizations**: Chart library with UNHCR branding (unhcrthemes)
✅ **AI Integration**: Quarto templates with AI-generated narratives
✅ **Data Quality**: Parallel extraction, error handling, logging
✅ **Documentation**: fusen package for consistent docs across notebooks

---

## Analytical Framework and Questions

### Standardized Key Questions

From `README.md` (lines 65-71), the R package defines **7 core analytical questions** that every UNHCR operation should answer:

#### Question 1: Most Funded Sectors per Country
**Purpose:** Understand priority areas and resource allocation
**R Function:** `show_sectors()`
**MCP Tool:** `unhcr_sector_summary`, `unhcr_top_sectors`
**Data Needed:** sector, transaction_value_USD, recipient_country
**Visualization:** Treemap, bar chart, or stacked bar

#### Question 2: Main Donors by Country
**Purpose:** Identify funding sources and partnerships
**R Function:** Implicit in report generation
**MCP Tool:** `unhcr_top_donors`, `unhcr_donor_breakdown`
**Data Needed:** transaction_provider_org, transaction_value_USD, recipient_country
**Visualization:** Horizontal bar chart, pie chart

#### Question 3: Main Implementing Partners by Country
**Purpose:** Understand implementation ecosystem
**R Function:** Derived from participating_org extraction
**MCP Tool:** `unhcr_implementing_partners`, `unhcr_partnership_analysis`
**Data Needed:** participating_org, iati_identifier, budget_value
**Visualization:** Network graph, bar chart

#### Question 4: Earmarking Type Breakdown
**Purpose:** Analyze funding flexibility
**R Function:** From transaction extraction
**MCP Tool:** `unhcr_earmarking_analysis`
**Data Needed:** transaction_aid_type_code, transaction_value_USD
**Visualization:** Donut chart, stacked bar

**Earmarking Categories (from codeEarmarkingCategory.RData):**
- `0` - Un-earmarked
- `1` - Tightly earmarked
- `2` - Loosely earmarked
- `3` - Core/Un-earmarked contributions

#### Question 5: Partnership Level Analysis
**Purpose:** Understand collaboration patterns
**R Function:** From participating_org role extraction
**MCP Tool:** `unhcr_partnership_levels`
**Data Needed:** participating_org_role, iati_identifier
**Visualization:** Matrix, heatmap

**Partnership Roles:**
- `1` - Funding
- `2` - Accountable
- `3` - Implementing
- `4` - Extending

#### Question 6: Expenditure vs Budget Comparison
**Purpose:** Track financial execution
**R Function:** `show_indicators()` with type="deviation"
**MCP Tool:** `unhcr_budget_vs_expenditure`, `unhcr_financial_deviation`
**Data Needed:** budget_value, transaction_value (expenditure), iati_identifier
**Visualization:** Deviation bar chart, waterfall

**Calculation Methodology:**
```
Deviation (%) = (actual - target) / target * 100
Progress (%) = (actual - baseline) / baseline * 100  
Gap to Green (%) = (actual - threshold_green) / threshold_green * 100
```

#### Question 7: Indicator Evolution Over Time
**Purpose:** Monitor programme performance
**R Function:** `show_indicators_time()`
**MCP Tool:** `unhcr_indicator_trends`, `unhcr_performance_tracking`
**Data Needed:** result_indicator_actual_value, result_indicator_target_value, year
**Visualization:** Line chart with thresholds, sparkline

**Indicator Types (Results Framework):**
- **Impact** - Long-term outcomes (global level)
- **Outcome** - Medium-term results (country/operation level) - **16 OA areas**
- **Output** - Short-term deliverables (activity level)

### UNHCR Results Framework (OA - Outcome Areas)

From `dev_unhcr_programme.Rmd` (lines 246-261):

1. **OA1** - Access to Territory, Registration and Documentation
2. **OA2** - Status Determination
3. **OA3** - Protection Policy and Law
4. **OA4** - Sexual and Gender-based Violence
5. **OA5** - Child Protection
6. **OA6** - Safety and Access to Justice
7. **OA7** - Community Engagement and Women's Empowerment
8. **OA8** - Well-Being and Basic Needs
9. **OA9** - Sustainable Housing and Settlements
10. **OA10** - Healthy Lives
11. **OA11** - Education
12. **OA12** - Clean Water, Sanitation and Hygiene (WASH)
13. **OA13** - Self Reliance, Economic Inclusion and Livelihoods
14. **OA14** - Voluntary Repatriation and Sustainable Reintegration
15. **OA15** - Resettlement and Complementary Pathways
16. **OA16** - Local Integration and other Local Solutions

**Color Palette (for visualizations):**
- Each OA has a designated color for consistent branding across all charts
- Example: OA8 (Well-Being) = `#e5243b` (SDG red)

### Out of Scope Questions

The R package explicitly excludes questions that require **cross-UN-agency data** (lines 73-85):

- Share of funds across UN agencies (UNICEF, WFP, IOM, etc.)
- Resource balancing between humanitarian crises
- Humanitarian vs development allocation
- Migratory vs refugee funding split
- ODA (Official Development Assistance) share
- ODA to national actors
- Humanitarian assistance share within ODA

**Implication for MCP Server:** These questions require **external data sources** beyond UNHCR's IATI publications. The MCP server should focus on **UNHCR-specific data** and document these limitations clearly.

---

## Data Reshaping Architecture

### Core Transformation Pipeline

From `dev_data_reshape.Rmd`, the R package implements a **sophisticated XML-to-tabular pipeline**:

```
IATI XML Files (from UNHCR)
    ↓
Download & Parse (xml2::read_xml)
    ↓
Parallel Extraction (14 specialized extractors)
    ↓
Data Cleaning & Transformation
    ↓
Export to Excel/CSV (writexl::write_xlsx)
    ↓
R Data Package (iati::dataActivity, iati::dataSector, etc.)
```

### 14 Extraction Functions

All extractors follow the same pattern:
1. Find XML nodes using XPath
2. Extract attributes and text values
3. Handle missing data (return NA_character_)
4. Build tibble data frame
5. Log progress

| Extractor | XML Path | Purpose | MCP Equivalent |
|-----------|----------|---------|----------------|
| `iati_activity` | `.//iati-activity` | Core activity metadata | `unhcr_activities` tool |
| `iati_transaction` | `.//iati-activity/transaction` | Financial movements | `unhcr_transactions` tool |
| `iati_budget` | `.//iati-activity/budget` | Planned allocations | `unhcr_budgets` tool |
| `iati_sector` | `.//iati-activity/sector` | Sector classifications | `unhcr_sectors` tool |
| `iati_result` | `.//iati-activity/result/indicator` | Results & indicators | **NEW: indicators tool** |
| `iati_participating_org` | `.//iati-activity/participating-org` | Partners | **NEW: partners tool** |
| `iati_location` | `.//iati-activity/location` | Geographic data | **NEW: locations tool** |
| `iati_humanitarian_scope` | `.//iati-activity/humanitarian-scope` | Humanitarian context | **NEW: humanitarian tool** |
| `iati_policy_marker` | `.//iati-activity/policy-marker` | Policy tags | **NEW: policy_markers tool** |
| `iati_document_link` | `.//iati-activity/document-link` | Documentation | **NEW: documents tool** |
| `iati_default_aid_type` | `.//iati-activity/default-aid-type` | Aid classification | **ENHANCE: add to activities** |
| `iati_tag` | `.//iati-activity/tag` | Custom tags | **NEW: tags tool** |
| `iati_related_activity` | `.//iati-activity/related-activity` | Activity relationships | **NEW: related_activities tool** |

### Key Implementation Details

#### Helper Functions

```r
# Safe XML value extraction
get_xml_value <- function(node, xpath, attr = NULL, pos = 1L) {
  if (!inherits(node, "xml_node")) return(NA_character_)
  found_nodes <- xml2::xml_find_all(node, xpath)
  if (length(found_nodes) < pos) return(NA_character_)
  target_node <- found_nodes[[pos]]
  if (!is.null(attr)) {
    value <- xml2::xml_attr(target_node, attr)
  } else {
    value <- xml2::xml_text(target_node)
  }
  if (is.na(value) || value == "") return(NA_character_)
  value
}

# Logging helper
log_debug <- function(..., verbose = TRUE) {
  if (verbose) message(Sys.time(), " [DEBUG] ", ...)
}
```

#### Parallel Processing

```r
# Uses furrr for parallel extraction
future::plan(future::multisession)
all_data <- furrr::future_imap(
  iati_extractors,
  ~ {
    xml_iati <- xml2::read_xml(iati_file)
    fn <- .x
    nm <- .y
    log_debug("  • Extracting: ", nm, verbose = verbose)
    res <- fn(xml_iati, verbose = verbose)
    res
  },
  .progress = TRUE,
  .options = furrr::furrr_options(seed = TRUE)
)
```

**MCP Server Recommendation:** Implement **async parallel requests** to IATI Datastore API for multiple collections simultaneously.

#### Main Orchestrator Function

```r
iati_reshape_all <- function(
  iati_file_url = 'https://files.unhcr.org/en/reporting/unhcr-activities-2026.xml',
  folder_name   = "data-raw",
  extractors    = NULL,  # NULL = all, or vector of names
  verbose       = TRUE
)
```

**MCP Server Equivalent:**
```python
# Bulk extraction tool
async def unhcr_bulk_extract(
    year: int | None = None,
    collections: list[str] | None = None,  # None = all
    format: str = "json"  # or "csv", "excel"
) -> dict:
    """
    Extract multiple IATI collections in parallel.
    Returns structured data for all requested collections.
    """
```

### Data Quality Considerations

1. **Multi-year Support**: Data from 2016 onwards, with different indicator sets pre-2022
2. **Null Handling**: Consistent NA_character_ for missing values
3. **Type Safety**: Explicit type conversions (as.numeric, as.character)
4. **Validation**: Input validation for filter parameters
5. **Progress Tracking**: Logging at each extraction stage

---

## Visualization Patterns (Chart Library)

The R package includes a comprehensive **chart library** with standardized visualizations for UNHCR programme analysis. These patterns can inform MCP server **data export formats** and **pre-aggregated endpoints**.

### Chart Categories

#### 1. Indicator Analysis Charts

**Function:** `show_indicators()` and `show_indicators_time()`

**Three Analysis Types:**

##### Type A: Deviation (Actual vs Target)
```r
show_indicators(year = 2025, ctr_name = "Brazil", 
                result_type_name = "Outcome", type = "deviation")
```

**Purpose:** Show how actual results deviate from programmatic targets
**Calculation:**
```
deviation_actual_target = round((actual - target) / if_else(target == 0, 1, target) * 100, 2)
# Account for indicator direction (ascending vs descending)
if (result_indicator_ascending == 0) deviation_actual_target <- deviation_actual_target * -1
```

**Color Coding (Traffic Light):**
- **Green**: deviation >= -1% (on or above target)
- **Orange**: deviation < -1% AND >= -15% (slightly below)
- **Red**: deviation < -15% (significantly below)

**Visualization:**
- Horizontal bar chart (coord_flip)
- Color by sector_rbm (Outcome Area) or deviation_color
- Faceted by population group
- Labels show percentage values

##### Type B: Progress (Actual vs Baseline)
```r
show_indicators(year = 2025, ctr_name = "Brazil", 
                result_type_name = "Outcome", type = "progress")
```

**Purpose:** Show progress from baseline to actual
**Calculation:**
```
progress_baseline = round((actual - baseline) / if_else(baseline == 0, 1, baseline) * 100, 2)
if (result_indicator_ascending == 0) progress_baseline <- progress_baseline * -1
```

**Color Coding:** Same traffic light system

##### Type C: Gap Analysis (Actual vs Green Threshold)
```r
show_indicators(year = 2025, ctr_name = "Brazil", 
                result_type_name = "Outcome", type = "gap")
```

**Purpose:** Show distance to acceptable global standards
**Calculation:**
```
gap_green = round((actual - threshold_green) / if_else(threshold_green == 0, 1, threshold_green) * 100, 2)
gap_orange = round((actual - threshold_orange) / if_else(threshold_orange == 0, 1, threshold_orange) * 100, 2)
gap_red = round((actual - threshold_red) / if_else(threshold_red == 0, 1, threshold_red) * 100, 2)
```

**Note:** Gap analysis is **only for Outcome indicators published after 2022**

#### 2. Sector Analysis Charts

**Function:** `show_sectors()`

**Purpose:** "What are the most funded sectors per country?"

**Visualization:**
- Bar chart or treemap
- Color by sector category
- Faceted by year or operation
- Shows expenditure evolution per impact/outcome area

#### 3. Common Visualization Elements

**UNHCR Theme (unhcrthemes package):**
```r
unhcrthemes::theme_unhcr(
  font_size = 18,
  axis_text_size = 9,
  grid = "X" or "Y",
  axis = "y",
  strip_text_size = rel(0.5),
  strip_text_face = "italic"
)
```

**Standard Chart Elements:**
- Source caption: "Source: Data published by UNHCR as part of the International Aid Transparency Initiative (IATI)"
- Wrapped labels (stringr::str_wrap with width=100-120)
- Percentage formatting with scales::label_number(accuracy=1, suffix="%")
- Faceting by population groups or dimensions

**Data Cleaning for Charts:**
```r
# Remove outliers
df <- df |>
  filter(!(abs(progress_baseline - median(progress_baseline)) > 
           3 * sd(progress_baseline)))

# Filter out missing data
df <- df |>
  filter(!is.na(actual)) |>
  filter(!is.na(target)) |>
  filter(!is.nan(deviation_actual_target))

# Reorder by value
df <- df |>
  group_by(result_indicator_title) |>
  arrange(desc(actual), .by_group=TRUE) |>
  ungroup()
```

### Visualization Data Requirements for MCP Server

To support chart generation by AI agents or external tools, the MCP server should provide:

1. **Pre-aggregated data endpoints:**
   - Sector funding by country/year
   - Donor contributions by country/year
   - Indicator values by type/country/year

2. **Chart-ready data formats:**
   - Data already grouped and summarized
   - Labels and descriptions included
   - Color mappings for consistent rendering

3. **Metadata for chart configuration:**
   - Recommended chart types for each analytical question
   - Color palettes (OA colors, traffic light colors)
   - Axis labels and titles

---

## AI-Powered Report Generation

From `dev_report.Rmd`, the R package provides **automated report generation** using Quarto templates.

### Report Generation Function

```r
generate_report <- function(
  type = "donor",      # or "operation", "recipient", "destination"
  name = NULL,         # NULL = batch process all
  top_n = 20           # Top N by total amount
)
```

**Process:**
1. Load Quarto template from package extension
2. For each entity (donor/operation):
   - Render template with entity-specific data
   - Generate HTML report
   - Move to output directory
3. Return list of report links

**Template Structure:**
```
_extension/
  donor/
    template.qmd    # Quarto template for donor reports
  operation/
    template.qmd    # Quarto template for operation reports
```

### Batch Processing Logic

**For Donors (lines 67-76):**
```r
name <- iati::dataTransaction |>
  left_join(iati::dataActivity, by = c("iati_identifier")) |>
  filter(year == 2025 & transaction_type_name == "Incoming Commitment") |>
  group_by(year, transaction_provider_org) |>
  summarise(transaction_value_USD = sum(transaction_value_USD, na.rm = TRUE)) |>
  arrange(desc(transaction_value_USD)) |>
  slice_head(n = 50) |>
  pull(transaction_provider_org)
```

**For Operations (lines 106-110):**
```r
name <- data |> sort() |> unique()
```

### Report Output

- Output directory: `docs/reports/`
- Filename format: `iatiAnalysis-{type}-{slug}.html`
- Example: `iatiAnalysis-donor-united-states-of-america-government-of.html`

### AI Narrative Generation Approach

The key insight from the R package's rationale:

1. **Standardized Input**: AI receives pre-processed data in consistent format
2. **Structured Prompts**: AI generates narrative based on standardized charts
3. **Human Refinement**: Analysts focus on nuance, not data assembly
4. **Consistency**: Same analytical framework applied to all operations

**MCP Server Application:**

The MCP server should provide **AI-ready data structures** that enable:
- Consistent prompting across all operations
- Pre-calculated metrics and comparisons
- Standardized field names and descriptions

### Report Content Structure

Based on the chart library, reports likely include:

1. **Executive Summary**
   - Key figures (total budget, expenditure, beneficiaries)
   - High-level trends

2. **Sector Analysis**
   - Most funded sectors
   - Sector trends over time
   - Sector vs budget comparisons

3. **Donor Analysis**
   - Top donors by contribution
   - Donor trends
   - Earmarking patterns

4. **Implementation Analysis**
   - Main implementing partners
   - Partnership levels
   - Geographic distribution

5. **Results Framework**
   - Indicator evolution (Impact, Outcome, Output)
   - Deviation from targets
   - Progress from baselines
   - Gap to thresholds

6. **Financial Analysis**
   - Budget vs expenditure
   - Expenditure patterns
   - Financial execution rate

---

## Code Tables and Reference Data

The R package includes **30+ IATI code lookup tables** as RData files. These are **critical for data interpretation** and should be embedded in the MCP server.

### Code Table Categories

#### 1. Activity Codes
- `codeActivityDateType.RData` - Activity date types
- `codeActivityScope.RData` - Activity scope codes
- `codeActivityStatus.RData` - Activity status codes

#### 2. Organisation Codes
- `codeOrganisationIdentifier.RData` - Organisation identifiers
- `codeOrganisationRegistrationAgency.RData` - Registration agencies
- `codeOrganisationRole.RData` - Organisation roles
- `codeOrganisationType.RData` - Organisation types

#### 3. Geographic Codes
- `codeCountry.RData` - Country codes and names
- `codeRegion.RData` - Region codes

#### 4. Financial Codes
- `codeAidType.RData` - Aid type codes
- `codeAidTypeCategory.RData` - Aid type categories
- `codeAidTypeVocabulary.RData` - Aid type vocabularies
- `codeBudgetIdentifier.RData` - Budget identifiers
- `codeBudgetIdentifierSector.RData` - Budget identifier sectors
- `codeBudgetStatus.RData` - Budget status codes
- `codeBudgetType.RData` - Budget type codes
- `codeCashandVoucherModalities.RData` - Cash and voucher modalities
- `codeFlowType.RData` - Flow type codes
- `codeDefaultFlowType.RData` - Default flow types
- `codeFinanceType.RData` - Finance type codes
- `codeTiedStatus.RData` - Tied status codes

#### 5. Sector Codes
- `codeSector.RData` - Sector codes (main table, ~22KB)
- `codeSectorCategory.RData` - Sector categories
- `codeSectorVocabulary.RData` - Sector vocabularies

#### 6. Policy and Humanitarian Codes
- `codeCollaborationType.RData` - Collaboration types
- `codePolicyMarker.RData` - Policy markers
- `codeHumanitarianScopeType.RData` - Humanitarian scope types
- `codeHumanitarianScopeVocabulary.RData` - Humanitarian scope vocabularies
- `codeHumCluster.RData` - Humanitarian clusters

#### 7. Result Framework Codes
- `mapping_indicator.RData` - Indicator mappings
- `mapping_result.RData` - Result mappings
- `mapping_sdg.RData` - SDG mappings

#### 8. Other Codes
- `codeCurrency.RData` - Currency codes
- `codeDescriptionType.RData` - Description types
- `codeEarmarkingCategory.RData` - Earmarking categories
- `codeGeographicLocationClass.RData` - Geographic location classes
- `codeResultType.RData` - Result types
- `codeUNSDGGoals.RData` - UN SDG goals
- `codeUNSDGTargets.RData` - UN SDG targets

### Code Table Structure

Each RData file typically contains a **data frame with code-value mappings**:

```r
# Example: codeCountry.RData
# Structure:
#   code: Character (ISO 2-letter country code)
#   name: Character (Country name)

# Example: codeSector.RData
# Structure:
#   code: Character (Sector code, e.g., "12220")
#   name: Character (Sector name, e.g., "Basic health care")
#   category: Character (Category)
#   vocabulary: Character (Vocabulary name)
#   vocabulary_uri: Character (Vocabulary URI)

# Example: codeOrganisationIdentifier.RData
# Structure:
#   code: Character (Organisation identifier)
#   name: Character (Organisation name)
#   type: Character (Organisation type)
#   registration_agency: Character
```

### MCP Server Integration Strategy

**Option 1: Embed as Resources**
```python
# In resources/ directory
@mcp.resource("unhcr://codes/country")
async def code_country():
    """Country code to name mapping from IATI"""
    return CODE_COUNTRY_DICT

@mcp.resource("unhcr://codes/sector")
async def code_sector():
    """Sector code to name mapping from IATI"""
    return CODE_SECTOR_DICT
```

**Option 2: Create Code Resolution Tools**
```python
@mcp.tool()
async def resolve_sector_code(code: str) -> dict:
    """Resolve a sector code to its name and description"""
    return {"code": code, "name": SECTOR_CODES.get(code, "Unknown")}

@mcp.tool()
async def resolve_country_code(code: str) -> dict:
    """Resolve a country code to its name"""
    return {"code": code, "name": COUNTRY_CODES.get(code, "Unknown")}
```

**Option 3: Pre-load in Client**
```python
# In client.py
class IATIClient:
    def __init__(self):
        self.sector_codes = self._load_code_table("sector")
        self.country_codes = self._load_code_table("country")
        # ... etc
    
    def _load_code_table(self, table_name: str) -> dict:
        """Load IATI code table from embedded data"""
        # Load from JSON or hardcoded dict
```

**Recommended: Hybrid Approach**
1. Embed **frequently used codes** (country, sector, donor) as resources
2. Create **resolution tools** for dynamic lookup
3. Pre-load **all codes** in the client for internal use

### Sample Code Data

From examining the RData files:

**Country Codes (codeCountry.RData):**
```
AF - Afghanistan
AL - Albania
DZ - Algeria
... (200+ countries)
```

**Sector Codes (codeSector.RData):**
```
11110 - General budget support
11120 - Core support to NGOs, other private bodies, institutions and individuals
11130 - Core contributions to multilateral institutions
12110 - General education policy and administrative management
12181 - Health education
12220 - Basic health care
12230 - Basic health infrastructure
12240 - Basic nutrition
... (500+ sectors)
```

**Sector Vocabularies:**
- `"1"` - OECD DAC CRS (most common)
- `"2"` - OECD DAC CRS (5-digit)
- `"99"` - Reporting Organisation

**Organisation Roles (codeOrganisationRole.RData):**
```
1 - Funding
2 - Accountable
3 - Implementing
4 - Extending
```

---

## Recommendations for MCP Server Integration

### Priority 1: Immediate Enhancements (1-2 days)

#### 1. Add Bulk Data Extraction Tools

**New Tools:**
```python
# In tools/bulk.py

@mcp.tool()
async def unhcr_bulk_extract(
    collections: list[str] | None = None,
    year: int | None = None,
    country_code: str | None = None,
    format: str = "json"
) -> dict:
    """
    Extract multiple IATI collections in parallel.
    
    Args:
        collections: List of collections to extract (activity, transaction, budget, sector, etc.)
        year: Filter by year
        country_code: Filter by ISO 2-letter country code
        format: Output format (json, csv)
    
    Returns:
        Dictionary with extracted data for all collections
    """
```

**Implementation:**
- Use asyncio.gather for parallel API requests
- Respect rate limits (50 connections max, from config)
- Include progress tracking (like R's .progress = TRUE)

#### 2. Add Missing Extractors as Tools

Based on the 14 R extractors, add these new tools:

```python
# tools/results.py
@mcp.tool()
async def unhcr_results(
    iati_identifier: str | None = None,
    year: int | None = None,
    result_type: str | None = None  # Impact, Outcome, Output
) -> list[dict]:
    """Get result indicators for activities"""

# tools/locations.py
@mcp.tool()
async def unhcr_locations(
    iati_identifier: str | None = None,
    country_code: str | None = None
) -> list[dict]:
    """Get location data for activities"""

# tools/participating_orgs.py
@mcp.tool()
async def unhcr_participating_orgs(
    iati_identifier: str | None = None,
    role: str | None = None  # Funding, Accountable, Implementing, Extending
) -> list[dict]:
    """Get participating organizations for activities"""

# tools/policy_markers.py
@mcp.tool()
async def unhcr_policy_markers(
    iati_identifier: str | None = None,
    code: str | None = None
) -> list[dict]:
    """Get policy markers for activities"""

# tools/humanitarian_scopes.py
@mcp.tool()
async def unhcr_humanitarian_scopes(
    iati_identifier: str | None = None
) -> list[dict]:
    """Get humanitarian scope information for activities"""

# tools/tags.py
@mcp.tool()
async def unhcr_tags(
    iati_identifier: str | None = None,
    vocabulary: str | None = None
) -> list[dict]:
    """Get tags for activities"""

# tools/related_activities.py
@mcp.tool()
async def unhcr_related_activities(
    iati_identifier: str
) -> list[dict]:
    """Get related activities for a specific activity"""

# tools/document_links.py
@mcp.tool()
async def unhcr_document_links(
    iati_identifier: str | None = None,
    category: str | None = None
) -> list[dict]:
    """Get document links for activities"""
```

#### 3. Add Pre-Built Analytical Tools

Implement the 7 standardized questions as tools:

```python
# tools/analytics_standard.py

@mcp.tool()
async def unhcr_most_funded_sectors(
    country_code: str | None = None,
    year: int | None = None,
    top_n: int = 10,
    vocabulary: str = "Reporting Organisation 2"
) -> dict:
    """
    What are the most funded sectors per country?
    
    Returns sector breakdown with funding amounts and percentages.
    """

@mcp.tool()
async def unhcr_top_donors(
    country_code: str | None = None,
    year: int | None = None,
    top_n: int = 20,
    transaction_type: str = "Incoming Commitment"
) -> dict:
    """
    Who are the main donors by country?
    
    Returns ranked list of donors with contribution amounts.
    """

@mcp.tool()
async def unhcr_implementing_partners(
    country_code: str | None = None,
    year: int | None = None,
    top_n: int = 20
) -> dict:
    """
    Who are the main implementing partners by country?
    
    Returns ranked list of partners with budget allocations.
    """

@mcp.tool()
async def unhcr_earmarking_analysis(
    year: int | None = None,
    country_code: str | None = None
) -> dict:
    """
    What's the breakdown of Earmarking Type from Donor Funds?
    
    Returns distribution of earmarking categories with percentages.
    """

@mcp.tool()
async def unhcr_partnership_levels(
    country_code: str | None = None,
    year: int | None = None
) -> dict:
    """
    What's the level of partnership between organisations?
    
    Returns matrix of partnership roles and relationships.
    """

@mcp.tool()
async def unhcr_budget_vs_expenditure(
    country_code: str | None = None,
    year: int | None = None
) -> dict:
    """
    How much expenditures compare to the initial budget?
    
    Returns comparison with deviation percentages.
    """

@mcp.tool()
async def unhcr_indicator_trends(
    country_code: str | None = None,
    result_type: str = "Outcome",  # Impact, Outcome, Output
    year: int | list[int] | None = None,
    indicator_code: str | None = None
) -> dict:
    """
    How much indicators evolve over time against thresholds?
    
    Returns indicator values with baseline, target, actual, and deviation.
    """
```

#### 4. Embed Code Tables as Resources

Create a new resources module for code tables:

```python
# resources/codes.py

from unhcr_iati_mcp.context import mcp

# Load all code tables
CODE_COUNTRY = {...}  # From codeCountry.RData
CODE_SECTOR = {...}   # From codeSector.RData
CODE_ORGANISATION = {...}  # From codeOrganisationIdentifier.RData
CODE_AID_TYPE = {...}  # From codeAidType.RData
CODE_POLICY_MARKER = {...}  # From codePolicyMarker.RData
# ... etc

@mcp.resource("unhcr://codes/country")
async def code_country():
    """IATI Country Codes - ISO 2-letter to name mapping"""
    return CODE_COUNTRY

@mcp.resource("unhcr://codes/sector")
async def code_sector():
    """IATI Sector Codes - Code to name and description mapping"""
    return CODE_SECTOR

@mcp.resource("unhcr://codes/sector_vocabularies")
async def code_sector_vocabularies():
    """IATI Sector Vocabularies"""
    return {
        "1": "OECD DAC CRS",
        "2": "OECD DAC CRS (5-digit)",
        "99": "Reporting Organisation"
    }

@mcp.resource("unhcr://codes/organisation")
async def code_organisation():
    """IATI Organisation Codes"""
    return CODE_ORGANISATION

@mcp.resource("unhcr://codes/aid_type")
async def code_aid_type():
    """IATI Aid Type Codes"""
    return CODE_AID_TYPE

@mcp.resource("unhcr://codes/policy_marker")
async def code_policy_marker():
    """IATI Policy Marker Codes"""
    return CODE_POLICY_MARKER

@mcp.resource("unhcr://codes/earmarking_category")
async def code_earmarking_category():
    """IATI Earmarking Category Codes"""
    return {
        "0": "Un-earmarked",
        "1": "Tightly earmarked",
        "2": "Loosely earmarked",
        "3": "Core/Un-earmarked contributions"
    }

@mcp.resource("unhcr://codes/organisation_role")
async def code_organisation_role():
    """IATI Organisation Role Codes"""
    return {
        "1": "Funding",
        "2": "Accountable", 
        "3": "Implementing",
        "4": "Extending"
    }

@mcp.resource("unhcr://codes/result_type")
async def code_result_type():
    """UNHCR Results Framework Types"""
    return {
        "Impact": "Long-term outcomes (global level)",
        "Outcome": "Medium-term results (country/operation level) - 16 OA areas",
        "Output": "Short-term deliverables (activity level)"
    }

@mcp.resource("unhcr://codes/outcome_areas")
async def code_outcome_areas():
    """UNHCR 16 Outcome Areas (OA1-OA16) with colors"""
    return {
        "OA1": {"name": "Access to Territory, Reg. and Documentation", "color": "#F0A3FF"},
        "OA2": {"name": "Status Determination", "color": "#C20088"},
        "OA3": {"name": "Protection Policy and Law", "color": "#993F00"},
        "OA4": {"name": "Sexual and Gender-based Violence", "color": "#FF3A21"},
        "OA5": {"name": "Child Protection", "color": "#FFCC99"},
        "OA6": {"name": "Safety and Access to Justice", "color": "#00689D"},
        "OA7": {"name": "Community Engagement and Women's Empowerment", "color": "#94FFB5"},
        "OA8": {"name": "Well-Being and Basic Needs", "color": "#e5243b"},
        "OA9": {"name": "Sustainable Housing and Settlements", "color": "#FD9D24"},
        "OA10": {"name": "Healthy Lives", "color": "#4C9F38"},
        "OA11": {"name": "Education", "color": "#C5192D"},
        "OA12": {"name": "Clean Water, Sanitation and Hygiene", "color": "#26BDE2"},
        "OA13": {"name": "Self Reliance, Economic Inclusion and Livelihoods", "color": "#A21942"},
        "OA14": {"name": "Voluntary Repatriation and Sustainable Reintegration", "color": "#9DCC00"},
        "OA15": {"name": "Resettlement and Complementary Pathways", "color": "#191919"},
        "OA16": {"name": "Local Integration and other Local Solutions", "color": "#2BCE48"}
    }
```

### Priority 2: Enhanced Data Export (3-5 days)

#### 1. Add Chart-Ready Data Export

```python
# tools/export_chart.py

@mcp.tool()
async def unhcr_export_sector_chart(
    country_code: str,
    year: int,
    vocabulary: str = "Reporting Organisation 2",
    format: str = "json"
) -> dict:
    """
    Export data in format ready for sector visualization.
    
    Returns:
    {
        "title": "Most Funded Sectors - {country} {year}",
        "subtitle": "Expenditure by sector (USD)",
        "data": [{"sector_code": "12220", "sector_name": "Basic health care", "value": 1000000}],
        "chart_type": "bar",
        "color_palette": "unhcr_sector",
        "recommended_chart": "horizontal_bar"
    }
    """

@mcp.tool()
async def unhcr_export_donor_chart(
    country_code: str,
    year: int,
    top_n: int = 20,
    format: str = "json"
) -> dict:
    """Export donor data ready for visualization."""

@mcp.tool()
async def unhcr_export_indicator_chart(
    country_code: str,
    result_type: str = "Outcome",
    year: int | list[int] | None = None,
    type: str = "deviation",  # deviation, progress, gap
    format: str = "json"
) -> dict:
    """
    Export indicator data for deviation/progress/gap charts.
    
    Returns data with pre-calculated deviations, colors, etc.
    """
```

#### 2. Add Report Generation Tools

```python
# tools/reports.py

@mcp.tool()
async def unhcr_generate_country_report(
    country_code: str,
    year: int,
    include_charts: bool = False,
    format: str = "json"  # or "html", "pdf" (future)
) -> dict:
    """
    Generate a comprehensive country report.
    
    Returns structured data that can be:
    - Used directly by AI agents for narrative generation
    - Rendered as HTML/PDF reports
    - Exported for external visualization
    
    Sections:
    - Executive Summary
    - Sector Analysis
    - Donor Analysis
    - Implementation Analysis
    - Results Framework
    - Financial Analysis
    """

@mcp.tool()
async def unhcr_generate_donor_report(
    donor_name: str,
    year: int,
    format: str = "json"
) -> dict:
    """Generate a donor profile report."""

@mcp.tool()
async def unhcr_generate_operation_report(
    operation_id: str,
    year: int,
    format: str = "json"
) -> dict:
    """Generate an operation profile report."""
```

### Priority 3: AI Agent Enhancements (1-2 weeks)

#### 1. Add Natural Language to Chart Mapping

Create a mapping from natural language queries to recommended charts:

```python
# In a new module: tools/ai_helpers.py

NL_TO_CHART = {
    "most funded sectors": {
        "tool": "unhcr_most_funded_sectors",
        "chart_type": "horizontal_bar",
        "required_params": ["country_code", "year"],
        "color_palette": "unhcr_sector"
    },
    "top donors": {
        "tool": "unhcr_top_donors",
        "chart_type": "bar",
        "required_params": ["country_code", "year"],
        "color_palette": "traffic_light"
    },
    "expenditure vs budget": {
        "tool": "unhcr_budget_vs_expenditure",
        "chart_type": "deviation_bar",
        "required_params": ["country_code", "year"],
        "color_palette": "traffic_light"
    },
    "indicator trends": {
        "tool": "unhcr_indicator_trends",
        "chart_type": "line_with_thresholds",
        "required_params": ["country_code", "result_type", "year"],
        "color_palette": "outcome_areas"
    },
    "earmarking breakdown": {
        "tool": "unhcr_earmarking_analysis",
        "chart_type": "donut",
        "required_params": ["year"],
        "color_palette": "earmarking"
    },
    "partnership levels": {
        "tool": "unhcr_partnership_levels",
        "chart_type": "heatmap",
        "required_params": ["country_code"],
        "color_palette": "partnership"
    }
}

@mcp.tool()
async def unhcr_suggest_chart(
    query: str,
    context: dict | None = None
) -> dict:
    """
    Suggest appropriate chart type and tool for a natural language query.
    
    Example:
    query: "Show me the most funded sectors in Kenya for 2025"
    
    Returns:
    {
        "query_type": "sector_analysis",
        "recommended_tool": "unhcr_most_funded_sectors",
        "recommended_chart": "horizontal_bar",
        "required_params": {"country_code": "KE", "year": 2025},
        "color_palette": "unhcr_sector",
        "data_format": "chart_ready"
    }
    """
```

#### 2. Add AI Prompt Templates

```python
# tools/ai_prompts.py

AI_PROMPT_TEMPLATES = {
    "sector_analysis": """
    Analyze the sector funding data for {country} in {year}.
    
    Context:
    - Data is from UNHCR's IATI publications (publisher_ref: XM-DAC-41121)
    - Values are in USD
    - Sector vocabulary: {vocabulary}
    
    Key Questions to Address:
    1. Which sectors received the most funding?
    2. What percentage of total funding goes to each sector?
    3. How does this compare to previous years?
    4. Are there any notable shifts in sector priorities?
    
    Data Structure:
    {data_preview}
    
    Please provide:
    - A 2-3 paragraph executive summary
    - 3-5 key findings as bullet points
    - A recommendation section
    """,
    
    "indicator_deviation": """
    Analyze the indicator deviation data for {country} {result_type} indicators in {year}.
    
    Context:
    - Deviation = (actual - target) / target * 100
    - Positive deviation = exceeding target (good for most indicators)
    - Negative deviation = below target
    - Color coding: Green (≥ -1%), Orange (-15% to -1%), Red (< -15%)
    
    Key Questions:
    1. Which indicators are on target (green)?
    2. Which indicators need attention (orange/red)?
    3. What patterns do you see across Outcome Areas?
    4. What recommendations would you make?
    
    Data:
    {data_preview}
    """,
    
    "financial_comparison": """
    Analyze the budget vs expenditure comparison for {country} in {year}.
    
    Context:
    - Budget = planned allocations
    - Expenditure = actual spending
    - Execution rate = expenditure / budget * 100
    
    Key Questions:
    1. What is the overall execution rate?
    2. Which sectors have high/low execution rates?
    3. What might explain deviations from 100%?
    4. Are there concerns about absorption capacity?
    """
}

@mcp.tool()
async def unhcr_generate_ai_prompt(
    tool_name: str,
    params: dict,
    data: dict | None = None
) -> dict:
    """
    Generate an AI prompt for analyzing data from a specific tool.
    
    Returns a structured prompt that can be used with any LLM.
    """
```

### Priority 4: Documentation Enhancements (2-3 days)

#### 1. Add Analytical Framework Documentation

Create `docs/ANALYTICAL_FRAMEWORK.md`:

```markdown
# UNHCR IATI Analytical Framework

## Overview

This document describes the standardized analytical framework for UNHCR IATI data, ensuring consistent analysis across all operations, countries, and time periods.

## 7 Standard Questions

Every UNHCR operation should be analyzed through these 7 lenses:

### 1. Sector Funding Analysis
**Question:** What are the most funded sectors per country?
**Purpose:** Understand priority areas and resource allocation
**Tools:** `unhcr_most_funded_sectors`, `unhcr_sector_summary`
**Visualization:** Horizontal bar chart, treemap

### 2. Donor Analysis
**Question:** Who are the main donors by country?
**Purpose:** Identify funding sources and partnerships
**Tools:** `unhcr_top_donors`, `unhcr_donor_breakdown`
**Visualization:** Horizontal bar chart

... (all 7 questions)

## Results Framework

### Outcome Areas (16)

UNHCR's Results Framework is organized into 16 Outcome Areas (OA):

| Code | Area | Color |
|------|------|-------|
| OA1 | Access to Territory, Reg. and Documentation | #F0A3FF |
| OA2 | Status Determination | #C20088 |
| ... | ... | ... |

### Indicator Calculation Methods

#### Deviation Analysis
```
Deviation (%) = (actual - target) / target * 100
```
- **Green:** ≥ -1% (on or above target)
- **Orange:** -15% to -1% (slightly below)
- **Red:** < -15% (significantly below)

#### Progress Analysis
```
Progress (%) = (actual - baseline) / baseline * 100
```
Same color coding as deviation.

#### Gap Analysis
```
Gap to Green (%) = (actual - threshold_green) / threshold_green * 100
```
Only available for Outcome indicators published after 2022.

## Code Tables

All IATI codes are available as MCP resources:

- `unhcr://codes/country` - ISO 2-letter country codes
- `unhcr://codes/sector` - Sector codes and names
- `unhcr://codes/organisation` - Organisation identifiers
- `unhcr://codes/earmarking_category` - Earmarking types
- `unhcr://codes/outcome_areas` - 16 Outcome Areas with colors

See [Code Reference](CODES.md) for complete list.
```

#### 2. Add Visualization Guide

Create `docs/VISUALIZATION.md`:

```markdown
# Visualization Guide for UNHCR IATI Data

## Recommended Chart Types by Question

### Sector Analysis
| Question | Chart Type | Tool | Data Format |
|---------|------------|------|-------------|
| Most funded sectors | Horizontal Bar | `unhcr_most_funded_sectors` | chart_ready |
| Sector trends over time | Stacked Area | `unhcr_sector_trends` | time_series |
| Sector vs budget | Grouped Bar | `unhcr_sector_budget_comparison` | comparison |

### Donor Analysis
| Question | Chart Type | Tool | Data Format |
|---------|------------|------|-------------|
| Top donors | Horizontal Bar | `unhcr_top_donors` | chart_ready |
| Donor trends | Line Chart | `unhcr_donor_trends` | time_series |
| Donor breakdown | Pie/Donut | `unhcr_donor_breakdown` | chart_ready |

### Indicator Analysis
| Question | Chart Type | Tool | Data Format |
|---------|------------|------|-------------|
| Deviation from target | Bar (with colors) | `unhcr_indicator_deviation` | chart_ready |
| Progress from baseline | Bar (with colors) | `unhcr_indicator_progress` | chart_ready |
| Gap to threshold | Bar (with colors) | `unhcr_indicator_gap` | chart_ready |
| Trends over time | Line with thresholds | `unhcr_indicator_trends` | time_series |

## Color Palettes

### UNHCR Outcome Areas
```css
.OA1 { fill: #F0A3FF; } /* Access to Territory */
.OA2 { fill: #C20088; } /* Status Determination */
.OA3 { fill: #993F00; } /* Protection Policy */
.OA4 { fill: #FF3A21; } /* SGBV */
.OA5 { fill: #FFCC99; } /* Child Protection */
.OA6 { fill: #00689D; } /* Safety and Justice */
.OA7 { fill: #94FFB5; } /* Community Engagement */
.OA8 { fill: #e5243b; } /* Well-Being (SDG red) */
.OA9 { fill: #FD9D24; } /* Housing */
.OA10 { fill: #4C9F38; } /* Healthy Lives (SDG green) */
.OA11 { fill: #C5192D; } /* Education */
.OA12 { fill: #26BDE2; } /* WASH (SDG blue) */
.OA13 { fill: #A21942; } /* Livelihoods */
.OA14 { fill: #9DCC00; } /* Repatriation */
.OA15 { fill: #191919; } /* Resettlement */
.OA16 { fill: #2BCE48; } /* Local Integration */
```

### Traffic Light (Status)
```css
.green { fill: #069C56; }    /* On target */
.orange { fill: #FF980E; }   /* Needs attention */
.red { fill: #D3212C; }      /* Critical */
```

## Data Export Formats

All chart-ready data exports include:

```json
{
  "metadata": {
    "title": "Chart Title",
    "subtitle": "Chart Subtitle",
    "source": "UNHCR IATI Data",
    "recommended_chart": "horizontal_bar",
    "color_palette": "unhcr_sector"
  },
  "data": [
    {
      "id": "sector_code",
      "label": "Sector Name",
      "value": 1000000,
      "percentage": 25.5,
      "color": "#4C9F38"
    }
  ],
  "chart_config": {
    "type": "horizontal_bar",
    "x_axis": "value",
    "y_axis": "label",
    "color_by": "category",
    "show_labels": true
  }
}
```
```

---

## Implementation Priority Matrix

### Phase 1: Critical (Week 1-2) - Foundation

| Task | Priority | Effort | Impact | Dependencies |
|------|----------|--------|--------|--------------|
| Add 14 extractor tools | High | 2 days | High | None |
| Add 7 analytical question tools | High | 3 days | High | Extractor tools |
| Embed code tables as resources | High | 1 day | High | None |
| Create bulk extraction tool | High | 1 day | Medium | None |
| Add chart-ready export | Medium | 2 days | Medium | Analytical tools |

**Total: ~9 days, High ROI**

### Phase 2: Important (Week 3-4) - Enhancements

| Task | Priority | Effort | Impact | Dependencies |
|------|----------|--------|--------|--------------|
| Add report generation tools | Medium | 3 days | High | Phase 1 |
| Add AI prompt templates | Medium | 2 days | Medium | Phase 1 |
| Add NL to chart mapping | Medium | 1 day | Medium | Phase 1 |
| Create analytical framework docs | Medium | 2 days | Medium | None |
| Create visualization guide | Medium | 2 days | Medium | Phase 1 |

**Total: ~10 days, Medium ROI**

### Phase 3: Nice-to-Have (Week 5+) - Polish

| Task | Priority | Effort | Impact | Dependencies |
|------|----------|--------|--------|--------------|
| Add Quarto integration | Low | 3 days | Low | Phase 2 |
| Add PDF export | Low | 2 days | Low | Phase 2 |
| Add interactive chart export | Low | 3 days | Low | Phase 2 |
| Create code table lookup tools | Low | 1 day | Low | Phase 1 |

**Total: ~9 days, Low ROI**

### Priority Scoring

- **High Priority**: Required for production readiness, blocks other work
- **Medium Priority**: Significant value add, reasonable effort
- **Low Priority**: Nice to have, can wait

---

## Technical Appendices

### Appendix A: IATI XML Structure

The R package extracts from this XML structure:

```xml
<iati-activities>
  <iati-activity>
    <iati-identifier>XM-DAC-41121-...</iati-identifier>
    <reporting-org ref="XM-DAC-41121" type="10">
      <narrative>UNHCR</narrative>
    </reporting-org>
    <title>
      <narrative>Activity Title</narrative>
    </title>
    <activity-date iso-date="2025-01-01" type="1">2025-01-01</activity-date>
    <recipient-country code="AF" percentage="100">Afghanistan</recipient-country>
    
    <!-- Multiple transactions -->
    <transaction ref="1" humanitarian="1">
      <transaction-type code="11">...</transaction-type>
      <transaction-date iso-date="2025-03-15"></transaction-date>
      <value currency="USD" value-date="2025-03-15">1000000</value>
      <provider-org ref="US-GOV-1" type="10">
        <narrative>USAID</narrative>
      </provider-org>
      <aid-type code="A01" vocabulary="1">...</aid-type>
    </transaction>
    
    <!-- Multiple sectors -->
    <sector vocabulary="1" vocabulary-uri="..." code="12220" percentage="50">
      <narrative>Basic health care</narrative>
    </sector>
    
    <!-- Multiple budgets -->
    <budget type="1" status="1">
      <period-start iso-date="2025-01-01"></period-start>
      <period-end iso-date="2025-12-31"></period-end>
      <value currency="USD" value-date="2025-01-01">2000000</value>
    </budget>
    
    <!-- Results framework -->
    <result type="2" aggregation-status="1">
      <title>
        <narrative>Outcome 1: Access to Territory</narrative>
      </title>
      <indicator>
        <title>
          <narrative>Number of people with access to territory</narrative>
        </title>
        <measure code="1">1</measure>
        <baseline year="2024" value="1000">
          <location ref="AF">Afghanistan</location>
        </baseline>
        <period>
          <period-start iso-date="2025-01-01"></period-start>
          <period-end iso-date="2025-12-31"></period-end>
          <target>
            <location ref="AF">Afghanistan</location>
            <value>1500</value>
          </target>
          <actual>
            <location ref="AF">Afghanistan</location>
            <value>1200</value>
          </actual>
        </period>
      </indicator>
    </result>
    
    <!-- Participating organizations -->
    <participating-org ref="US-GOV-1" type="10" role="1" activity-id="XM-DAC-41121-...">
      <narrative>USAID</narrative>
    </participating-org>
    
    <!-- Locations -->
    <location ref="AF-KAN" reach-code="1">
      <name>
        <narrative>Kandahar</narrative>
      </name>
      <location-id vocabulary="G1" code="AF.KAN">Kandahar</location-id>
    </location>
    
    <!-- And 5 more element types... -->
  </iati-activity>
</iati-activities>
```

### Appendix B: Data Field Mapping (R → MCP)

| R Field | MCP Field | Type | Description |
|---------|-----------|------|-------------|
| iati_identifier | iati_identifier | string | Unique activity identifier |
| reporting_org_ref | reporting_org_ref | string | Reporting organisation reference |
| title_eng | title | string | Activity title (English) |
| description_eng_1 | description | string | Activity description |
| activity_status_code | status | string | Activity status code |
| activity_date_1 | start_date | string | Activity start date |
| activity_date_2 | end_date | string | Activity end date |
| recipient_country_code | country_code | string | ISO 2-letter country code |
| recipient_country | country_name | string | Country name |
| budget_type | budget_type | string | Budget type code |
| budget_status | budget_status | string | Budget status code |
| budget_value | budget_value | float | Budget amount (USD) |
| transaction_type_code | transaction_type | string | Transaction type code |
| transaction_date | transaction_date | string | Transaction date |
| transaction_value_USD | transaction_value | float | Transaction amount (USD) |
| transaction_provider_org_ref | donor_ref | string | Donor organisation reference |
| transaction_provider_org | donor_name | string | Donor organisation name |
| sector_vocabulary | sector_vocabulary | string | Sector vocabulary |
| sector_code | sector_code | string | Sector code |
| sector_desc | sector_name | string | Sector name |
| sector_pct | sector_percentage | float | Sector percentage |
| result_type_name | result_type | string | Result type (Impact/Outcome/Output) |
| result_title | result_title | string | Result title |
| result_indicator_title | indicator_title | string | Indicator title |
| result_indicator_measure | indicator_measure | string | Indicator measure |
| result_indicator_baseline_value | baseline | float | Baseline value |
| result_indicator_target_value | target | float | Target value |
| result_indicator_actual_value | actual | float | Actual value |
| result_indicator_ascending | ascending | int | Indicator direction (0=descending, 1=ascending) |
| participating_org_ref | org_ref | string | Organisation reference |
| participating_org | org_name | string | Organisation name |
| participating_org_type | org_type | string | Organisation type |
| participating_org_role | org_role | string | Organisation role code |

### Appendix C: R Package Dependencies

The R package uses these key packages:

- **xml2** - XML parsing (equivalent to Python's xml.etree or lxml)
- **rvest** - Web scraping (for HTML data)
- **httr** - HTTP requests (equivalent to httpx in Python)
- **dplyr** - Data manipulation (equivalent to pandas)
- **tibble** - Modern data frames
- **purrr** - Functional programming (equivalent to Python's built-ins)
- **furrr** - Parallel processing (equivalent to asyncio + concurrent.futures)
- **future** - Parallel backend
- **ggplot2** - Visualization (equivalent to matplotlib/plotly)
- **scales** - Scale functions for ggplot2
- **unhcrthemes** - UNHCR-branded themes
- **stringr** - String manipulation (equivalent to Python's str methods)
- **glue** - String interpolation (equivalent to f-strings)
- **fusen** - Documentation generation
- **quarto** - Report generation
- **writexl** - Excel export
- **fs** - File system operations

### Appendix D: Performance Considerations

**R Package:**
- Uses parallel processing (multisession) for extraction
- Processes ~20,000+ activities per year
- Typical extraction time: 30-60 seconds for full UNHCR dataset
- Memory usage: ~2-4 GB for full dataset

**MCP Server Targets:**
- Use async I/O for API requests
- Implement connection pooling (max 50, already configured)
- Add rate limiting (already in client.py)
- Target response time: < 500ms for simple queries, < 2s for complex
- Memory usage: < 1 GB

### Appendix E: File References

| File | Purpose | Lines of Interest |
|------|---------|------------------|
| README.md | Package overview | 65-71 (key questions), 88-90 (structure) |
| dev_data_reshape.Rmd | Data extraction | 45-519 (extractors), 541-561 (parallel processing) |
| dev_unhcr_programme.Rmd | Visualizations | 137-1081 (chart functions), 347-344 (color palette) |
| dev_report.Rmd | Report generation | 28-147 (generate_report), 67-76 (batch processing) |
| build.R | Package build | N/A |
| data.R | Pre-processed data | N/A |
| *.RData | Code tables | N/A (binary) |
| mapping_*.RData | Mappings | N/A (binary) |

---

## Next Steps

1. **Immediate (Today):**
   - Review this document with the team
   - Prioritize Phase 1 tasks
   - Assign owners to each task

2. **This Week:**
   - Implement bulk extraction tool
   - Embed 5 most-used code tables (country, sector, donor, organisation, earmarking)
   - Add 2-3 extractor tools as proof of concept

3. **Next Week:**
   - Complete all Phase 1 tasks
   - Begin Phase 2 (report generation)
   - Test with real UNHCR data

4. **Ongoing:**
   - Document each new feature
   - Add tests for each new tool
   - Update README with examples

---

*Generated from R-analysis review: 2025-07-03*
*Author: MCP Server Development Team*
