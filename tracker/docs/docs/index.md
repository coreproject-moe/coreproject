---
icon: lucide/rocket
---

# Get started

<p align='center'>
  <img src="images/icon.svg" alt='logo' width='200' loading='lazy' />
</p>

<p align='center'>
  Torrent Tracker for the next generation of torrent streaming
</p>

---

CoreProject tracker is a [python](https://www.python.org/) based, [redis](https://redis.io/) backend highly available torrent tracker written for the next generation of torrent streaming.


Features:

* Highly Scalable: Multi-core worker architecture with CPU_COUNT TCP + CPU_COUNT UDP workers, each on its own event loop. Scales infinitely via Redis clustering.
* Geo-Aware Peer Selection: Powered by [IPLocate.io](https://iplocate.io) (CC BY-SA 4.0), peers are ranked by combined geo distance, BEP40 network proximity, and activity score.
* Truly Event Driven: No shared data between processes. Redis acts as the single source of truth with TTL-based geo caching.
* Protocol Compatible: Full BEP3 (HTTP), BEP15 (UDP), and WebTorrent (WebSocket) compatibility verified against libtorrent, anacrolix/torrent, and webtorrent.
* Reverse Proxy Ready: Supports nginx, Caddy, Apache, HAProxy, Cloudflare, Fly.io, and Plesk proxy headers with spoofing protection.
* Radar Map API: Real-time swarm visualization via `/api/tracker_data` endpoint with country-level peer location data.
* Comprehensive Testing: 100% code coverage with unit, integration, and BEP protocol compatibility tests.