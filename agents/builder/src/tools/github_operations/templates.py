TEMPLATES = {
    "pr_template": """<!-- BEGIN_TODO -->
{todo}
<!-- END_TODO -->

<!-- BEGIN_TITLE -->
{title}
<!-- END_TITLE -->

<!-- BEGIN_DESCRIPTION -->
{description}
<!-- END_DESCRIPTION -->

<!-- BEGIN_ACCEPTANCE_CRITERIA -->
{acceptance_criteria}
<!-- END_ACCEPTANCE_CRITERIA -->

<!-- BEGIN_TESTS -->
{tests}
<!-- END_TESTS -->
""",
    "review_template": """## Pull Request Review

### Title
{title}

### Description
{description}

### Requirements Met
{met_requirements}

### Requirements Not Met
{unmet_requirements}

### Test Coverage
#### Passing Tests
{passed_tests}

#### Failed Tests
{failed_tests}

#### Missing Test Cases
{missing_tests}

### Recommendation: {recommendation}

### Reasons
{recommendation_reasons}

### Action Items
{action_items}
""",
}
