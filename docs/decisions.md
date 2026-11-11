Decision Note: Test ID Normalization

1. What problem did we face?
Some test names contain memory addresses or UUIDs that change evry time tests run. Because of this, FlakeRadar may identify the same test as two diffrent tests.

2. What did we decide?
We decided to normalize test names by replacing changing memory addresses with 0x? and UUIDs with <uuid> when generating test IDs. We preserve the original test names in the CaseResult model.

3. Why did we choose this approach?
This approach helps FlakeRadar recognize the same test across multiple runs, even when its memory address or UUID changes.

4. What is the downside?
Two genuinely different tests containing different UUIDs could accidentally get the same normalized ID. This may cause FlakeRadar to treat them as one test.


Basic Flaky Detector - Design Decisions

1. How does FlakeRadar decide whether a test is flaky?
FlakeRadar checks whether a test has both passed and failed under identical conditions (same commit, Python version, and operating system). If the results are inconsistent, it classifies the test as flaky. It requires at least five runs before making a classification. Errors are treated as failures, while skipped tests are ignored.

2. Why are changes across commits weaker evidence?
When a test's result changes across different commits, the code itself may have changed. The result could be due to a bug fix or a newly introduced bug rather than randomness. Therefore, changes across commits are weaker evidence of flakiness.

3. What are the limitations of this detector?
The detector considers only recorded conditions. Changes in libraries, machine load, or execution time may go unnoticed. Missing environment information may also affect how runs are grouped. The minimum requirement of five runs is a judgment-based threshold, not a proven confidence measure. Additionally, analyzing every test may become slower as the database grows.