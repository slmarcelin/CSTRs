
from pandas import DataFrame

import pandas as pd



def GRAPH(path = 'LOG_6.csv', info = 'Temperature', from_date = 0 ,to_date = 0 ):
	# Using the index_col and parse_dates parameters of the read_csv() function.
	CsvFile = pd.read_csv(path, index_col=0, parse_dates=True)
	
	Data = CsvFile.loc[from_date : to_date]
	# CREATE dataframe
	dframe = DataFrame(Data,columns=[info])
	return dframe


def DataFrame(path,rate,TimeRange,now):
	DF = pd.read_csv(path, index_col=0) #Fetch the csv file for the selected counter
	DF.index= pd.to_datetime(DF.index,errors='coerce', format='%Y-%m-%d %H:%M:%S') #set the first column to datetime
	DF=DF.loc[str(TimeRange) : str(now)] #Select the data based on that
	DF=DF.resample(rate).mean()  #Resample the data based on hours and sum the data for each hour
	DF=DF.dropna()

	return DF

