import importlib.util, os
from pathlib import Path
c=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location("harness",c/"samsun-reply-validation.py")
m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
m.SOURCE=Path("/work/mg551/gsd-phase04-recovery.L0IReu/yeni-3961-source")
os.environ["GSD0404_PREVIEW_STAGING"]="/work/mg551/gsd-phase04-recovery.L0IReu"
m.main(c/"3961-yeni-committee-package-draft.json",c/"3961-yeni-committee-review-draft.json",scope="3961-yeni-committee-v2",event_id="0404-3961-yeni-committee-event",relation_id="0404-3961-yeni-committee-relation",absent_dispute="")
