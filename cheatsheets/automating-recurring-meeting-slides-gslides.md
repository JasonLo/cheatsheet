# Automating recurring meeting slides with gslides

_Grounded in JasonLo's repos as of 2026-11-03. Current practice is from developers.google.com/workspace/slides/api._

## Reference snippet

```python
# Authenticate with a service account and replace template placeholders in one batch.
from google.oauth2 import service_account
from googleapiclient.discovery import build

SCOPES = ["https://www.googleapis.com/auth/presentations"]
creds = service_account.Credentials.from_service_account_file("key.json", scopes=SCOPES)
slides = build("slides", "v1", credentials=creds)

# Copy the template presentation first (uses Drive API).
drive = build("drive", "v3", credentials=creds)
copy = drive.files().copy(fileId=TEMPLATE_ID, body={"name": "Standup 2026-11-03"}).execute()
deck_id = copy["id"]

# Replace all {{placeholder}} tokens in one batchUpdate call.
requests = [
    {"replaceAllText": {"containsText": {"text": "{{DATE}}", "matchCase": True},
                        "replaceText": "2026-11-03"}},
    {"replaceAllText": {"containsText": {"text": "{{OWNER}}", "matchCase": True},
                        "replaceText": "JasonLo"}},
]
slides.presentations().batchUpdate(presentationId=deck_id, body={"requests": requests}).execute()
```

## Typical usage patterns

- **Template-copy then replace.** Keep one template presentation with `{{PLACEHOLDER}}` tokens and copy it with the Drive API before each meeting. Fill all tokens with `replaceAllText` in one `batchUpdate` call, which makes all modifications atomic.

- **Preflight before pushing.** Fetch the target presentation and confirm all required placeholder tokens are present before the main script runs. This prevents a botched push from producing a live deck with unfilled tokens.

- **Separate push, format, and preflight into distinct scripts.** Keep each concern in its own script so each step can be tested and re-run independently. Connect the scripts with a shell wrapper or a CI job.

## Learnings

- **Editing slides by index or position** → **edit slides by element ID from `replaceAllText` or `createSlide` responses**. Element IDs are stable across edits, but slide positions change when slides are reordered. Use the IDs returned by the API, not hardcoded positions.

- **One API call for each change** → **bundle all changes in a single `batchUpdate` call**. Each call to the Slides API costs a round trip and counts toward quota. A single `batchUpdate` with many requests is atomic and uses one round trip.

- **Storing credentials in the script or environment directly** → **use a service account key file and pass the path through an environment variable**. Hard-coded credentials leak into version history. A service account separates the automation identity from a personal OAuth session and does not require interactive login.

## Agent rules

- ALWAYS copy the template presentation with the Drive API before modifying it; never edit the template directly.
- ALWAYS bundle all slide edits into a single `batchUpdate` call, not one call for each change.
- ALWAYS use element IDs from API responses to target shapes; never use hardcoded slide or element indices.
- NEVER store service account key content in source code; pass the key file path through an environment variable.
- ALWAYS run a preflight check that confirms all placeholder tokens exist before the main push script runs.
