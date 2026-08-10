# Video API v2 support samples

A collection of older scripts I used while testing and supporting integrations
with an existing video-management API.

The repository shows the kind of hands-on work involved in reproducing partner
questions: authentication, REST requests, device status events, I/O control,
recordings, snapshots and media downloads. It does **not** represent an API
platform, a production SDK or a video backend that I built.

## Repository status

These are reference samples, not a maintained client library. They were created
for specific support and testing scenarios and have different levels of
completeness. Review the current provider documentation and each script before
running it. Endpoints, response formats and authentication flows may have
changed since the examples were written.

## Scenarios

| Folder | Integration scenario | Main evidence | Status |
| --- | --- | --- | --- |
| `deviceCameraIO` | Read or change camera I/O state | REST calls and response inspection | Historical sample |
| `eventsStatusWebsocket` | Observe device status changes | Authentication, account selection and WebSocket events | Historical sample; needs broader refactoring |
| `ldsSync` | Test local display station synchronisation | Exploratory notebook and support notes | Exploratory |
| `mediaBatchFLVDownload` | Download multiple media files | Concurrent downloads, progress and logging | Historical sample |
| `mediaEEMediaplayer` | Exercise a browser media player | JavaScript integration and playback setup | Vendor-library example |
| `mediaForceRecording` | Start and inspect a forced recording | REST calls, timing and diagnostic log viewer | Historical sample |
| `mediaMp4Downloader` | Download MP4 recordings over a date range | CLI arguments, timestamps and file handling | Most reusable v2 sample |
| `mediaSnapshotOfRecording` | Request a still image from a recording | Time conversion and media request | Historical sample |

## Safe local setup

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
```

Some older scripts expect a `baseaaa.json` file in their own folder:

```bash
cp eventsStatusWebsocket/baseaaa.example.json eventsStatusWebsocket/baseaaa.json
```

Fill the local copy only. `baseaaa.json` is excluded by `.gitignore`. Never put
real usernames, passwords, tokens, auth keys, account IDs, camera IDs or media
URLs in a commit, screenshot, issue or shared log.

Read [SECURITY.md](SECURITY.md) before connecting a sample to an account.

## What should be improved before production use

The samples intentionally remain labelled as historical because several still
need work:

- consistent request time-outs and `raise_for_status()` handling;
- pagination and explicit rate-limit/backoff behaviour;
- a shared authentication/configuration module;
- automated tests with mocked API responses;
- structured redacted logging and correlation IDs;
- removal of query-string credentials where the API supports safer transport;
- consistent command-line interfaces and output paths;
- confirmation of current API versions and endpoint behaviour.

Those gaps are listed openly so the repository is useful as evidence of
integration/support work without being mistaken for production-ready software.

## Independence and attribution

This is an independent personal collection and is not an official Eagle Eye
Networks project or supported SDK. Product and company names are used only to
identify the integration target. Some examples may be adapted from publicly
available developer material; retain original notices and identify the source in
the relevant folder when that applies.

No general open-source licence is currently declared for the whole repository.
Do not assume permission to redistribute vendor libraries or adapted source code
until ownership and applicable licences have been confirmed.
