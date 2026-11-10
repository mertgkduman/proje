"""Gerçek Chromium ile kaynak bağlantısına tıklanmasını doğrula."""
import glob
import os
from pathlib import Path
import shutil
import subprocess
import tempfile


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
