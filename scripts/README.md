# Scripts

Phase 1 support utilities:

- `profile_dataset.py` performs read-only CSV inspection and writes the measured dataset profile.
- `generate_artifacts.py` renders the architecture PNG and proposal PDF from the Phase 1 documentation.
- `generate_presentation_brief.py` renders the concise four-page PDF used for email and the live presentation.

Phase 2 ingestion components:

- `ingest.py` is the command-line entry point for raw ingestion and full source profiling.
- `ingestion/` contains environment configuration, strict streaming CSV parsing, PostgreSQL access, raw loading, profiling, and logging modules.
- `Dockerfile` builds the one-shot Python 3.12 ingestion image.
- `requirements.txt` contains the minimal runtime dependency (`psycopg`).

Run the supported container workflow from the repository root:

```bash
docker compose run --rm ingestion --strict-files
```

Useful options:

```bash
docker compose run --rm ingestion --profile-only --strict-files
docker compose run --rm ingestion --skip-profile
docker compose run --rm ingestion --force --skip-profile
```

Transformation and analytical modeling intentionally remain outside Phase 2.
