TEMPLATES = {
    "worker_pr_template": """

<!-- BEGIN_TITLE -->
# {title}
<!-- END_TITLE -->

## Description
### Task
<!-- BEGIN_TODO -->
{todo}
<!-- END_TODO -->

### Acceptance Criteria
<!-- BEGIN_ACCEPTANCE_CRITERIA -->
{acceptance_criteria}
<!-- END_ACCEPTANCE_CRITERIA -->

### Changes Made
<!-- BEGIN_DESCRIPTION -->
{changes}
<!-- END_DESCRIPTION -->

### Tests
<!-- BEGIN_TESTS -->
{tests}
<!-- END_TESTS -->

## Signatures
### Staking Key
<!-- BEGIN_STAKING_KEY -->
{staking_key}: {staking_signature}
<!-- END_STAKING_KEY -->

### Public Key
<!-- BEGIN_PUB_KEY -->
{pub_key}: {public_signature}
<!-- END_PUB_KEY -->
""",
    "leader_pr_template": """

<!-- BEGIN_TITLE -->
# {title}
<!-- END_TITLE -->
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
