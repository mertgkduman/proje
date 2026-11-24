from pathlib import Path
here=Path(__file__).resolve().parent
text=(here/'baglar-2016-reports-validation.py').read_text().replace("case='baglar-2016-reports'","case='baglar-2016-reports-v2'").replace('db451e12baa2c6670c1fc074b9150339d5f109a233415bdd86886adf6dd11222','005fda05b3e462a76c0a5d8a33248eb38c149d6adcdd8ea2e84c376695b6cccd').replace('43fd373990be7a923d8b71992d8233cf9871a82679c5d5bc81ac477d9fe3f331','4dac79689061ea897d70c201265b0efeb4707fc76e0c6ba7f7d0932fcabf58be')
exec(compile(text,str(here/'baglar-2016-reports-validation.py'),'exec'))
