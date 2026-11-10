"""Gerçek Chromium ile kaynak bağlantısına tıklanmasını doğrula."""
import glob
import os
from pathlib import Path
import shutil
import subprocess
import tempfile
import functools
import http.server
import threading


def browser():
    candidates = [os.environ.get('BROWSER_BIN')] + [shutil.which(n) for n in ('chromium', 'chromium-browser', 'google-chrome', 'chrome')]
    candidates += glob.glob(str(Path.home() / '.cache' / '**' / 'chrome-headless-shell'), recursive=True)
    return next((p for p in candidates if p and Path(p).is_file() and os.access(p, os.X_OK)), None)


def probe(report):
    executable = browser()
    if not executable: raise RuntimeError('Headless Chrome bulunamadı')
    content = Path(report).read_text(encoding='utf-8')
    marker = '<script>document.querySelector("a[href$=kurulus]").click();const d=document.getElementById("source-kurulus");document.body.dataset.probe=(d.open && d.textContent.includes("24.07.2026") && !!d.querySelector("a[href^=https]") && !!d.querySelector("a[href*=readable]")) ? "PASS" : "FAIL";</script>'
    with tempfile.TemporaryDirectory() as directory:
        copy = Path(directory) / 'probe.html'
        copy.write_text(content.replace('</html>', marker + '</html>'), encoding='utf-8')
        result = subprocess.run([executable, '--headless', '--no-sandbox', '--disable-gpu', '--dump-dom', copy.as_uri()], capture_output=True, text=True, timeout=30)
        if result.returncode or 'data-probe="PASS"' not in result.stdout:
            raise AssertionError('Tarayıcı kaynak tıklamasını doğrulayamadı: ' + result.stderr[-1000:])
        return 'BROWSER_CLICK_OK'


def probe_tabs(content, source_id):
    executable = browser()
    if not executable:
        raise RuntimeError('Headless Chrome bulunamadı')
    marker = '''<script>
const first=document.querySelector('[role=tab]'), next=first.nextElementSibling;
next.click(); const clicked=next.getAttribute('aria-selected')==='true';
next.dispatchEvent(new KeyboardEvent('keydown',{key:'Home',bubbles:true}));
const keyboard=first.getAttribute('aria-selected')==='true' && document.activeElement===first;
const citation=document.querySelector('[role=tabpanel] .citation[href="#source-''' + source_id + '''"]');
citation.click(); const source=document.getElementById('source-''' + source_id + '''');
const opened=source.open && !source.closest('[role=tabpanel]').hidden;
source.open=false;
setTimeout(()=>{document.body.dataset.probe=(clicked&&keyboard&&opened&&document.activeElement===citation&&document.documentElement.scrollWidth<=innerWidth)?'PASS':'FAIL';document.body.dataset.checks=[clicked,keyboard,opened,document.activeElement===citation,document.documentElement.scrollWidth<=innerWidth].join(',')},50);
</script>'''
    with tempfile.TemporaryDirectory() as directory:
        path = Path(directory) / 'index.html'
        path.write_text(content.replace('</html>', marker + '</html>'), encoding='utf-8')
        handler = functools.partial(http.server.SimpleHTTPRequestHandler, directory=directory)
        server = http.server.ThreadingHTTPServer(('127.0.0.1', 0), handler)
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()
        try:
            for url in (path.as_uri(), 'http://127.0.0.1:%d/index.html' % server.server_port):
                result = subprocess.run([executable, '--headless', '--no-sandbox', '--disable-gpu', '--window-size=360,800', '--virtual-time-budget=1500', '--dump-dom', url + '#source-' + source_id], capture_output=True, text=True, timeout=30)
                if result.returncode or 'data-probe="PASS"' not in result.stdout:
                    import re
                    raise AssertionError('Tarayıcı etkileşimi başarısız: ' + str(re.findall(r'data-checks="[^"]+"', result.stdout)) + result.stderr[-300:])
        finally:
            server.shutdown()
            server.server_close()
            thread.join()
    return 'BROWSER_TABS_OK'
