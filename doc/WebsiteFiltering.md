# How does Website Filtering work?

The list works either as a **denylist** (block listed domains) or an
**allowlist** (block everything except listed domains).

When a restricted user's session becomes the active session, `PPCDaemon`:

1. Configures **smartdns-rs** (`/etc/smartdns/smartdns.conf`) as a local DNS
   server that does not resolve blocked domains:

   ```
   # denylist:                    # allowlist:
   address /denied.com/#          address /allowed.com/-
   address /*.denied.com/#        address /*.allowed.com/-
                                  address /./#
   ```

2. Points `/etc/resolv.conf` to `nameserver 127.0.0.1` and locks the file
   with `chattr +i` so it can not be changed.
3. Writes managed browser policies (Chrome, Chromium, Brave: `URLBlocklist`/
   `URLAllowlist`; Firefox: `WebsiteFilter`) and disables DNS-over-HTTPS in
   them, so the browsers can not bypass the local DNS.

When the active session changes to a non-restricted user, the smartdns
service is stopped, `/etc/resolv.conf` is restored and the browser policies
are removed.
