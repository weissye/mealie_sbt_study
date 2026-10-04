# Dependency transfer control: oracle false positive

The uploaded campaign stopped in food-control sample 1, seed 287457, at the first target update. The nested live ZIP SHA-256 matches its result record. Expected and observed food responses differ only in updatedAt. The requested name persisted, and all other fields in that response were identical. This is an oracle false positive, not a confirmed Mealie defect. Later control phases and transfer probes were not executed; their behavior remains unknown.

## Correction

The generic opt-in dependency_transfer configuration explicitly declares target_timestamp_fields. Only documented date-time update fields can be configured. Only the successfully updated owned target may acquire a new timestamp. Its observed timestamp becomes the baseline for later reads. Other targets remain strictly protected, including their timestamps. Identities, creation timestamps, names, quantities and references remain protected. The independent receipt validator applies the same scoped rule and validates timestamp syntax. Existing configurations without the option keep strict comparison.

## Git evidence

The supplied console log records TRANSFER_WORK_PUSH_VERIFIED for commit 2e02325e8dd007e6260daa7507b389734d3ec2f4 before this campaign began. This campaign and the timestamp correction require a subsequent commit. No live acceptance is claimed for the corrected generator until a new owned-resource run completes.
