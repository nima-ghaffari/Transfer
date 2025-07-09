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

## User Manual (Step-by-Step Guide)

این دفترچه راهنما شما را قدم به قدم برای نصب، اجرا و استفاده از تمام قابلیت‌های برنامه راهنمایی می‌کند.

### ۱. پیش‌نیازها (نصب پایتون و کتابخانه‌ها)

برای اجرای این برنامه، ابتدا باید پایتون و سپس چند کتابخانه جانبی را روی سیستم خود نصب کنید.

#### نصب پایتون

اگر پایتون روی سیستم شما نصب نیست، آن را از وب‌سایت رسمی دانلود و نصب کنید:

* **آدرس دانلود:** [**https://www.python.org/downloads/**](https://www.python.org/downloads/)

    > **نکته بسیار مهم برای کاربران جدید:** در هنگام نصب پایتون، حتماً تیک گزینه‌ی **"Add Python to PATH"** را در اولین صفحه نصب فعال کنید. این کار اجرای دستورات بعدی را بسیار ساده‌تر می‌کند.

#### نصب کتابخانه‌های مورد نیاز

پس از نصب پایتون، پنجره Command Prompt (CMD) یا PowerShell را باز کرده و دستور زیر را برای نصب تمام کتابخانه‌های لازم کپی و اجرا کنید:

```bash
pip install pyopenssl pandas openpyxl
```

### ۲. نحوه اجرای برنامه

1.  هر سه فایل `launcher.py`، `server.py` و `client.py` را در یک پوشه در کنار هم قرار دهید.
2.  برنامه را **فقط** از طریق فایل `launcher.py` اجرا کنید:
    ```bash
    python launcher.py
    ```
3.  از پنجره باز شده، برنامه مورد نظر (Server یا Client) را برای اجرا انتخاب کنید.

### ۳. راهنمای سرور (Server Guide)

پس از اجرای سرور، با بخش‌های زیر روبرو می‌شوید:

1.  **انتخاب محتوا (Share Configuration):**
    * ابتدا مشخص کنید که می‌خواهید یک پوشه کامل (`Share Directory`) یا یک فایل تکی (`Share Single File`) را به اشتراک بگذارید.
    * روی دکمه `Browse...` کلیک کرده و فایل یا پوشه مورد نظر را از روی سیستم خود انتخاب کنید.

2.  **تنظیمات سرور (Server Settings):**
    * **Port:** یک شماره پورت برای اتصال کلاینت‌ها وارد کنید (مقدار پیش‌فرض `5000` مناسب است).
    * **Max Clients:** حداکثر تعداد کاربرانی که می‌توانند همزمان متصل شوند را مشخص کنید.
    * **Require Password:** اگر می‌خواهید برای سرور رمز عبور بگذارید، این تیک را فعال کرده، رمز خود را وارد کنید و روی `Confirm Password` کلیک کنید.

3.  **شروع به کار سرور (Control Panel):**
    * پس از انجام تنظیمات، روی دکمه بزرگ **`▶️ Start`** کلیک کنید.
    * وضعیت سرور به "Running" تغییر می‌کند و IP آدرس‌های لازم برای اتصال کلاینت‌ها نمایش داده می‌شود:
        * **Server IP:** برای اتصال کلاینت دسکتاپ.
        * **Web Access:** برای اتصال با مرورگر وب (موبایل و کامپیوتر).

4.  **مدیریت کلاینت‌ها (Client Management Tab):**
    * در این تب، لیست تمام کلاینت‌های متصل، وضعیت آن‌ها (در حال دانلود، بیکار و...) و پیشرفت دانلودشان را به صورت زنده مشاهده می‌کنید.
    * با انتخاب یک کلاینت از لیست، می‌توانید با کلیک روی **`Disconnect Selected`** او را از سرور اخراج کرده یا با کلیک روی **`Send Warning`** برای او پیام اخطار ارسال کنید.

5.  **چت با کلاینت‌ها (Chats Tab):**
    * در این تب، لیست تمام کلاینت‌هایی که قابلیت چت با آن‌ها وجود دارد نمایش داده می‌شود.
    * یک کلاینت را از لیست انتخاب کرده و روی **`Open Chat Window`** کلیک کنید تا پنجره چت خصوصی با او باز شود.
    * اگر پیام جدیدی از کلاینتی دریافت کنید که پنجره چت او باز نیست، یک نقطه قرمز (🔴) روی عنوان تب "Chats" ظاهر می‌شود.

### ۴. راهنمای کلاینت (Client Guide)

پس از اجرای کلاینت، مراحل زیر را برای اتصال و دانلود دنبال کنید:

1.  **ورود اطلاعات سرور:**
    * در کادر `Server IP`، آدرس IP که در برنامه سرور نمایش داده شده را وارد کنید. با تایپ اعداد، برنامه به صورت خودکار برای خوانایی بهتر نقطه (`.`) اضافه می‌کند.
    * در کادر `Port`، همان پورتی که در سرور تنظیم کرده‌اید را وارد کنید.

2.  **اتصال به سرور:**
    * روی دکمه `🔗 Connect` کلیک کنید.
    * اگر سرور نیاز به رمز عبور داشته باشد، کادر `Password` فعال می‌شود. رمز را وارد کرده و روی `🔑 Login` کلیک کنید.

3.  **انتخاب و دانلود فایل‌ها:**
    * پس از اتصال موفق، لیست فایل‌های اشتراک‌گذاری شده نمایش داده می‌شود.
    * فایل‌های مورد نظر خود را با زدن تیک کنار آن‌ها انتخاب کنید. می‌توانید از تیک `Select All` برای انتخاب همه فایل‌ها استفاده کنید.
    * **مسیر ذخیره:** روی آیکون پوشه (📁) کلیک کرده و پوشه‌ای را روی سیستم خود به عنوان مقصد اصلی دانلودها انتخاب کنید.
    * **(اختیاری) ذخیره در پوشه جدید:** اگر تیک `Download into a new sub-folder` را بزنید، می‌توانید یک نام برای پوشه جدید وارد کرده و روی `Create` کلیک کنید. در این صورت، فایل‌ها در این زیرپوشه ذخیره خواهند شد.
    * در نهایت، روی دکمه **`⬇️ Download Selected`** کلیک کنید تا دانلود شروع شود.
    * اگر دانلود با خطا مواجه شود، همین دکمه به **`🔄 Retry Download`** تغییر می‌کند تا بتوانید دوباره تلاش کنید.

4.  **چت با سرور:**
    * پس از اتصال، دکمه **`💬 Chat with Server`** فعال می‌شود. با کلیک روی آن، پنجره چت با مدیر سرور باز می‌شود.
    * اگر پیام جدیدی از سرور دریافت کنید، یک نقطه قرمز (🔴) روی این دکمه ظاهر خواهد شد.

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
```