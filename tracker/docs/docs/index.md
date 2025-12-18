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

* Highly Scalable: The implementation is based on the highly [architecture](architecture.md), this will be able to scale infinitely (via redis clustering).
* Truly Event Driven: The [architecture](architecture.md) is truly event driven, there is no data shared between processes. Redis acts as a single source of truth.
* Efficient Architecture: Our [architecture](architecture.md) is highly efficient,