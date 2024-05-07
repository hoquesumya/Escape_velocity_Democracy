# TESTING.md

This file describes how we test the Escape Velocity for Democracy blockchain project.

## Testing

We used a variety of techniques to test the project, including [pytest](https://docs.pytest.org/en/latest/) and manual testing. Below are a few our our test cases. Further tests can be seen at the bottom of most .py files.
- Verify that blockchain length is consistent with what we expect.
- Verify that our strategy for handling forks works as expected. (unimplemented due to 2-person team)
- Verify that the blockchain rejects invalid transactions.
- Verify our proof of work algorithm works as expected.
