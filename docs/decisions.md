Decision Note: Test ID Normalization

1. What problem did we face?
Some test names contain memory addresses or UUIDs that change evry time tests run. Because of this, FlakeRadar may identify the same test as two diffrent tests.

2. What did we decide?
We decided to normalize test names by replacing changing memory addresses with 0x? and UUIDs with <uuid> when generating test IDs. We preserve the original test names in the CaseResult model.

3. Why did we choose this approach?
This approach helps FlakeRadar recognize the same test across multiple runs, even when its memory address or UUID changes.

4. What is the downside?
Two genuinely different tests containing different UUIDs could accidentally get the same normalized ID. This may cause FlakeRadar to treat them as one test.