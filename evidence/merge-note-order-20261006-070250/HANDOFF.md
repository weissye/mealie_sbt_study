# Merge note-order qualification

Source release was pushed at d3d5c752a40270d79f505f1fff3ba6682099c4f1. The preserved merge run stopped at `MERGE_RESPONSE_STATE_MISMATCH`. The POST response retained identity and list/food/unit bindings and returned quantity 3 after adding 2 to 1. Both notes were present, in the reverse of the exact concatenation order assumed by the oracle. That ordering requirement was not established by the contract.

The original archive remains unchanged. This is an oracle false positive, not a confirmed new application defect. Independent post-merge item/list reads were not reached. A corrected merge-only experiment uses fresh resources; the accepted distinct control does not need to be repeated.

The repair compares exact note components as a multiset at the POST response, item GET and list GET. It preserves existing quantity, identity, binding and unrelated-item checks. Local tests execute the archived generated callbacks with stubs; they are not a native replay or a Mealie result.
