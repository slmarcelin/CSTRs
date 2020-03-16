import pandas as pd


# --- Function to obtain the dataframe of a file -------------
# ARGUMENTS:
# path-> file to be read
# rate-> rate to calculate the mean value of the variable
# TimeRange-> used to obtain the data within a range of time
# now-> current time
def FileDataFrame(path, rate, TimeRange, now):

    # Fetch the csv file
    DF = pd.read_csv(path, index_col=0)

    # set the first column to datetime
    DF.index = pd.to_datetime(DF.index,
                              errors='coerce',
                              format='%Y-%m-%d %H:%M:%S')

    # Select the data within atime range
    DF = DF.loc[str(TimeRange): str(now)]

    # Resampling the data with the mean
    DF = DF.resample(rate).mean()

    # Drop empty entries
    DF = DF.dropna()

    return DF
