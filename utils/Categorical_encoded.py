import utils 
"""
The functions made below use the functions in the utils file. The data must contain columns created by 
these functions.

"""
convert_ts(ts)
parse_ts_listen(data)
parse_release_date(data)
get_moment_of_day(ts_listen)
parse_moment_of_day(data)
get_user_age_bucket(user_age)
parse_user_age(data)


def time_of_day_categorical(data):
    """
    Converts the moment of day buckets to categorical varibales in different columns.
    Input: pandas DataFrame
    Output: Appended dataframe(Use data = time_of_day_categorical(data) to change the
    existing Dataframe)
    
    """
   if "moment_of_day" not in data:
        raise IOError("The input dataframe does not contain "
                      "the column 'moment_of_day'")
        
    temp1 = pd.get_dummies(data.moment_of_day) # Making the dummy variable from the categorical 'moment_of_day'
    
    data = pd.concat([data,temp1],axis =1) # Joining the new dataset with the encoding to the original data
    
    del temp1
    
    return data

data = time_of_day_categorical(data)  #Function Call
del data['moment_of_day'] #Removing the 'moment_of_day' column


def age_categorical(data):

    """
    Converts the age buckets to categorical varibales in different columns.
    Input: pandas DataFrame
    Output: Appended dataframe(Use data = age_categorical(data) to change the
    existing Dataframe)
    
    """
   
    if "user_age_bucket" not in data:
        raise IOError("The input dataframe does not contain "
                      "the column 'user_age_bucket'")
        
    temp = pd.get_dummies(data.user_age_bucket) #Making the dummy variable from the categorical 'user_age_bucket'
    
    data = pd.concat([data, temp],axis =1) ## Joining the new dataset with the encoding to the original data
    
    del temp
    
    return data


data = age_categorical(data) #Function Call
del data['user_age_bucket']  #removing the 'user_age_bucket' column











