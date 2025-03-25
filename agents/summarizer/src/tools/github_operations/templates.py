TEMPLATES = {
    "pr_template": ("# {title}\n\n" "## Summary of Changes\n" "{description}\n\n"),
    "review_template": (
        "# PR Review: {title}\n\n"
        "## Recommendation: {recommendation}\n\n"
        "### Justification\n"
        "{recommendation_reasons}\n\n"
        "## Summary of Changes\n"
        "{description}\n\n"
        "## Requirements Review\n"
        "### ✅ Met Requirements\n"
        "{met_requirements}\n\n"
        "### ❌ Unmet Requirements\n"
        "{unmet_requirements}\n\n"
        "## Test Evaluation\n"
        "### Passed Tests\n"
        "{passed_tests}\n\n"
        "### Failed Tests\n"
        "{failed_tests}\n\n"
        "### Missing Test Cases\n"
        "{missing_tests}\n\n"
        "## Action Items\n"
        "{action_items}\n\n"
    ),
}
