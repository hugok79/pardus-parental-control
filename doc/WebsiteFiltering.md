# How does Website Filtering work?

1. Browser policies are set in major browsers(google chrome, chromium, firefox, brave)
2. Content of the `/etc/resolv.conf` changed to: `nameserver 127.0.0.1`
3. For prevention changing `/etc/resolv.conf` by another instance, `chattr +i` applied.
4. Smartdns-rs service configured and service enabled to work as a local dns server. (/etc/smartdns/smartdns.conf)


### smartdns-rs:
Example allowlist:
```
# "Allow Only" with subdomains
address /*/# 
address /allowed.com/-
address /*.allowed.com/-
```
Example denylist:
```
# "Deny Only" with subdomains
address /denied.com/#
address /*.denied.com/#
```

Example full smartdns.conf:

```
# Listen on local port 53
bind [::]:53
bind-tcp [::]:53

# Certificated Listening
#bind-tls [::]:853 # DoT
#bind-https [::]:853 # DoH

tcp-idle-time 4

# Base DNS Server
server 1.1.1.3
server-tcp 1.1.1.3

# DNS over TLS (DoT)
#server-https https://cloudflare-dns.com/dns-query 
#server-tls {BASE_DNS_SERVER}

# Dns over Quic (DoQ)
# server-quic family.adguard-dns.com

# If Denylist Selected:
address /google.com/#
address /*.google.com/#

# IF Allowlist Selected:
address /google.com/-
address /*.google.com/-
address /./#

```

### Browser Policy
Chrome based:
- Chrome: `/etc/opt/chrome/policies/managed/policies.json`
- Brave: `/etc/brave/policies/managed/policies.json`
- Chromium `/etc/chromium/managed/policies.json`
policies.json:
```
{
	"URLBlocklist": ["*"],
	"URLAllowlist": ["youtube.com","pardus.org.tr"], # block everything, just permit youtube and pardus
	"DnsOverHttpsMode": "off"
}

```
Firefox `/etc/firefox/policies/policies.json`:
```
{
  "policies": {
    "WebsiteFilter": {
      "Block": ["<all_urls>"],
      "Exceptions": ["*://*.youtube.com/*", "*://*.pardus.org.tr/*"]
    },
    "DNSOverHTTPS": {
    	"Enabled": false,
    	"Locked": true
    }
  }
}
```

All these settings applied by Pardus Parental Control regarding the list in `/var/lib/pardus/pardus-parental-control/profiles.json`.