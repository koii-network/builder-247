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

### Changes Made
<!-- BEGIN_CHANGES -->
{changes}
<!-- END_CHANGES -->

### Tests and Verification
<!-- BEGIN_TESTS -->
{tests}
<!-- END_TESTS -->

### PRs Merged
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
    "review_template": """
<!-- BEGIN_TITLE -->
# {title}
<!-- END_TITLE -->

<!-- BEGIN_DESCRIPTION -->
## Description
{description}
<!-- END_DESCRIPTION -->

<!-- BEGIN_RECOMMENDATION -->
## Recommendation
{recommendation}

Reasons:
{recommendation_reasons}
<!-- END_RECOMMENDATION -->

<!-- BEGIN_UNMET_REQUIREMENTS -->
## Unmet Requirements
{unmet_requirements}
<!-- END_UNMET_REQUIREMENTS -->

<!-- BEGIN_TESTS -->
## Tests

### Failed Tests
{failed_tests}

### Missing Test Cases
{missing_tests}
<!-- END_TESTS -->

<!-- BEGIN_ACTION_ITEMS -->
## Action Items
{action_items}
<!-- END_ACTION_ITEMS -->

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
}
