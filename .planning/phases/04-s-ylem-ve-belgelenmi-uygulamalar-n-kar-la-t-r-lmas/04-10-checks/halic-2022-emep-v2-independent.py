from pathlib import Path
c=Path(__file__).resolve().parent;text=(c/'halic-2022-emep-independent.py').read_text().replace('halic-2022-emep-','halic-2022-emep-v2-')
exec(compile(text,str(c/'halic-2022-emep-independent.py'),'exec'))
