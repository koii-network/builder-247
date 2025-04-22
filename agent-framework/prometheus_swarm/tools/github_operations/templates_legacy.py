TEMPLATES = {
    "pr_template": ("# {title}\n\n" "## Summary of Changes\n" "{description}\n\n"),
    "review_template": (
        "# PR Review: {title}\n\n"
        "## Recommendation: {recommendation}\n\n"
        "### Justification\n"
        "{recommendation_reasons}\n\n"
    ),
}