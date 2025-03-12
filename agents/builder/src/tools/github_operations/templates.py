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

### Summary of Work
<!-- BEGIN_DESCRIPTION -->
{description}
<!-- END_DESCRIPTION -->

### Changes Made
<!-- BEGIN_CHANGES -->
{changes}
<!-- END_CHANGES -->

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

## Description
### Summary of Work
<!-- BEGIN_DESCRIPTION -->
{description}
<!-- END_DESCRIPTION -->

### Consolidated Pull Requests
<!-- BEGIN_CONSOLIDATED_PRS -->
{consolidated_prs}
<!-- END_CONSOLIDATED_PRS -->

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
