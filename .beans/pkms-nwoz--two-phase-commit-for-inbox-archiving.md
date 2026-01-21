---
# pkms-nwoz
title: Two-phase commit for inbox archiving
status: draft
type: feature
priority: deferred
created_at: 2026-01-21T07:33:02Z
updated_at: 2026-01-21T07:33:02Z
---

Implement two-phase commit pattern for inbox archiving to prevent data loss.

## Current Risk

- Inbox file deleted immediately after copy
- If archive operation fails mid-process, data lost
- No recovery mechanism
- Single point of failure

## Two-Phase Commit Pattern

### Phase 1: Prepare
1. Copy inbox file to archive (with temp name)
2. Verify archive file integrity (hash check)
3. Create archive metadata/transaction log
4. DO NOT delete inbox file yet

### Phase 2: Commit
1. Rename temp archive file to final name
2. Mark transaction as committed
3. Delete inbox file
4. Clean up transaction log

### Recovery
- On startup, check for incomplete transactions
- Complete or rollback partial archives
- Ensure no data loss

## Implementation

```python
def archive_with_safety(inbox_path, archive_path):
    # Phase 1: Prepare
    temp_archive = archive_path + ".tmp"
    shutil.copy2(inbox_path, temp_archive)
    if hash_file(inbox_path) != hash_file(temp_archive):
        raise ArchiveError("Hash mismatch")
    
    # Phase 2: Commit
    os.rename(temp_archive, archive_path)
    os.unlink(inbox_path)
```

## Benefits

- No data loss even if process killed
- Atomic operations (rename is atomic)
- Recoverable partial state
- Idempotent retry safe

## Considerations

- Slightly slower due to extra verification
- Need transaction log or marker files
- Recovery code must run on startup
- Test with disk full scenarios

## Acceptance Criteria

- Zero data loss in chaos tests
- Recovery from interrupted archives
- Performance impact <10%
- Clear audit trail of all archives