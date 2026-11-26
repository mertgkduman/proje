import importlib.util, os, hashlib
from pathlib import Path
c=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location("harness",c/"samsun-reply-validation.py")
m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
for name, expected in (("3961-yeni-committee-package-draft.json", "df8f9c5253112ec11cbdf28208fdeac0a97a811d5acbdd210fb53f217b55b629"), ("3961-yeni-committee-review-draft.json", "5ad1689587e43e152725d82fbdabc18ed69f87e293e60413892c0e72c217e1ce")):
 assert hashlib.sha256((c/name).read_bytes()).hexdigest() == expected, name
_original_call = m.subprocess.call
def node_local_call(*args, **kwargs):
 env = os.environ.copy()
 env["TMPDIR"] = "/tmp"
 kwargs["env"] = env
 return _original_call(*args, **kwargs)
m.subprocess.call = node_local_call
m.SOURCE=Path("/work/mg551/gsd-phase04-recovery.L0IReu/yeni-3961-source")
os.environ["GSD0404_PREVIEW_STAGING"]="/work/mg551/gsd-phase04-recovery.L0IReu"
m.main(c/"3961-yeni-committee-package-draft.json",c/"3961-yeni-committee-review-draft.json",scope="3961-yeni-committee-v3",event_id="0404-3961-yeni-committee-event",relation_id="0404-3961-yeni-committee-relation",absent_dispute="")
