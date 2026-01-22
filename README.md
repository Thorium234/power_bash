Here’s a professional **README.md** you can drop into your repository (`power_bash`) that explains how to **clone, set up, and run your Tkinter file finder project**.

You can copy-paste this into `README.md` at the root of your repo.

---

````markdown
# Smart File Finder Pro

A powerful, multi-tab, GUI-based file search tool built with Python and Tkinter — designed for Linux workflows.  
Supports multi-search tabs, favorites, threaded search with cancellation, file previews, caching, and more.

🔗 **Repository:** https://github.com/Thorium234/power_bash

---

## ⚙️ Features

✔ Multi-tab search (unlimited)  
✔ Search by extension or filename  
✔ Threaded search (no UI freezing)  
✔ Search result caching  
✔ Favorites (auto-saved, restored on startup)  
✔ Open files/folders using default apps (`xdg-open`)  
✔ Preview supported file types (e.g., `.drawio`)  
✔ Dark theme UI  
✔ Safe, responsive GUI

---

## 📦 Requirements

### System Dependencies (Ubuntu / Debian)
Install Tkinter & preview tools:

```bash
sudo apt update
sudo apt install -y \
    python3-tk \
    xdg-utils \
    drawio
````

> `drawio` is optional – only needed for previewing `.drawio` files.

---

## 🧠 Python Dependencies

This project uses a virtual environment. Dependencies are listed in `requirements.txt`.

```bash
pip install -r requirements.txt
```

---

## 🛠️ Clone & Setup

Open a terminal and run:

```bash
git clone https://github.com/Thorium234/power_bash.git
cd power_bash/file_finder_gui
```

### Create & Activate Virtual Environment

```bash
python3 -m venv env
source env/bin/activate
```

Install dependencies:

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

---

## ▶️ Run the Application

With the virtual environment activated:

```bash
python app.py
```

The GUI should launch immediately.

---

## 📁 How To Use

1. Choose **By Extension** or **By Name**
2. Enter a query (e.g., `drawio`, `txt`, `report`)
3. Click **🔍 Search**
4. Results show in the active tab
5. Actions:

   * **📂 Open File** — open selected file
   * **📁 Open Folder** — show containing folder
   * **⭐ Favorite** — mark current tab as favorite
   * **➕ New Tab** — open a fresh search tab
6. Favorite tabs are saved and restored on next launch

---

## 📌 Notes

* Searches are cached for faster repeated results.
* You can cancel a running search with the **Cancel Search** button.
* The app stores favorite tabs in `~/.file_finder_tabs.json`.
* The cache is stored in `~/.file_finder_cache.pkl`.

---

## 🐳 (Optional) Docker Support

**Make sure Docker daemon is running:**

```bash
sudo systemctl start docker
```

**Build the image:**

```bash
docker build -t file_finder_gui .
```

**Run the container (X11 GUI):**

```bash
xhost +local:docker
docker run -it --rm \
  -e DISPLAY=$DISPLAY \
  -v /tmp/.X11-unix:/tmp/.X11-unix \
  -v $HOME:/home/user \
  file_finder_gui
```

⚠ On Wayland you may need an X11 compatibility layer (e.g., XWayland).

---

## 🧩 Troubleshooting

* **UI doesn’t launch?** Confirm Tkinter is installed:

  ```bash
  python -c "import tkinter"
  ```

  If no errors, it’s installed.

* **drawio preview not working?**
  Ensure `drawio` CLI is installed and in PATH.

* **Docker cannot connect?**
  Make sure Docker Engine or Docker Desktop is running.

---

## 📜 License

This project is open source — feel free to improve, extend, or fork!

---

## 🚀 Next Enhancements (Ideas)

* Keyboard shortcuts (Ctrl+T, Ctrl+Enter, etc.)
* Search scope presets (Home / Projects)
* Ripgrep backend support
* Dark/Light theme toggle

---



