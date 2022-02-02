# How to use dataChange.py

## Purpose 
The purpose of this python script is to merge to data files : one from the capteurs, and the other one from the Weather.

1) Create and launch your virtual environment with 
```bash
python -m venv venv # create environment
```

```bash
source venv/bin/activate 
```

At the end, `deactivate` to deactivate your environment.

2) Put your data files in the dataCapteurs directory.

3) go to the directory with your terminal : `cd dataCapteurs`

4) launch the python script with 
```bash
python dataChange.py nameOfCapteurDataFile nameOfWeatherDataFile nameOfOutputFile
```

For example : 
```bash
python dataChange.py analyse4-ECN0811.txt Potenvol_sable_50.pot test
```

5) A file `test.csv`will be created with the output. By default, the output is `res.csv`


**In order to work, the data needs to be exactly as the same format every time !!**

# How to use gpx_to_csv.py

1) 