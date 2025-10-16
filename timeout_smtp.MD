# Timeout SMTP Server

`timeout_smtp.py` is a simple, configurable Python script that simulates a slow or unresponsive SMTP server. Its purpose is to help developers, network administrators, and reliability engineers test how their systems behave when an SMTP server accepts a connection but then fails to respond in a timely manner.

This is an essential tool for **resilience testing**, helping you uncover and fix issues related to network timeouts, application logic, and user experience under adverse network conditions.

---

## Why Is This Useful?

In a perfect world, network services are always fast and reliable. In reality, servers can become overloaded, networks can become congested, and firewalls can drop packets. When your application tries to send an email through a misbehaving SMTP server, it can lead to several problems:

* **Application Hangs:** Web requests or background jobs can get stuck waiting for a network response, consuming resources and degrading user experience.
* **Resource Exhaustion:** If many threads or processes get stuck waiting for an SMTP server, you can run out of available workers, database connections, or memory.
* **Silent Failures:** Poorly configured clients might not time out correctly, leading to emails being lost without any error logs.

This script helps you **proactively simulate** these failure scenarios in a controlled environment so you can build more robust and reliable software.

---

## Features

* **Zero Dependencies:** Runs with a standard Python 3 installation. No `pip install` needed.
* **Highly Configurable:** Control the bind IP, port, timeout duration, and behavior using environment variables.
* **Multiple Failure Modes:** Simulate different real-world failure scenarios (e.g., timeout before the banner, after the banner, or during a partial response).
* **Concurrent Client Handling:** Uses threading to handle multiple simultaneous connections, allowing you to test how your system handles multiple stuck connections at once.
* **Graceful Shutdown:** Responds to `SIGINT` (Ctrl+C) and `SIGTERM` for clean termination.

---

## How to Use

### Requirements

* Python 3.x

### Running the Server

1.  Save the script as `timeout_smtp.py`.
2.  Run it from your terminal:
    ```bash
    python3 timeout_smtp.py
    ```
3.  The server is now running and will accept connections. To stop it, press **`Ctrl+C`**.

### Configuration

The server's behavior is controlled entirely through environment variables.

| Variable      | Description                                                                 | Default             |
| :------------ | :-------------------------------------------------------------------------- | :------------------ |
| `BIND_IP`     | The IP address to bind the server to. Use `0.0.0.0` to listen on all interfaces. | `127.0.0.1`         |
| `PORT`        | The TCP port to listen on.                                                  | `2525`              |
| `SLEEP_SECS`  | The number of seconds the server will stall or "sleep" for each connection. | `600` (10 minutes)  |
| `MODE`        | The timeout simulation mode. See **Modes of Operation** below for details.  | `no_banner`         |
| `BANNER_HOST` | The fake hostname used in the welcome banner (for `after_banner` mode).     | `sleepy.mx.local`   |
| `LOG_LEVEL`   | The logging verbosity (e.g., `DEBUG`, `INFO`, `WARNING`, `ERROR`).          | `INFO`              |

---

## Modes of Operation

The `MODE` environment variable is the most important setting, as it defines *how* the server will time out.

### 1. `no_banner` (Default)
This mode simulates a server that accepts a TCP connection but never sends the initial SMTP `220` banner. This is common if a server is behind a firewall that accepts the connection but then drops the packets, or if the service is completely hung.

* **Server Behavior:** Accepts the connection, logs the new peer, and immediately sleeps for `SLEEP_SECS`. It sends no data.
* **Client Experience:** The client connects successfully but receives no data. It will eventually time out waiting for the server greeting.

### 2. `after_banner`
This mode simulates a server that is initially responsive but hangs after sending the welcome banner. This can happen if the SMTP service process crashes or hangs after the initial handshake.

* **Server Behavior:** Accepts the connection, sends a complete `220 ESMTP Service Ready` banner, and then immediately sleeps for `SLEEP_SECS`.
* **Client Experience:** The client connects and receives the banner, thinking the server is healthy. It then times out when it sends its first command (e.g., `EHLO` or `HELO`) and waits for a response that never comes.

### 3. `partial_line`
This mode simulates a server that starts sending the banner but never finishes the line. This can test a client's robustness against malformed or incomplete network data, which might occur due to packet fragmentation or a bug in the server software.

* **Server Behavior:** Accepts the connection, sends only the partial string `"220 "`, and then sleeps for `SLEEP_SECS`. Note the lack of a hostname or the terminating `\r\n` characters.
* **Client Experience:** The client connects and receives a fragment of data. It will get stuck waiting for the rest of the line to arrive in its network buffer, eventually timing out.

---

## Examples & Use Cases

### Example 1: Basic Run

Run the server on the default port (2525) to simulate a server that never sends a banner.
```bash
python3 timeout_smtp.py