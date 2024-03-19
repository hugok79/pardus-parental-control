## Yöntem:

Kısıtlanabilir kullanıcıların network ayarlarını değiştirebilme yetkisi olmamalı. (ilk defa kullanıcı açılırken, grouplar ile)

### Kullanım
1. pardus-parental-control servisi kullanıcı login olduğunda açılır
2. Servis kullanıcı adına uygun profili devreye sokar.
3. /etc/resolv.conf içeriği yerel adrese değiştirilir: `nameserver 127.0.0.1`
4. /etc/resolv.conf'un sadece root tarafından değiştirilmesi garantisi için: `sudo chmod o+t /etc/resolv.conf` veya `sudo chattr +i /etc/resolv.conf`, tekrar değiştirilebilir yapmak için `-i`
5.  smartdns servisi whitelist/blacklist'e göre pardus-parental-control tarafından config edilir(/etc/smartdns/smartdns.conf) ve servis çalıştırılır.

### smartdns-rs:
Allow List örnek içeriği, sadece google.com ve yandex.com'a izin ver.
```
# "Allow Only" with subdomains
address /*/# 
address /allowed.com/-
address /*.allowed.com/-
```
Deny List örnek içeriği, google.com ve yandex.com'u yasakla.
```
# "Deny Only" with subdomains
address /denied.com/#
address /*.denied.com/#
```
smartdns.conf dosyasının tam içeriği (*allow veya deny sadece biri olmalı*):

```
# Listen on local port 53
bind [::]:53
bind-tcp [::]:53  

tcp-idle-time 5

# Cache
cache-size 32768

# DNS servers, 1.1.1.3 is basically: "1.1.1.1 + No Malware + No Adult Content"
server 1.1.1.3
server-tls 1.1.1.3

# Configure DoH3
server-h3 1.1.1.1

# Configure DoQ
server-quic unfiltered.adguard-dns.com


# == DOMAIN FILTERING ==

# "Deny Only" with subdomains
address /denied.com/#
address /*.denied.com/#

# "Allow Only" with subdomains
address /*/# 
address /allowed.com/-
address /*.allowed.com/-

```