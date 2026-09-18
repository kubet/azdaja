import AppKit
import WebKit
import CryptoKit
import Foundation

let args = CommandLine.arguments
if args.count != 3 { fatalError("usage: test INPUT.html NEW-output.json") }
let input = URL(fileURLWithPath: args[1]).standardizedFileURL
let output = URL(fileURLWithPath: args[2])
precondition(!FileManager.default.fileExists(atPath: output.path))
let app = NSApplication.shared
app.setActivationPolicy(.prohibited)
let config = WKWebViewConfiguration()
config.websiteDataStore = .nonPersistent()
let view = WKWebView(frame: NSRect(x: 0, y: 0, width: 1100, height: 900), configuration: config)
let window = NSWindow(contentRect: NSRect(x: 0, y: 0, width: 1100, height: 900), styleMask: [.borderless], backing: .buffered, defer: false)
window.contentView = view

final class Audit: NSObject, WKNavigationDelegate {
    var refused: [String] = []
    func webView(_ webView: WKWebView, decidePolicyFor action: WKNavigationAction, decisionHandler: @escaping (WKNavigationActionPolicy) -> Void) {
        if action.request.url?.isFileURL == true { decisionHandler(.allow) }
        else { refused.append(action.request.url?.scheme ?? "missing"); decisionHandler(.cancel) }
    }
    func webView(_ webView: WKWebView, didFail navigation: WKNavigation!, withError error: Error) { fputs("navigation failed\n", stderr); exit(2) }
    func webView(_ webView: WKWebView, didFailProvisionalNavigation navigation: WKNavigation!, withError error: Error) { fputs("provisional navigation failed\n", stderr); exit(2) }
    func webView(_ webView: WKWebView, didFinish navigation: WKNavigation!) {
        let script = """
        (() => {
          const all = [...document.querySelectorAll('details[id^="window-"]')];
          const first = all[0];
          if(first) first.open = true;
          const pre = first?.querySelector('pre.source');
          return {
            title: document.title,
            user_agent: navigator.userAgent,
            counts: document.querySelector('#counts').textContent,
            criteria: document.querySelector('#criteria code').textContent,
            coverage_collapsed: !document.querySelector('#coverage-sources').open,
            completed: document.querySelectorAll('#completed details').length,
            unknown: document.querySelectorAll('#unknown details').length,
            pending: document.querySelectorAll('#pending details').length,
            styles: [...document.querySelectorAll('style')].map(e => e.textContent),
            csp: document.querySelector('meta[http-equiv="Content-Security-Policy"]').content,
            source_white_space: pre ? getComputedStyle(pre).whiteSpace : null,
            source_overflow_wrap: pre ? getComputedStyle(pre).overflowWrap : null,
            source_client_width: pre?.clientWidth,
            source_scroll_width: pre?.scrollWidth,
            page_client_width: document.documentElement.clientWidth,
            page_scroll_width: document.documentElement.scrollWidth,
            first_opened: first?.open,
            injected: window.__queue_injected ?? null,
            forbidden_elements: document.querySelectorAll('script,img,iframe,object,embed,link,form,input,button,svg,math,base').length,
            forbidden_attributes: [...document.querySelectorAll('*')].flatMap(e=>[...e.attributes].filter(a => /^on/i.test(a.name)||['src','srcset','style','action'].includes(a.name)||(a.name==='href'&&!a.value.startsWith('#'))).map(a=>a.name)),
            resources: performance.getEntriesByType('resource').map(e=>e.name),
            windows: all.map(e=>({id:e.id.substring(7),source:e.querySelector('pre.source code').textContent,summary:e.querySelector('summary').textContent,section:e.parentElement.id,audit_text:e.querySelector('dl').textContent}))
          };
        })()
        """
        webView.evaluateJavaScript(script) { result, error in
            guard error == nil, var report = result as? [String: Any], let rows = report["windows"] as? [[String:Any]] else { fputs("DOM audit failed\n", stderr); exit(2) }
            report["windows"] = rows.map { row -> [String:Any] in
                var next = row
                let text = next.removeValue(forKey: "source") as! String
                let data = Data(text.utf8)
                next["source_bytes"] = data.count
                next["source_sha256"] = SHA256.hash(data: data).map { String(format:"%02x",$0) }.joined()
                return next
            }
            report["refused_external_navigation"] = self.refused
            report["input_sha256"] = SHA256.hash(data: try! Data(contentsOf: input)).map { String(format:"%02x",$0) }.joined()
            report["engine"] = "System WebKit WKWebView, nonpersistent isolated data store"
            report["page_source_javascript"] = false
            let data = try! JSONSerialization.data(withJSONObject: report, options: [.sortedKeys])
            try! data.write(to: output, options: [.withoutOverwriting])
            let snapshot = WKSnapshotConfiguration()
            webView.takeSnapshot(with: snapshot) { image, error in
                if let image = image, let tiff = image.tiffRepresentation, let bmp = NSBitmapImageRep(data:tiff), let png = bmp.representation(using:.png, properties:[:]) {
                    try? png.write(to: output.appendingPathExtension("png"), options: [.withoutOverwriting])
                }
                print("browser DOM and rendering receipt written")
                exit(0)
            }
        }
    }
}
let audit = Audit()
view.navigationDelegate = audit
view.loadFileURL(input, allowingReadAccessTo: input.deletingLastPathComponent())
DispatchQueue.main.asyncAfter(deadline:.now()+25) { fputs("browser acceptance deadline\n", stderr); exit(124) }
app.run()
