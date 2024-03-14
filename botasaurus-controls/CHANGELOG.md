3.1.0 / 2021/08/23
====================
- Add `sessionToken` option to persist generated headers

3.0.1 / 2021/08/20
====================
- Use own proxy agent

3.0.0 / 2021/08/19
====================
- Switch to TypeScript
- Enable insecure parser by default
- Use `header-generator` to order headers
- Remove `default` export in favor of `import { gotScraping }`
- Fix leaking ALPN negotiation

2.1.2 / 2021/08/06
====================
- Mimic `got` interface

2.1.1 / 2021/08/06
====================
- Use `header-generator` v1.0.0

2.1.0 / 2021/08/06
====================
- Add `TransfomHeadersAgent`
- Optimizations
- Use Got 12
- docs: fix instances anchor

2.0.2-beta / 2021/08/04
====================
- Use `TransfomHeadersAgent` internally to transform headers to `Pascal-Case`

2.0.1 / 2021/07/22
====================
- pin `http2-wrapper` version as the latest was causing random CI failures

2.0.0 / 2021/07/22
====================
- **BREAKING**: Require Node.js >=15.10.0 because HTTP2 support on lower Node.js versions is very buggy.
- Fix various issues by refactoring from got handlers to hooks.

1.0.4 / 2021/05/17
====================
- HTTP2 protocol resolving fix

1.0.3 / 2021/04/27
====================
- HTTP2 wrapper fix

1.0.2 / 2021/04/18
====================
- Fixed TLS

1.0.1 / 2021/04/15
====================
- Improved ciphers
- Fixed request payload sending

1.0.0 / 2021/04/07
====================
- Initial release
