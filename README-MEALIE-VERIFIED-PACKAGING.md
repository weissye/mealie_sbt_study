# Install without replay

Extract this delta into the study root. It changes only tools/run_mealie_generator_live.py, adds an offline packaging regression test, and preserves a sanitized copy of the supplied successful review with qualification and handoff. Existing generator source is unchanged.

Run `py -3 -B tools/test_mealie_review_packaging.py` to check packaging without contacting Mealie. No replay is needed for the completed two-tag acceptance. Do not publish the original review.zip: native model/products contains an authentication token. This correction prevents that directory from entering future review archives; it does not erase private native products on disk.

Archive the evidence directory and documentation in Git according to your normal evidence workflow. This package has not been committed or pushed on your computer.
