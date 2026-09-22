# **String Cleaning & Standardization Pipeline — PRD**

## **1. Overview**

Build a reusable Python string-cleaning pipeline that standardizes inconsistent text data received from multiple sources.

The pipeline should transform messy text into consistent, analysis-ready values while handling whitespace, casing, special characters, categorical variations, and null values.

---

## **2. Objectives**

- Remove leading and trailing whitespace.
- Normalize text casing.
- Remove unwanted special characters.
- Standardize categorical labels.
- Handle null and empty values safely.
- Create reusable cleaning functions.
- Validate transformations using before/after comparisons.
- Make the pipeline reusable across datasets.

---

## **3. Project Setup**
4.1 Whitespace Cleaning

Apply .str.strip() to all string columns.

df[col] = df[col].str.strip()

The pipeline must:

Identify string columns.
Remove leading/trailing whitespace.
Compare unique values before and after cleaning.
Show value_counts() for at least 2 columns.
4.2 Casing Normalization

Convert categorical text to a consistent case.

Preferred standard:

df[col] = df[col].str.lower()

Example:

JOHN → john
John → john
john → john

The pipeline must:

Normalize at least 3 columns.
Use one consistent casing standard.
Document the casing decision.
Show before/after examples.
4.3 Special Character Removal

Remove unwanted characters using:

r"[^a-zA-Z0-9 ]"

Example:

df[col] = df[col].str.replace(
    r"[^a-zA-Z0-9 ]",
    "",
    regex=True
)

Example transformation:

São Paulo → So Paulo
Montréal → Montral
Product_C → ProductC

The pipeline must:

Use regex for cleaning.
Handle international characters.
Show before/after examples.
Document the regex pattern.
4.4 Categorical Standardization

Create mapping dictionaries to consolidate variations.

Example:

segment_map = {
    "b2b": "B2B",
    "b 2 b": "B2B",
    "business-to-business": "B2B",
    "sme": "SMB",
    "small medium enterprise": "SMB",
    "enterprise": "Enterprise"
}

Apply using:

df["segment"] = df["segment"].replace(segment_map)

Requirements:

At least 3 categories.
At least 3 variations per category.
Document the canonical value for each category.
Show before/after value_counts().
5. Reusable Cleaning Function

Create:

def clean_text_column(
    series,
    lowercase=True,
    strip=True,
    remove_special=False,
    mapping=None
):
    ...

The function must support:

Lowercase conversion.
Whitespace removal.
Special-character removal.
Optional mapping.
Null-value handling.
Reuse across different columns.

Example:

df["name"] = clean_text_column(
    df["name"],
    lowercase=True,
    strip=True
)

df["segment"] = clean_text_column(
    df["segment"],
    mapping=segment_map
)

df["location"] = clean_text_column(
    df["location"],
    lowercase=True,
    strip=True,
    remove_special=True
)
6. Testing Requirements

Test the pipeline using:

test_cases = [
    "  Product A  ",
    "PRODUCT B",
    "Product_C",
    None,
    ""
]

Verify:

Whitespace is removed.
Casing is normalized.
Special characters are removed.
Null values do not cause errors.
Empty strings are handled correctly.
7. Validation

The pipeline should provide evidence of successful cleaning through:

Before/after value_counts().
Before/after .head() samples.
Unique-value comparisons.
Special-character examples.
Categorical mapping results.
Edge-case test results.
8. Deliverables
Required File
scripts/string_cleaning_pipeline.py
The Script Must Include
Whitespace cleaning.
Casing normalization.
Special-character removal.
Categorical mapping.
Reusable cleaning function.
Null handling.
Test cases.
Before/after validation.