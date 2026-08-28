🚀 TeraBox / Diskwala Video Downloader Bot

A powerful Telegram bot for downloading videos from TeraBox and Diskwala, then delivering them directly to users through Telegram.

The bot supports multiple download engines, automatic URL detection, Telegram-side caching, Firestore persistence, flood-control queueing, cancellation, quality fallback, and admin tools.

⚠️ Disclaimer: Use this project only with content you are authorized to download and redistribute. Respect the Terms of Service, copyright laws, and the policies of the services involved.

⸻

✨ Features

🔗 Automatic URL Detection

Send a TeraBox or Diskwala URL anywhere in a supported chat.

The bot automatically detects the URL and uses the user’s selected download mode.

📥 Four Download Modes

Mode	Command	Description
Traditional	/get	Legacy chunk-based TeraBox downloader
Experimental	/exp	Fast TeraBox direct-link extractor
Experimental HD	/exphd	TeraBox extractor targeting HD
Diskwala	/dw	Diskwala direct-video downloader

⚡ Experimental Downloader

/exp and /exphd use a metadata/extractor service to resolve a direct CDN or streaming URL.

Advantages:

* Faster metadata resolution
* Direct video downloading
* Multipart/concurrent downloading
* HLS support
* FFmpeg remuxing
* HD mode
* Less dependence on traditional TeraBox chunk collection

💾 Telegram-Side Caching

Every successfully processed source can be cached in a private Telegram storage group.

First request:

User
 ↓
Resolve URL
 ↓
Download video
 ↓
Upload to storage group
 ↓
Send video to user

Repeat request:

User
 ↓
Find cache
 ↓
Forward existing Telegram message
 ↓
Done

This avoids downloading and uploading the same video repeatedly.

🗄️ Firebase Firestore

Firestore stores:

* Users
* Groups/chats
* Selected download mode
* Cached video message IDs
* Source/cache relationships

🛑 Download Cancellation

Active downloads display an inline:

❌ Cancel

button.

When pressed, the bot sets a cancellation event and the active pipeline stops at its next safe checkpoint.

🚦 Flood Control

The bot includes:

* Global flood cooldown
* Async semaphore
* Background queue
* FloodWaitError handling
* Automatic queue processing
* Delayed retry after Telegram cooldown

This helps the bot survive traffic spikes.

🎯 Quality Fallback

Traditional mode can attempt qualities in order:

1080p
 ↓
720p
 ↓
480p
 ↓
360p

If one quality fails, the next available quality is attempted.

⸻

📋 Commands

User Commands

/start

Displays the welcome message and available commands.

/start

/get

Traditional TeraBox downloader.

/get https://terabox.com/...

Best suited for smaller files. The traditional pipeline is more sensitive to TeraBox rate limits.

/exp

Fast TeraBox downloader.

/exp https://terabox.com/...

/exphd

TeraBox downloader targeting HD quality.

/exphd https://terabox.com/...

/dw

Diskwala downloader.

/dw https://diskwala.example/...

/settings

Change the default automatic download mode.

Available modes:

get
exp
exphd
dw

/random

Send a random previously cached video.

/random

/op

Send feedback to the administrator.

/op Your feedback here

⸻

👑 Admin Commands

/recent

Display recently active users/chats.

/recent

Only the configured administrator can use this command.

/broadcast

Broadcast a message to known users and groups.

/broadcast Your message here

Use responsibly. Broadcasting to a large number of chats can trigger Telegram rate limits.

⸻

🧠 Automatic Mode Routing

When a user sends a normal message, the bot first checks their configured mode.

For example:

User mode = exp

and the message contains:

https://terabox.com/...

The bot automatically runs the experimental TeraBox pipeline.

If the user sends the wrong type of URL, the bot provides a helpful hint instead of silently ignoring it.

Example:

Current mode: exp
Detected Diskwala link.
Use /dw <url>
or change your default mode to dw using /settings.

⸻

🏗️ Architecture

graph TD
    U["User / Group"] --> TR["global_tracker"]
    TR --> DB["Firestore"]
    TR --> R{"Slash command?"}
    R -->|Yes| CMD["Command handlers"]
    R -->|No| MSG["handle_message"]
    CMD --> GET["/get"]
    CMD --> EXP["/exp"]
    CMD --> EXPHD["/exphd"]
    CMD --> DW["/dw"]
    CMD --> SET["/settings"]
    CMD --> RANDOM["/random"]
    CMD --> OP["/op"]
    MSG --> MODE["get_user_mode"]
    MODE --> ROUTE["Mode-based URL routing"]
    GET --> TP["Traditional pipeline"]
    EXP --> EP["Experimental pipeline"]
    EXPHD --> EP
    DW --> DP["Diskwala pipeline"]
    TP --> CACHE["Firestore Cache"]
    EP --> CACHE
    DP --> CACHE
    CACHE -->|Hit| FORWARD["Forward cached Telegram message"]
    CACHE -->|Miss| DOWNLOAD["Download"]
    DOWNLOAD --> STORAGE["Storage Group"]
    STORAGE --> SEND["Send to user"]

⸻

📁 Project Structure

.
├── main.py
├── .env
├── .gitignore
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
├── apt.txt
├── README.md
│
├── telegram_logic/
│   ├── bot.py
│   ├── helpers.py
│   ├── progress_callbacks.py
│   ├── queue.py
│   ├── terabox_trad.py
│   ├── terabox_exp.py
│   ├── diskwala.py
│   │
│   └── commands/
│       ├── start.py
│       ├── get.py
│       ├── experimental.py
│       ├── diskwala.py
│       ├── random.py
│       ├── settings.py
│       ├── opinion.py
│       ├── cancel_download.py
│       ├── recent.py
│       └── broadcast.py
│
├── terabox/
│   ├── public_api.py
│   ├── core_pipeline.py
│   └── internal_helpers.py
│
├── teraboxDL/
│   ├── terabox_dl.py
│   ├── public_api.py
│   └── stream_downloader.py
│
├── diskwalaDL/
│   └── public_api.py
│
└── firebase_db/
    ├── db.py
    ├── users.py
    └── cache.py

⸻

⚙️ Requirements

Software

Recommended environment:

Python 3.11+
FFmpeg
Git

FFmpeg must be available through:

ffmpeg -version

The bot uses FFmpeg for operations such as remuxing HLS/TS streams into MP4.

⸻

🔥 Firebase Setup

Create a Firebase project and enable:

Firestore Database

Create a service account and obtain its credentials.

The credentials can be supplied through the FIREBASE_SECRETS environment variable.

Example:

FIREBASE_SECRETS={"type":"service_account",...}

Never commit Firebase service-account credentials to GitHub.

⸻

🤖 Telegram Setup

Create a Telegram bot using @BotFather.

You will need:

BOT_TOKEN=

You also need Telegram API credentials:

APP_ID=
API_HASH=

These can be obtained from:

https://my.telegram.org

⸻

🔐 Environment Configuration

Create a .env file in the project root.

Example:

# Telegram
BOT_TOKEN=your_telegram_bot_token
APP_ID=your_telegram_app_id
API_HASH=your_telegram_api_hash
# Telegram storage
STORAGE_GROUP_ID=-1001234567890
# Admin
ADMIN_ID=123456789
# Firebase
FIREBASE_SECRETS={"type":"service_account",...}
# TeraBox experimental extractor
THIRD_PARTY_TERABOXDL_URL=https://example.com/
PROXY_URL=http://your-proxy/v1
# Diskwala
DISKWALA_PROXY_URL=http://your-proxy/video
DISKWALA_API_KEY=your_api_key
# Traditional TeraBox mode
COOKIES1=
COOKIES2=

⸻

🔑 Environment Variables

Variable	Purpose
BOT_TOKEN	Telegram bot token
APP_ID	Telegram API ID
API_HASH	Telegram API hash
STORAGE_GROUP_ID	Private Telegram storage group
ADMIN_ID	Bot administrator ID
FIREBASE_SECRETS	Firestore service-account credentials
THIRD_PARTY_TERABOXDL_URL	Experimental TeraBox extractor
PROXY_URL	TeraBox proxy endpoint
DISKWALA_PROXY_URL	Diskwala resolver
DISKWALA_API_KEY	Diskwala API authentication
COOKIES1..N	Traditional TeraBox session cookies

⸻

🗃️ Storage Group

Create a private Telegram supergroup for video caching.

Set:

STORAGE_GROUP_ID=-1001234567890

The bot must have sufficient permissions to send messages/files to this group.

The group acts as the bot’s persistent Telegram-side video storage.

⸻

📦 Installation

Clone the repository:

git clone https://github.com/YOUR_USERNAME/YOUR_REPOSITORY.git
cd YOUR_REPOSITORY

Create a virtual environment:

python -m venv venv

Activate it on Linux/macOS:

source venv/bin/activate

Windows:

venv\Scripts\activate

Install Python dependencies:

pip install -r requirements.txt

Make sure FFmpeg is installed:

ffmpeg -version

Configure .env:

nano .env

Then start the bot:

python main.py

⸻

🐳 Docker

Build the image:

docker build -t terabox-diskwala-bot .

Run:

docker run -d \
  --name terabox-bot \
  --restart unless-stopped \
  --env-file .env \
  terabox-diskwala-bot

Check logs:

docker logs -f terabox-bot

⸻

🐳 Docker Compose

Example:

services:
  bot:
    build: .
    container_name: terabox-diskwala-bot
    restart: unless-stopped
    env_file:
      - .env

Start:

docker compose up -d --build

View logs:

docker compose logs -f

Stop:

docker compose down

⸻

🧩 Download Pipeline

The experimental TeraBox and Diskwala pipelines follow a common high-level workflow.

flowchart TD
    START["Incoming URL"] --> FLOOD{"Flood cooldown?"}
    FLOOD -->|Yes| QUEUE["Add to flood queue"]
    FLOOD -->|No| SEM["Acquire semaphore"]
    SEM --> CANCEL["Create cancellation event"]
    CANCEL --> CACHE{"Cache hit?"}
    CACHE -->|Yes| FORWARD["Forward cached Telegram message"]
    CACHE -->|No| META["Resolve metadata"]
    META --> DOWNLOAD["Download video"]
    DOWNLOAD --> PRE["Prepare upload"]
    PRE --> STORAGE{"Storage enabled?"}
    STORAGE -->|Yes| UPLOAD["Upload to storage"]
    UPLOAD --> CACHEADD["Add message ID to Firestore"]
    STORAGE -->|No| SEND["Send directly"]
    CACHEADD --> SEND
    SEND --> CLEAN["Cleanup temporary files"]
    CLEAN --> END["Finished"]
    CANCEL -.->|Cancel| ABORT["Abort pipeline"]

⸻

⚡ Upload Optimization

The upload pipeline avoids unnecessarily reading the same file twice.

Before

send_file(filepath)
      ↓
Read file from disk
      ↓
Upload
      ↓
Fallback
      ↓
send_file(filepath)
      ↓
Read disk again
      ↓
Upload again

After

_pre_upload_file(filepath)
      ↓
Read file once
      ↓
Prepare InputFile
      ↓
Upload to storage
      ↓
Reuse prepared handle
      ↓
Send to user

This reduces unnecessary disk I/O and avoids repeating expensive preparation work.

⸻

🚦 Flood Control

The bot uses a global cooldown and background queue to handle Telegram FloodWaitError.

Example scenario:

50 users
   ↓
20 active jobs
   ↓
Semaphore limit
   ↓
Telegram FloodWaitError
   ↓
Global cooldown
   ↓
New requests → Queue
   ↓
Cooldown expires
   ↓
Queue worker resumes jobs

During a flood cooldown, new requests are queued rather than immediately starting another Telegram-heavy operation.

The queue worker gradually resumes processing after the cooldown.

⸻

🔒 Concurrency Control

The downloader uses a semaphore to limit concurrent processing.

Example:

asyncio.Semaphore(20)

This means at most 20 pipelines can enter the protected processing section simultaneously.

The exact limit should be adjusted according to:

* VPS CPU
* RAM
* Network bandwidth
* Telegram limits
* Downloader/proxy capacity

⸻

🛑 Cancellation

Each active download receives its own cancellation event.

Conceptually:

User
 ↓
Download starts
 ↓
active_tasks[user/task] = cancel_event
 ↓
User presses ❌ Cancel
 ↓
cancel_event.set()
 ↓
Downloader checks event
 ↓
Stops at next checkpoint
 ↓
Temporary files cleaned

Cancellation is cooperative rather than an unsafe hard process kill.

⸻

🌐 Supported TeraBox Domains

Experimental URL matching supports domains such as:

terabox.com
1024terabox.com
teraboxapp.com
freeterabox.com
terabox.app
terabox.fun
4funbox.co
4funbox.com
mirrobox.com
nephobox.com
1024tera.com
momerybox.com
tibibox.com

Optional:

www.

The matcher supports multiple URL layouts, including:

https://domain/.../<SURL>

and:

https://domain/<SURL>

⸻

📡 Traditional TeraBox Pipeline

The legacy /get pipeline uses a chunk-based approach.

A typical flow is:

Share URL
   ↓
Share page
   ↓
Metadata
   ↓
Streaming endpoint
   ↓
Discover TS chunks
   ↓
Download chunks
   ↓
Assemble
   ↓
FFmpeg/remux
   ↓
Telegram

Each discovered chunk is tracked by its index.

Example:

_0_ts
_1_ts
_2_ts
_3_ts
...

⸻

⚠️ Traditional Chunk Collection

The traditional pipeline uses a bounded request strategy rather than polling indefinitely.

Conceptually:

Discover chunks
      ↓
Track indexes
      ↓
Check for gaps
      ↓
Check completion
      ↓
Stop when complete
      ↓
OR
Request budget reached

This reduces excessive requests to the upstream service.

Long videos can still experience missing segments depending on the upstream service’s behavior.

⸻

🎞️ HLS / FFmpeg

When an HLS stream is returned, the downloader can use FFmpeg to process the stream and remux it into a suitable video container.

Example conceptual pipeline:

M3U8
 ↓
TS segments
 ↓
FFmpeg
 ↓
MP4

FFmpeg must therefore be installed and accessible through PATH.

⸻

💾 Cache Architecture

Firestore maintains separate cache buckets for each mode:

get
exp
exphd
dw

Conceptually:

cache/
 ├── get/
 ├── exp/
 ├── exphd/
 └── dw/

A source URL is associated with a Telegram storage-group message ID.

On a cache hit:

Source URL
   ↓
Firestore lookup
   ↓
Message ID found
   ↓
Telegram forward

No external download is required.

⸻

👤 User Database

The user database can track:

user_id
chat_id
username
first_seen
last_seen
download_mode

The global tracker runs before command/message routing.

Incoming update
      ↓
global_tracker
      ↓
track user/chat
      ↓
command or normal message

⸻

🔄 Automatic Mode Example

Suppose the user selects:

/settings

and chooses:

exp

Then they can simply send:

https://terabox.com/...

The bot automatically behaves approximately as:

Message
 ↓
get_user_mode()
 ↓
exp
 ↓
TeraBox URL matcher
 ↓
process_terabox_experimental()
 ↓
Cache lookup
 ↓
Download / Forward

⸻

❗ Cross-Type URL Hints

The bot does not silently ignore unsupported links.

Example:

Current mode: dw
User sends TeraBox URL

The bot can respond with:

⚠️ This is a TeraBox link.
Use /exp, /exphd or /get
or change your default mode in /settings.

Likewise:

Current mode: exp
User sends Diskwala URL

The bot can suggest:

⚠️ This is a Diskwala link.
Use /dw
or change your default mode to dw.

⸻

📊 Request Flow

sequenceDiagram
    participant U as User
    participant B as Bot
    participant DB as Firestore
    participant EX as Extractor
    participant TG as Telegram Storage
    U->>B: Send URL
    B->>DB: Track user
    B->>DB: Check selected mode
    B->>DB: Search cache
    alt Cache hit
        DB-->>B: Storage message ID
        B->>TG: Forward cached message
        TG-->>U: Video
    else Cache miss
        B->>EX: Resolve metadata
        EX-->>B: Direct/stream URL
        B->>EX: Download
        EX-->>B: Video file
        B->>TG: Upload to storage
        TG-->>B: Message ID
        B->>DB: Save cache
        B->>U: Send video
    end

⸻

⚠️ Limitations

Telegram File Limits

Telegram’s Bot API has file-size restrictions.

For large videos, delivery can fail depending on the API/server configuration being used.

Always verify the limits applicable to your deployment before relying on large-file uploads.

Rate Limits

TeraBox and Telegram can apply rate limits.

The bot therefore uses:

Semaphore
+
FloodWait handling
+
Queue
+
Request budgets

However, no implementation can guarantee that upstream services will never rate-limit or block requests.

Proxy Dependency

Experimental and Diskwala modes depend on external resolver/proxy infrastructure.

If the resolver changes or becomes unavailable:

URL
 ↓
Resolver
 X

the downloader may stop working until the resolver integration is updated.

Temporary Disk Usage

Downloads are normally written to temporary storage before Telegram delivery.

Make sure your VPS has enough:

Disk space
RAM
Bandwidth

for the largest expected downloads.

⸻

🔐 Security

Never Commit .env

Add this to .gitignore:

.env
*.json
cookies.txt
__pycache__/
*.pyc
downloads/
temp/
*.log

Protect Secrets

Never publish:

BOT_TOKEN
API_HASH
FIREBASE_SECRETS
DISKWALA_API_KEY
COOKIES1
COOKIES2
PROXY credentials

If a secret is accidentally uploaded to GitHub, revoke/rotate it immediately.

⸻

🧪 Testing Checklist

Before deploying, test:

[ ] /start
[ ] /settings
[ ] /get
[ ] /exp
[ ] /exphd
[ ] /dw
[ ] /random
[ ] /op
[ ] /recent
[ ] /broadcast
[ ] Automatic URL detection
[ ] TeraBox URL detection
[ ] Diskwala URL detection
[ ] Wrong-mode hint
[ ] Cache hit
[ ] Cache miss
[ ] Cancel button
[ ] FloodWait handling
[ ] Queue recovery
[ ] FFmpeg
[ ] Firebase connection
[ ] Storage group upload
[ ] Large-file handling
[ ] Temporary-file cleanup

⸻

🛠️ Troubleshooting

Bot does not start

Check:

python --version

Then:

pip install -r requirements.txt

Check environment variables:

BOT_TOKEN
APP_ID
API_HASH
FIREBASE_SECRETS

⸻

FFmpeg not found

Run:

ffmpeg -version

If unavailable, install FFmpeg through your operating system/package manager.

⸻

Cache not working

Verify:

FIREBASE_SECRETS
STORAGE_GROUP_ID

Also make sure the bot has permission to send messages/files to the storage group.

⸻

Videos are not downloading

Check:

Extractor/proxy availability
Network connection
FFmpeg
Temporary disk space
Environment variables
Upstream URL changes

⸻

Telegram FloodWait

Do not continuously restart the bot to bypass a Telegram cooldown.

Allow the queue/cooldown mechanism to handle the wait.

Also consider reducing:

Concurrent downloads
Progress-message frequency
Unnecessary Telegram API calls

⸻

📈 Performance Recommendations

For a VPS deployment:

CPU:        2+ cores
RAM:        2–4 GB+
Storage:    SSD recommended
Network:    Stable high-speed connection
FFmpeg:     Installed

Actual requirements depend heavily on concurrent downloads and video sizes.

For high traffic, consider:

Lower progress update frequency
↓
Tune semaphore
↓
Use efficient temporary storage
↓
Keep Telegram cache enabled
↓
Avoid duplicate downloads

⸻

🧹 Temporary File Cleanup

Every successful or failed pipeline should clean temporary files.

Conceptually:

try:
    download()
    process()
    upload()
finally:
    cleanup()

This prevents a VPS from eventually filling its disk with old videos.

⸻

📌 Recommended Deployment Flow

1. Create Telegram bot
        ↓
2. Create Telegram storage group
        ↓
3. Create Firebase project
        ↓
4. Configure Firestore
        ↓
5. Configure .env
        ↓
6. Install FFmpeg
        ↓
7. Install Python dependencies
        ↓
8. Run locally
        ↓
9. Test commands
        ↓
10. Deploy with Docker
        ↓
11. Monitor logs

⸻

🔄 Updating the Bot

When updating the source:

git pull

Then:

pip install -r requirements.txt

For Docker:

docker compose down
docker compose up -d --build

Check:

docker compose logs -f

⸻

📜 License

Choose and add an appropriate license before publishing this repository.

For example:

MIT License

If this project contains third-party code, APIs, extractors, or dependencies with different licenses, review their licenses before redistributing the project.

⸻

⚠️ Responsible Use

This project is intended for legitimate use cases such as:

* Downloading content you own
* Downloading content you have permission to access
* Personal backups where legally permitted
* Testing your own infrastructure
* Educational development

Do not use the bot to facilitate copyright infringement, unauthorized redistribution, credential theft, abuse of third-party services, or circumvention of access controls.

⸻

⭐ Credits

Built with:

* Python
* Telethon
* Firebase Firestore
* FFmpeg
* AsyncIO
* External metadata/resolver services

⸻

🤝 Contributing

Pull requests are welcome.

Before submitting a PR:

1. Test your changes
2. Keep secrets out of Git
3. Update README when behavior changes
4. Add error handling
5. Avoid unnecessary Telegram API requests

⸻

📞 Support

If you encounter an issue, include:

Python version
OS/VPS information
Command used
Relevant logs
Mode used
Whether cache was hit/missed

Never include:

BOT_TOKEN
API_HASH
Firebase credentials
API keys
Cookies
Private proxy credentials

⸻

🚀 Quick Start

The shortest setup path:

git clone https://github.com/YOUR_USERNAME/YOUR_REPOSITORY.git
cd YOUR_REPOSITORY
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
# Configure .env
python main.py

Then open your Telegram bot and send:

/start

Choose a mode with:

/settings

and send a supported link.

⸻

TeraBox / Diskwala Video Downloader — multi-mode downloading, Telegram caching, Firestore persistence and flood-aware processing in one bot.
