# Pro Secure Suite - Secure File Transfer Application

This project is a comprehensive client-server suite for secure file sharing over a network, developed using Python. It features a full graphical user interface built with `tkinter` and ensures all communications are encrypted using SSL/TLS. The suite includes advanced features for server management, client interaction, and multi-platform access.

---

## How It Works (Technical Overview)

This application is built on a robust client-server architecture with several key technologies working in tandem to provide a secure and interactive experience.

* **Networking (TCP/IP Sockets):** The foundation of the application is Python's `socket` module. It uses the TCP protocol to establish reliable, connection-oriented communication between the server and clients. The server opens multiple ports to handle different services simultaneously:
    * **Main Port:** For file transfer commands and data.
    * **Chat Port:** A dedicated port for real-time, two-way text communication.
    * **Web Port:** For providing access to files via a web browser.

* **Security (SSL/TLS Encryption):** All communication channels (file, chat, and web) are secured using Python's `ssl` module. The server automatically generates a self-signed SSL certificate (`server.key`, `server.crt`) upon first run. Every socket connection is then wrapped in a TLS (Transport Layer Security) context, encrypting all data in transit. This protects against eavesdropping and ensures data integrity.

* **Graphical User Interface (GUI):** The user-friendly interface for both the server and client is built using Python's standard GUI toolkit, **`tkinter`**. The modern look and feel are achieved using the `ttk.Style` functionality with a custom dark theme.

* **Concurrency (Multithreading):** The server is designed to handle multiple clients at once without freezing the main application window. This is achieved using the **`threading`** module. For each incoming connection (whether for file transfer, chat, or a web request), the server spawns a new thread to handle that client's requests independently.

* **Custom Communication Protocol:** A simple, text-based protocol was designed to manage interactions. Commands are sent as plain strings, often with prefixes, to distinguish different actions.
    * **Examples:** `LIST_FILES` (requests the file list), `DOWNLOAD_FILES` (initiates a file download), `MSG_C2S:` (a chat message from a Client to the Server), `MSG_S2C:` (a chat message from the Server to a Client).

* **Web Access (HTTPS Server):** To allow users to download files without the dedicated client app, a simple, secure web server is integrated using Python's `http.server` module. It is wrapped with the same SSL context to serve files over **HTTPS**, making it accessible and secure from any modern web browser, including on mobile devices.

---

## دفترچه راهنما (User Manual)

<div dir="rtl">
این دفترچه راهنما شما را قدم به قدم برای نصب، اجرا و استفاده از تمام قابلیت‌های برنامه راهنمایی می‌کند.
</div>

### ۱. پیش‌نیازها (نصب پایتون و کتابخانه‌ها)

<div dir="rtl">
برای اجرای این برنامه، ابتدا باید پایتون و سپس چند کتابخانه جانبی را روی سیستم خود نصب کنید.
</div>

#### نصب پایتون

<div dir="rtl">
اگر پایتون روی سیستم شما نصب نیست، آن را از وب‌سایت رسمی دانلود و نصب کنید:
</div>

* **آدرس دانلود:** [**https://www.python.org/downloads/**](https://www.python.org/downloads/)

    > **نکته بسیار مهم برای کاربران جدید:** در هنگام نصب پایتون، حتماً تیک گزینه‌ **Add Python to PATH** را در اولین صفحه نصب فعال کنید. این کار اجرای دستورات بعدی را بسیار ساده‌تر می‌کند.

#### نصب کتابخانه‌های مورد نیاز

<div dir="rtl">
پس از نصب پایتون، پنجره Command Prompt یا CMD را باز کرده و دستور زیر را برای نصب تمام کتابخانه‌های لازم کپی و اجرا کنید:
</div>

```bash
pip install pyopenssl pandas openpyxl
```

### ۲. نحوه اجرای برنامه

<div dir="rtl">
<ol>
<li>هر سه فایل <code>launcher.py</code>، <code>server.py</code> و <code>client.py</code> را در یک پوشه در کنار هم قرار دهید.</li>
<li>برنامه را <strong>فقط</strong> از طریق فایل <code>launcher.py</code> اجرا کنید:</li>
</ol>
</div>

```bash
python launcher.py
```

<div dir="rtl">
<ol start="3">
<li>از پنجره باز شده، برنامه مورد نظر (Server یا Client) را برای اجرا انتخاب کنید.</li>
</ol>
</div>

### ۳. راهنمای سرور (Server Guide)

<div dir="rtl">
پس از اجرای سرور، با بخش‌های زیر روبرو می‌شوید:
</div>

<div dir="rtl">
<ol>
<li>
<strong>انتخاب محتوا (Share Configuration):</strong>
<ul>
<li>ابتدا مشخص کنید که می‌خواهید یک پوشه کامل (Share Directory) یا یک فایل تکی (Share Single File) را به اشتراک بگذارید.</li>
<li>روی دکمه <code>Browse...</code> کلیک کرده و فایل یا پوشه مورد نظر را از روی سیستم خود انتخاب کنید.</li>
</ul>
</li>
<li>
<strong>تنظیمات سرور (Server Settings):</strong>
<ul>
<li><strong>Port:</strong> یک شماره پورت برای اتصال کلاینت‌ها وارد کنید (مقدار پیش‌فرض <code>5000</code> مناسب است).</li>
<li><strong>Max Clients:</strong> حداکثر تعداد کاربرانی که می‌توانند همزمان متصل شوند را مشخص کنید.</li>
<li><strong>Require Password:</strong> اگر می‌خواهید برای سرور رمز عبور بگذارید، این تیک را فعال کرده، رمز خود را وارد کنید و روی <code>Confirm Password</code> کلیک کنید.</li>
</ul>
</li>
<li>
<strong>شروع به کار سرور (Control Panel):</strong>
<ul>
<li>پس از انجام تنظیمات، روی دکمه بزرگ <strong>▶️ Start</strong> کلیک کنید.</li>
<li>وضعیت سرور به "Running" تغییر می‌کند و IP آدرس‌های لازم برای اتصال کلاینت‌ها نمایش داده می‌شود:
<ul>
<li><strong>Server IP:</strong> برای اتصال کلاینت دسکتاپ.</li>
<li><strong>Web Access:</strong> برای اتصال با مرورگر وب (موبایل و کامپیوتر).</li>
</ul>
</li>
</ul>
</li>
<li>
<strong>مدیریت کلاینت‌ها (Client Management Tab):</strong>
<ul>
<li>در این تب، لیست تمام کلاینت‌های متصل، وضعیت آن‌ها (در حال دانلود، بیکار و...) و پیشرفت دانلودشان را به صورت زنده مشاهده می‌کنید.</li>
<li>با انتخاب یک کلاینت از لیست، می‌توانید با کلیک روی <strong>Disconnect Selected</strong> او را از سرور اخراج کرده یا با کلیک روی <strong>Send Warning</strong> برای او پیام اخطار ارسال کنید.</li>
</ul>
</li>
<li>
<strong>چت با کلاینت‌ها (Chats Tab):</strong>
<ul>
<li>در این تب، لیست تمام کلاینت‌هایی که قابلیت چت با آن‌ها وجود دارد نمایش داده می‌شود.</li>
<li>یک کلاینت را از لیست انتخاب کرده و روی <strong>Open Chat Window</strong> کلیک کنید تا پنجره چت خصوصی با او باز شود.</li>
<li>اگر پیام جدیدی از کلاینتی دریافت کنید که پنجره چت او باز نیست، یک نقطه قرمز (🔴) روی عنوان تب Chats ظاهر می‌شود.</li>
</ul>
</li>
</ol>
</div>

### ۴. راهنمای کلاینت (Client Guide)

<div dir="rtl">
پس از اجرای کلاینت، مراحل زیر را برای اتصال و دانلود دنبال کنید:
</div>

<div dir="rtl">
<ol>
<li>
<strong>ورود اطلاعات سرور:</strong>
<ul>
<li>در کادر <code>Server IP</code>، آدرس IP که در برنامه سرور نمایش داده شده را وارد کنید. با تایپ اعداد، برنامه به صورت خودکار برای خوانایی بهتر نقطه (<code>.</code>) اضافه می‌کند.</li>
<li>در کادر <code>Port</code>، همان پورتی که در سرور تنظیم کرده‌اید را وارد کنید.</li>
</ul>
</li>
<li>
<strong>اتصال به سرور:</strong>
<ul>
<li>روی دکمه <strong>🔗 Connect</strong> کلیک کنید.</li>
<li>اگر سرور نیاز به رمز عبور داشته باشد، کادر <code>Password</code> فعال می‌شود. رمز را وارد کرده و روی <strong>🔑 Login</strong> کلیک کنید.</li>
</ul>
</li>
<li>
<strong>انتخاب و دانلود فایل‌ها:</strong>
<ul>
<li>پس از اتصال موفق، لیست فایل‌های اشتراک‌گذاری شده نمایش داده می‌شود.</li>
<li>فایل‌های مورد نظر خود را با زدن تیک کنار آن‌ها انتخاب کنید. می‌توانید از تیک <code>Select All</code> برای انتخاب همه فایل‌ها استفاده کنید.</li>
<li><strong>مسیر ذخیره:</strong> روی آیکون پوشه (📁) کلیک کرده و پوشه‌ای را روی سیستم خود به عنوان مقصد اصلی دانلودها انتخاب کنید.</li>
<li><strong>(اختیاری) ذخیره در پوشه جدید:</strong> اگر تیک <code>Download into a new sub-folder</code> را بزنید، می‌توانید یک نام برای پوشه جدید وارد کرده و روی <code>Create</code> کلیک کنید. در این صورت، فایل‌ها در این زیرپوشه ذخیره خواهند شد.</li>
<li>در نهایت، روی دکمه <strong>⬇️ Download Selected</strong> کلیک کنید تا دانلود شروع شود.</li>
<li>اگر دانلود با خطا مواجه شود، همین دکمه به <strong>🔄 Retry Download</strong> تغییر می‌کند تا بتوانید دوباره تلاش کنید.</li>
</ul>
</li>
<li>
<strong>چت با سرور:</strong>
<ul>
<li>پس از اتصال، دکمه <strong>💬 Chat with Server</strong> فعال می‌شود. با کلیک روی آن، پنجره چت با مدیر سرور باز می‌شود.</li>
<li>اگر پیام جدیدی از سرور دریافت کنید، یک نقطه قرمز (🔴) روی این دکمه ظاهر خواهد شد.</li>
</ul>
</li>
</ol>
</div>

---

## Development Process

This section outlines the technical journey and step-by-step process undertaken to build this application from the ground up.

### Phase 1: Core Foundation
The initial phase focused on establishing the fundamental infrastructure for a secure client-server file transfer system.
* **Core Technologies:** Python, `tkinter` for the GUI, and `socket` + `ssl` for secure, encrypted communication.
* **Initial Designs:** Basic GUIs for both server and client were created, handling core logic like selecting content, setting connection parameters, listing files, and downloading.

### Phase 2: UX and Structural Improvements
With the core functionality in place, the focus shifted to improving the project's structure and user experience.
* **Launcher Implementation:** A central `launcher.py` was created to provide a single entry point for both applications.
* **Enhanced Navigation:** "Back to Launcher" buttons were added for a more fluid workflow.
* **Connection Stability:** Initial connection bugs were resolved by optimizing the server's threading and socket initialization sequence.

### Phase 3: Advanced Server-Side Features
This phase involved adding powerful monitoring and administrative capabilities to the server.
* **Structured Logging:** The log system was upgraded to a `Treeview` table with categorized events.
* **Log Exporting:** An "Export Logs" feature was added, utilizing the `pandas` library to save logs as `.xlsx` or `.txt` files.
* **Integrated Web Server:** A secure HTTPS server was integrated to allow file access from any web browser, especially on mobile devices.

### Phase 4: Interactive Communication & Final Polish
The final phase focused on implementing real-time communication and performing last-mile optimizations.
* **Two-Way Chat System:** A dual-socket architecture was implemented to enable live chat without interrupting file transfers. This included a dedicated "Chats" tab on the server with `Toplevel` windows for each client conversation.
* **Notifications:** A "red dot" (🔴) notification system was added for new, unread chat messages.
* **Client UX Enhancements:** The IP entry field was improved with a monospaced font and an auto-dot insertion feature. Critical bugs related to button states and UI updates were resolved.
* **Code Optimization:** The entire codebase was refactored to improve readability, remove redundancy, and enhance stability, all without altering the core algorithms.

---

## Credits

Created By -Nima Ghaffari
[![portfolio](https://img.shields.io/badge/Telegram-2CA5E0?style=for-the-badge&logo=telegram&logoColor=white)](https://t.me/nimaghaffari001)

---