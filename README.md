# YouTube Playlist Watch Calculator

This program helps you plan your YouTube learning or entertainment sessions more efficiently.  
Given a YouTube playlist, a starting video (with optional timestamp), and your desired watch duration in minutes, it tells you **exactly** which video and what timestamp to stop at—no more guesswork!

---

## ✨ Features

- **Flexible playlist selection**:  
  Choose from your pre-saved playlists (defined in `playlists.json`) or enter a new YouTube playlist URL.
- **Smart duration calculation**:  
  Specify where you want to start (video number + optional mm:ss timestamp) and how many minutes you wish to watch; the program tells you precisely where to stop.
- **Efficient & Fast**:  
  Loads all video durations in a single batch for speed (only queries YouTube individually if needed).
- **Persistent playlist management**:  
  Manually manage your playlists in a simple JSON file for future use.
- **Intuitive output**:  
  The program displays clear, easy-to-follow instructions with formatted output and handles all common input errors.

---

## 🚀 Getting Started

### 1. Requirements

- Python 3.8+
- [`yt-dlp`](https://github.com/yt-dlp/yt-dlp) (`pip install yt-dlp`)

### 2. Installation

Clone the repository and install dependencies:

```bash
git clone https://github.com/yourusername/playlist-watch-calculator.git
cd playlist-watch-calculator
pip install yt-dlp
````

### 3. Setting Up Playlists

To quickly choose playlists in the app, create a `playlists.json` file in the same directory.
Example format:

```json
{
  "Physics Lectures": "https://www.youtube.com/playlist?list=PLKyB9RYzaFQphysics",
  "Lo-fi Study Mix": "https://www.youtube.com/playlist?list=PLKyB9RYzaFQlofi"
}
```

* Playlist names must be **unique**.
* The file must be valid JSON (double quotes, commas).
* Edit this file with any text editor to add, remove, or rename playlists.

### 4. Usage

Run the program:

```bash
python main.py
```

**Walkthrough:**

1. **Choose a playlist**:
   If you have playlists saved, select from the list. If not, paste any YouTube playlist URL.
2. **Choose starting point**:
   Enter the starting video number (e.g., `4`), or `4 2:30` to start at 2 minutes 30 seconds into video 4.
3. **Set watch duration**:
   Enter how many minutes you want to watch.
4. **Result**:
   The program tells you which video (and timestamp) to stop at to fit your watch session.

---

## ⚙️ Configuration

Open `main.py` and look for:

```python
PROMPT_BEFORE_SAVED_PLAYLIST = True
```

* If set to `True`:
  You will be asked whether to choose a saved playlist or enter a new one.
* If set to `False`:
  The program will always present the list of saved playlists (if any) without asking.

---

## 📝 Example Session

```
Available saved playlists:
1 - Physics Lectures
2 - Lo-fi Study Mix
Select playlist: 1

Fetching playlist...

Enter the starting video number (max -> 43) [optional timestamp mm:ss]: 5 3:00

Enter the number of minutes you want to watch: 25

Calculating...

Watch till video: 8 -> What is Quantum Entanglement?
Watch until: 12:40 / 20:19 (7 minutes and 39 seconds unwatched)
```

---

## 🛠 Troubleshooting

* **Durations are missing/wrong:**
  Some rare playlists may hide durations. The program will still fetch them, but may be slower.
* **Program is slow:**
  This is usually due to YouTube throttling or playlists with many missing durations. Most users should see results in just a few seconds.

---

## 🤝 Contributing

Pull requests and improvements are welcome!
