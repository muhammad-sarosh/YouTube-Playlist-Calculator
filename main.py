import json
import os
import re
from yt_dlp import YoutubeDL

# When True  → program **asks** “Use a saved playlist? (y/n)”.
# When False → program skips that question and jumps straight to the list of
#              stored playlists (if any).  If the JSON file is empty/invalid
#              it falls back to manual URL entry.
PROMPT_BEFORE_SAVED_PLAYLIST = False
PLAYLIST_DB_FILE = "playlists.json"           # JSON file path


# Saved-playlist helpers
def _load_saved_playlists() -> dict[str, str]:
    """Return {name: url} or {} if file missing/invalid."""
    if not os.path.exists(PLAYLIST_DB_FILE):
        return {}
    try:
        with open(PLAYLIST_DB_FILE, "r", encoding="utf-8") as fp:
            data = json.load(fp)
        # keep only str→str pairs
        return {k: v for k, v in data.items() if isinstance(k, str) and isinstance(v, str)}
    except Exception:
        return {}


def _select_saved_playlist(db: dict[str, str]) -> str | None:
    """Present numbered list; return chosen URL or None on failure."""
    if not db:
        return None
    print("\nAvailable saved playlists:")
    names = list(db.keys())
    for idx, name in enumerate(names, 1):
        print(f"{idx} - {name}")
    while True:
        choice = input("\nSelect playlist: ").strip()
        if not choice.isdigit():
            print("Enter a number.")
            continue
        idx = int(choice)
        if 1 <= idx <= len(names):
            return db[names[idx - 1]]
        print("Number out of range.")


# Generic input helpers
def get_valid_playlist_url() -> str:
    while True:
        url = input("\nEnter the YouTube playlist URL: ").strip()
        if re.match(r"^https?://(www\.)?youtube\.com/playlist\?list=", url):
            return url
        print("Invalid playlist URL format.")


def maybe_get_playlist_url() -> str:
    """
    Decide how to obtain the playlist URL, following the new rules:

      • If the JSON store is empty or invalid → prompt for URL directly.
      • Otherwise …
          – If PROMPT_BEFORE_SAVED_PLAYLIST is True  → ask y/n first.
          – If False                                 → jump straight to list.
    """
    db = _load_saved_playlists()
    if not db:                          # nothing stored → manual entry
        return get_valid_playlist_url()

    if PROMPT_BEFORE_SAVED_PLAYLIST:
        while True:
            ans = input("\nUse a saved playlist? (y/n): ").lower().strip()
            if ans in ("y", "n"):
                break
            print("Please answer y or n.")
        if ans == "y":
            url = _select_saved_playlist(db)
            if url:
                return url
        # chose “n” or invalid selection → manual entry
        return get_valid_playlist_url()

    # PROMPT_BEFORE_SAVED_PLAYLIST is False → pick directly
    url = _select_saved_playlist(db)
    return url if url else get_valid_playlist_url()


def get_valid_watch_time() -> int:
    while True:
        try:
            minutes = int(input("\nEnter the number of minutes you want to watch: "))
            if minutes > 0:
                return minutes
            print("Please enter a positive number.")
        except ValueError:
            print("Invalid input. Please enter an integer.")


def get_valid_start_input(max_index: int) -> tuple[int, int]:
    """
    Accept either:
        • “7”       → start from video 7 at 0:00
        • “7 4:57”  → start from video 7 at 4 min 57 s
    Returns (video_number, offset_seconds).
    """
    ts_re = re.compile(r"^(\d+):([0-5]?\d)$")  # mm:ss
    while True:
        raw = input(
            f"Enter the starting video number (max -> {max_index}) "
            "[optional timestamp mm:ss]: "
        ).strip()
        parts = raw.split()
        if len(parts) not in (1, 2):
            print("Please give either a video number or “number mm:ss”.")
            continue

        # video number
        try:
            vid_idx = int(parts[0])
        except ValueError:
            print("Video number must be an integer.")
            continue
        if not (1 <= vid_idx <= max_index):
            print("Number out of range.")
            continue

        # optional timestamp
        offset_sec = 0
        if len(parts) == 2:
            m = ts_re.match(parts[1])
            if not m:
                print("Timestamp must be in mm:ss (e.g. 4:07).")
                continue
            minutes, seconds = map(int, m.groups())
            offset_sec = minutes * 60 + seconds

        return vid_idx, offset_sec


# Utility routines
def seconds_to_mm_ss(seconds: int) -> tuple[int, int]:
    return divmod(int(seconds), 60)


def fetch_video_duration_and_title(url: str) -> tuple[int, str]:
    """Fallback request when playlist entry lacks a duration."""
    ydl_opts = {"quiet": True, "skip_download": True}
    with YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=False)
        return info.get("duration", 0), info.get("title", "Unknown Title")


def fmt_unwatched(minutes: int, seconds: int) -> str:
    parts = []
    if minutes:
        parts.append(f"{minutes} minute{'s' if minutes != 1 else ''}")
    if seconds:
        parts.append(f"{seconds} second{'s' if seconds != 1 else ''}")
    return f" ({' and '.join(parts)} unwatched)" if parts else ""


# Main routine
def main() -> None:
    playlist_url = maybe_get_playlist_url()

    print("\nFetching playlist...")
    ydl_opts = {"quiet": True, "extract_flat": True, "skip_download": True}
    with YoutubeDL(ydl_opts) as ydl:
        playlist_info = ydl.extract_info(playlist_url, download=False)

    entries = playlist_info.get("entries", [])
    if not entries:
        print("No videos found in the playlist.")
        return

    desired_minutes = get_valid_watch_time()
    start_idx, start_offset = get_valid_start_input(len(entries))

    print("\nCalculating...\n")

    target_seconds = desired_minutes * 60
    watched_seconds = 0

    final_index = start_idx - 1
    final_partial = False
    partial_watch_time = 0
    final_dur = 0
    final_title = "Unknown"

    for i in range(start_idx - 1, len(entries)):
        entry = entries[i]
        video_id = entry["url"]
        full_url = (
            f"https://www.youtube.com/watch?v={video_id}"
            if "youtube" not in video_id
            else video_id
        )

        duration = entry.get("duration")
        title = entry.get("title", "Unknown Title")
        if duration is None:                                # slow fallback
            duration, title = fetch_video_duration_and_title(full_url)

        if i == start_idx - 1 and start_offset >= duration:
            print("Timestamp exceeds video length; please try again.")
            return

        usable = duration - start_offset if i == start_idx - 1 else duration

        if watched_seconds + usable >= target_seconds:
            need = target_seconds - watched_seconds
            partial_watch_time = start_offset + need if i == start_idx - 1 else need
            final_index = i
            final_partial = True
            final_dur = duration
            final_title = title
            break
        else:
            watched_seconds += usable
            final_index = i
            final_dur = duration
            final_title = title

    # Output
    BOLD = "\033[1m"
    RESET = "\033[0m"

    print(f"\nWatch till video: {BOLD}{final_index + 1} -> {final_title}{RESET}")

    if final_partial:
        w_m, w_s = seconds_to_mm_ss(partial_watch_time)
        t_m, t_s = seconds_to_mm_ss(final_dur)
        rem = final_dur - partial_watch_time
        r_m, r_s = seconds_to_mm_ss(rem)
        print(
            f"Watch until: {BOLD}{w_m}:{w_s:02} / {t_m}:{t_s:02}{RESET}"
            f"{fmt_unwatched(r_m, r_s)}"
        )
    else:
        t_m, t_s = seconds_to_mm_ss(final_dur)
        print(f"Watch until: {BOLD}{t_m}:{t_s:02} / {t_m}:{t_s:02}{RESET}")


if __name__ == "__main__":
    main()