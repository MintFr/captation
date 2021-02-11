# -*- coding: utf-8 -*-
"""
Created on Mon Jan 11 15:48:10 2021
@author: victo
"""

from datetime import datetime
from datetime import timedelta
from datetime import date
import random

fichiertest=open('Concentration_Fond.dat','w')
fichiertest.write('Date\tPM10\tPM25\tNO2\tNO\tO3\n')

Begin = datetime(year=2021, month=1, day =8, hour = 9, minute=0)
End = datetime(year=2021, month=1, day =10, hour = 8, minute=0)
H = timedelta(seconds=3600)
t=Begin

TXT=''
while t<=End:
    text=str(t.day)+'/'+str(t.month)+'/'+str(t.year)+'/ '+str(t.hour)+':'+str(t.minute)+'\t 1\t 1 \t 1 \t 1 \t 1\n'
    TXT=TXT+text
    t=t+H
fichiertest.write(TXT)

fichiertest.close()
