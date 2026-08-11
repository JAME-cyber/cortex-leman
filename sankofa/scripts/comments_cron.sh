#!/bin/bash
# Sankofa Comments Watchdog
# Runs comment_manager.py, auto-posts replies, delivers summary only when new comments found.
# Silent when no new comments (watchdog pattern).

cd /home/tars/sankofa

OUTPUT=$(python3 comment_manager.py --post 2>&1)

# Only deliver if there's actual content (new comments found)
if [ -n "$OUTPUT" ]; then
    echo "$OUTPUT"
fi
