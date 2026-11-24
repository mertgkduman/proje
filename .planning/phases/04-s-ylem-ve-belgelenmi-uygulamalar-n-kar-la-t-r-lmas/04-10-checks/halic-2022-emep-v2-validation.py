from pathlib import Path
c=Path(__file__).resolve().parent;text=(c/'halic-2022-emep-validation.py').read_text().replace("case='halic-2022-emep'","case='halic-2022-emep-v2'")
exec(compile(text,str(c/'halic-2022-emep-validation.py'),'exec'))
