# EnvComparer

### Crafted with ❤️ by codesaksham for developers.

EnvComparer is a sleek, premium developer utility designed to quickly align, compare, and debug environment variable files side-by-side. It is built strictly in **Python FastAPI** and features a beautiful **glassmorphic dark-mode user interface** styled with pure vanilla CSS and responsive client-side filters.

---

## ✨ Features

- **Side-by-Side Key Alignment**: Handles differences in key sequences seamlessly. The parsing engine extracts all unique keys, sorts them alphabetically, and aligns matching rows.
- **Robust Value Extraction**: Parses standard `.env` formats, supports both `=` and `:` delimiters, handles single/double quotes, and strips trailing inline comments (`#`) safely.
- **Harmonious Status Highlighting**:
  - 🟢 **Matches**: Variables present in both lists with identical values.
  - 🔴 **Mismatches**: Present in both but with conflicting values (highlighted with dashed borders and red ambient glow).
  - 🟡 **Missing Right**: Variables defined only in List A.
  - 🟣 **Missing Left**: Variables defined only in List B.
- **Instant Search**: Search through keys or value strings with high-performance real-time DOM updates.
- **Snappy Client-Side Filters**: Filter rows instantly by status (All, Mismatches, Missing Left, Missing Right, Matches) without page refreshes.
- **One-Click Clipboard Copy**: Clicking any value card (or its copy icon) copies the string directly to the clipboard, flashing the card with a soft emerald glow and raising a sleek slide-up toast notification.

---

## 🛠️ Project Structure

```
env-comparer/
├── app/
│   ├── main.py          # FastAPI application, web routing, and Jinja2 initialization
│   ├── parser.py        # Environment variable extraction & comparison algorithms
│   └── templates/
│       └── index.html   # Glassmorphic UI template, CSS styling, and client-side JS
├── requirements.txt     # Minimal Python framework requirements
├── Dockerfile           # Multi-stage lightweight Python container setup
├── docker-compose.yml   # Containerized service definition (exposes port 8090)
├── run.sh               # Standalone shell script for automated local execution
└── README.md            # This documentation
```

---

## ⚡ Getting Started

You can run EnvComparer in two ways:

### 1. Standalone Local Server (Native Python)
Simply run the shell launcher script. It automatically manages virtual environment creation, pip package installations, and starts the server with hot-reload enabled:
```bash
chmod +x run.sh
./run.sh
```
*The app will start instantly on **`http://localhost:8090`**.*

### 2. Containerized (Docker Compose)
Run the application using Docker Compose to isolate it as a microservice:
```bash
docker compose up -d --build
```
*The container will build and expose the tool on port **`8090`**.*

---

## 💎 Design Highlights

- **Palette**: Tailored HSL color models optimized for dark modes (`hsl(220, 95%, 60%)` to `hsl(180, 100%, 45%)`).
- **Typography**: Responsive typographic hierarchy using Google Fonts (`Outfit` for system text and `Fira Code` for monospaced environment keys/values).
- **Glassmorphism**: Backdrop blur effects (`backdrop-filter: blur(16px)`) combined with thin borders and glowing radial shadows to provide a modern developer aesthetic.
