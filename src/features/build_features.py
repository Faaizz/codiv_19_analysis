import numpy as np
import pandas as pd
from sklearn import linear_model
from scipy import signal

# Create Linear Regression Model
reg= linear_model.LinearRegression(fit_intercept= True)  


def get_doubling_rate_via_regression(in_array):
    """ Approximate the doubling time using linear regression.

    3 datapoints are used to approximate the number of days 
    it takes for the number of infected people to double at each point.

    Parameters:
    ----------
    in_array: List/ numpy Array
        input data

    Returns:
    -------
    doubling_time: double
    """
    
    # Assert output vector is 3 datapoints long
    assert len(in_array)==3
 
    y= np.array(in_array)
    # Calculate slope using central difference
    X= np.arange(-1,2).reshape(-1,1)

    # Fit data
    reg.fit(X,y)
    intercept= reg.intercept_
    slope= reg.coef_

    return intercept/slope


def rolling_regression(df_input, col="confirmed"):
    """ Roll over entries to approximate the doubling time using linear regression.

    Parameters:
    ----------
    df_input: pandas DataFrame
        input data
    col: string
        key to column which holds data entries

    Returns:
    -------
    result: pandas Series
    """
    
    days_back= 3
    
    result= df_input[col].rolling(
            window=days_back,
            min_periods=days_back
        ).apply(get_doubling_rate_via_regression, raw=False)
    
    return result


def savgol_filter(df_input, col='confirmed', window=5):
    """ Filter data using savgol filter.

    Parameters:
    ----------
    df_input: pandas DataFrame
        input data
    col: string
        key to column which holds data entries

    Returns:
    -------
    df_result: pandas DataFrame
        df_input with additional column with name col+"_filtered"
    """

    window=5
    degree=1

    df_result=df_input

    filter_in= df_input[col].fillna(0)
    result= signal.savgol_filter(
            np.array(filter_in), window, degree
        )

    df_result[col+ "_filtered"]= result
    return df_result
    

def calc_filtered_data(df_input, filter_on='confirmed'):
    """ Filter data using savgol filter and return merged dataframe

    Parameters:
    ----------
    df_input: pandas DataFrame
        input data
    filter_on: string
        key to column which holds data entries on which to filter

    Returns:
    -------
    df_out: pandas DataFrame
        df_input with additional column with name filter_on+"_filtered"
    """

    # Assertion
    must_contain= set(['state', 'country', filter_on])
    assert must_contain.issubset(set(df_input.columns))

    pd_filt_res= df_input.groupby(['state','country']).apply(savgol_filter, filter_on).reset_index()
    df_out= pd.merge(df_input, pd_filt_res[['index', filter_on+'_filtered']], on=['index'], how='left')

    return df_out


def calc_doubling_rate(df_input, double_on='confirmed'):
    """ Calculate doubling rate using linear regression and return merged dataframe

    Parameters:
    ----------
    df_input: pandas DataFrame
        input data
    double_on: string
        key to column which holds data entries

    Returns:
    -------
    df_out: pandas DataFrame
        df_input with additional column with name double_on+"_filtered"
    """

    # Assertion
    must_contain= set(['state', 'country', double_on])
    assert must_contain.issubset(set(df_input.columns))

    pd_doub_res= df_input.groupby(['state','country']).apply(rolling_regression, double_on).reset_index()
    pd_doub_res= pd_doub_res.rename(columns={'level_2': 'index', double_on: double_on+"_DR"})

    df_out= pd.merge(df_input, pd_doub_res[['index', double_on+'_DR']], on=['index'], how='left')

    return df_out



if __name__ == "__main__":
    # Test data
    test_data= np.array([2,4,6])
    # Expected result= 2
    result= get_doubling_rate_via_regression(test_data)
    assert(int(result[0]) == 2)

    pd_JH_rel= pd.read_csv(
            'data/processed/COVID_relational_full.csv', 
            sep=';', parse_dates=[0]
        )
    pd_JH_rel= pd_JH_rel.sort_values('date', ascending=True).reset_index(drop=True)
    pd_JH_rel= pd_JH_rel.reset_index()

    pd_res= calc_filtered_data(pd_JH_rel, filter_on='confirmed')
    pd_res= calc_doubling_rate(pd_res, double_on='confirmed')
    pd_res= calc_doubling_rate(pd_res, double_on='confirmed_filtered')

    # Cleanup confirmed_filtered_DR
    DR_mask= pd_res['confirmed']>100
    pd_res['confirmed_filtered_DR']= pd_res['confirmed_filtered_DR'].where(DR_mask, other=np.NaN)

    # Save
    pd_res.to_csv('data/processed/COVID_final_set.csv', sep=';', index=False)

