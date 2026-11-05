# flakeradar
when we perform a test on a code sometimes it passes and sometimes it fails so our flakeradar will maintain a record of these test results

FlakeRadar

One line: FlakeRadar is a tool that reads the test results from a project’s CI robot and tells the team which tests are unreliable, and why.

The problem
Some tests pass and fail at random even when the code hasn’t changed. These are called flaky tests. Programmers waste hours investigating false alarms or re-running the robot until it turns green. Worse, people start ignoring failures, so a real bug can hide behind “probably flaky.” Large companies like Atlassian have built internal tools for this, but small teams and open-source projects rarely have one.

Who needs it

Developers who are tired of red results they can’t trust.
Maintainers of open-source projects whose CI keeps failing randomly.
Small teams that can’t afford a paid tool.

What FlakeRadar will do (the MVP, first working version)

Fetch test results from a public project’s GitHub Actions history.
Store every result in a database, with the test name, pass or fail, the code version, and the time.
Find flaky tests using simple, explainable rules. The strongest signal is the same test passing and failing on the same code version, because the code didn’t change but the result did. A second signal is how often a test flips between pass and fail over time.
Show a ranked list: “These are the 10 most unreliable tests, and here is the evidence for each.”

What we may add later (only if each solves a real problem)

Group similar failure messages, to guess the likely cause.
Post a comment on a pull request saying “this failure looks like a known flaky test.”
A small dashboard.
Move the database to PostgreSQL and make it faster with indexes.

What it will NOT do

It won’t fix the flaky tests. It only finds them and shows the evidence.
It won’t claim certainty. Detection is based on statistics, so it gives a likelihood, not a guarantee.
It won’t use AI unless AI clearly earns its place.
It won’t use made-up data. We test on real open-source projects.

How it works, in a picture

GitHub Actions (CI results)
          |
          v
  Fetch the results
          |
          v
  Store in the database
          |
          v
  Analyze: which tests flip results?
          |
          v
  Ranked list of flaky tests + evidence

Tools: Python, FastAPI, SQLite (PostgreSQL later), pytest, Git and GitHub, GitHub Actions, VS Code.

How we’ll judge success (honestly)

It finds flaky tests in real open-source projects, and we can show the evidence.
We measure how many of its flags are wrong (false alarms) and say so openly.
You can explain every design decision and its trade-offs.

What you’ll learn by building it: working with a database, building an API, handling messy real data, basic statistics, testing, and deploying a project, all of which appear in placement interviews.