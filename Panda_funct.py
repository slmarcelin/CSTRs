import tkinter as tk
from pandas import DataFrame
import matplotlib.pyplot as plt

import pandas as pd
import seaborn as sns
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg




def GRAPH(path = 'LOG_6.csv', info = 'Temperature', from_date = 0 ,to_date = 0 ):
	# Using the index_col and parse_dates parameters of the read_csv() function.
	CsvFile = pd.read_csv(path, index_col=0, parse_dates=True)
	Data= CsvFile.loc[from_date : to_date]
	# CREATE dataframe
	dframe = DataFrame(Data,columns=[info])
	return dframe











# Using the index_col and parse_dates parameters of the read_csv() function.
#opsd_daily = pd.read_csv('LOG_6.csv', index_col=0, parse_dates=True)

# FILTERING DATA
#from_date = '2019-01-01 00:00:00'   ## YYYY-MM-DD
#to_date = '2019-06-15 11:59:00'		## YYYY-MM-DD

#Data1= opsd_daily.loc[from_date : to_date]
#print(Data1)

# CREATE dataframe
#df1 = DataFrame(Data1,columns=['Temperature'])
#print(df1)





# root= tk.Tk()

# figure = plt.Figure(figsize=(15,15), dpi=100)
# ax = figure.add_subplot(111)
# line = FigureCanvasTkAgg(figure, root)
# line.get_tk_widget().pack()


# df = GRAPH(path = 'LOG_6.csv', info = 'Temperature', from_date = '2019-01-01 00:00:00' ,to_date = '2019-06-15 11:59:00'	 )
# df.plot(kind='line', legend=True, ax=ax, color='r',marker='.', fontsize=10)
# ax.set_title('Reactor temperature 2019')



# root.mainloop()


















