#!/usr/bin/env python
# coding: utf-8

# # Assignment Overview Part 1:
# 
# Part 1, attribution: 
# Allocate conversions by channel (social, organic_search, referral, email, paid_search, display, direct) and evaluate effectiveness
# 
# • Test 3 methods for allocation
# 
# • Calculate CAC for each of the channels
# 
# • Discuss observations and potential conclusions from CAC calculations

# ## Import Dataset

# In[1]:


import pandas as pd
import numpy as np


# In[2]:


channel_spend_df = pd.read_csv('channel_spend_student_data.csv')


# In[48]:


#For part 1, keep only total spend info
total_spend = channel_spend_df[channel_spend_df['tier'] == 'total']


# In[65]:


import ast
total_dict = ast.literal_eval(total_spend['spend by channel'].item())


# In[70]:


total_spend_df = pd.DataFrame.from_dict(total_dict,orient='index',columns=['total_spend'])


# In[4]:


aa_df = pd.read_csv('attribution_allocation_student_data.csv')


# In[6]:


aa_df.shape


# In[30]:


#Keep only converted rows
aa_df_converted = aa_df[aa_df['convert_TF'] == True]


# In[31]:


aa_df_converted.shape


# # First Allocation Method - First Interaction

# In[23]:


#Function for First Interaction

def first_interaction(row):
    label = row.touch_1
    return label


# In[32]:


aa_df_converted['first_interaction_allocation'] = aa_df_converted.apply(first_interaction,axis=1)


# In[71]:


first_interaction_df = aa_df_converted.groupby('first_interaction_allocation').agg({'convert_TF': 'count'})


# In[79]:


first_interaction_df = first_interaction_df.join(total_spend_df)


# In[81]:


first_interaction_df['CAC'] = first_interaction_df['total_spend'] / first_interaction_df['convert_TF']


# In[82]:


first_interaction_df


# Display has the lowest CAC, followed by email and social, while referral and paid_search are the most expensive channels.

# # Second Allocation Method - Last Interaction

# In[88]:


def last_interaction(row):
    if pd.notna(row.touch_5) == True:
        label = row.touch_5
    elif pd.notna(row.touch_4) == True:
        label = row.touch_4
    elif pd.notna(row.touch_3) == True:
        label = row.touch_3
    elif pd.notna(row.touch_2) == True:
        label = row.touch_2
    else:
        label = row.touch_1
    return label


# In[89]:


aa_df_converted['last_interaction_allocation'] = aa_df_converted.apply(last_interaction,axis=1)


# In[91]:


last_interaction_df = aa_df_converted.groupby('last_interaction_allocation').agg({'convert_TF': 'count'})


# In[92]:


last_interaction_df = last_interaction_df.join(total_spend_df)


# In[94]:


last_interaction_df['CAC'] = last_interaction_df['total_spend'] / last_interaction_df['convert_TF']


# In[95]:


last_interaction_df


# Using last interaction allocation method, display still has the lowest CAC, followed by social and email, while referral and paid_search remains the most expensive.

# # Third Allocation Method: Last Non-Direct Interaction

# In[102]:


def last_nondirect_interaction(row):
    
    #boolean variable assigned
    assigned = False
    
    #Check 5th interaction
    if pd.notna(row.touch_5) == True:
        if row.touch_5 != 'direct':
            label = row.touch_5
            assigned = True
    
    #Check 4th interaction if not assigned 
    if assigned == False:        
        if pd.notna(row.touch_4) == True:
            if row.touch_4 != 'direct':
                label = row.touch_4
                assigned = True
    
    #Check 3rd interaction if not assigned
    if assigned == False:
        if pd.notna(row.touch_3) == True:
            if row.touch_3 != 'direct':
                label = row.touch_3
                assigned = True
    
    #Check 2nd interaction if not assigned
    if assigned == False:
        if pd.notna(row.touch_2) == True:
            if row.touch_2 != 'direct':
                label = row.touch_2
                assigned = True
    
    #If still not assigned, it means the customer only had 1st interaction. This may be direct.
    if assigned == False:
        label = row.touch_1
    return label


# In[110]:


aa_df_converted['last_nondirect_interaction_allocation'] = aa_df_converted.apply(last_nondirect_interaction,axis=1)


# In[111]:


last_nondirect_interaction_df = aa_df_converted.groupby('last_nondirect_interaction_allocation').agg({'convert_TF': 'count'})
last_nondirect_interaction_df = last_nondirect_interaction_df.join(total_spend_df)


# In[112]:


last_nondirect_interaction_df['CAC'] = last_nondirect_interaction_df['total_spend'] / last_nondirect_interaction_df['convert_TF']


# In[113]:


last_nondirect_interaction_df


# Once again, display is the channel with the cheapest CAC, followed by social and email, and then paid search and referral. For all 3 attribution model types, it seems like paid search and referral are the most expensive channel that yield few new customers, hence we should stop investing in them.

# # Part 2: Allocation
# 
# For one of the allocation methods, calculate the marginal CAC by spending tier by channel
# 
# - Discuss how your observations/conclusions from the previous section may change
# - This week we spent 1,500 total on advertising across all platforms. Next week we want to allocate the same budget in 50 increments, i.e. 700 spend on display adds, 50 spend on social ads, etc. Determine how you would most effectively allocate this budget.

# In[144]:


#Process Channel by Spend Data

tier_spend = channel_spend_df[channel_spend_df['tier'] != 'total']

tier_spend['spend by channel'] = tier_spend['spend by channel'].map(eval)


# In[145]:


tier_spend_df = pd.concat([tier_spend.drop(['spend by channel'], axis=1), tier_spend['spend by channel'].apply(pd.Series)], axis=1)


# In[235]:


tier_spend_df['tier'] = tier_spend_df['tier'].astype('int')


# In[236]:


tier_spend_df


# In[312]:


#Choose last non-direct interaction model

tier_count = aa_df_converted.groupby(['last_nondirect_interaction_allocation','tier']).agg({'convert_TF': 'count'})


# In[313]:


tier_count = tier_count.reset_index()


# In[334]:


def get_spend(row):
    channel = row.last_nondirect_interaction_allocation
    tier = row['tier']
    label = tier_spend_df[tier_spend_df['tier'] == tier][channel].item()
    return label


# In[315]:


tier_count['spend'] = tier_count.apply(get_spend,axis=1)


# In[316]:


#Drop free columns

tier_count_paid = tier_count[~tier_count['last_nondirect_interaction_allocation'].isin(['direct','organic_search'])]


# In[317]:


tier_count_paid['marginal_spend'] = 50


# In[337]:


def get_marginal(df):
    
    list_of_dataframes = []
    
    list_of_channels = df['last_nondirect_interaction_allocation'].unique()
    
    for channel in list_of_channels:
        
        #create new df for every channel
        channel_df = df[df['last_nondirect_interaction_allocation'] == channel]
        
        #Get calculations for every channel
        tier1_conv = channel_df[channel_df['tier'] == 1]['convert_TF'].item()
        tier2_conv = channel_df[channel_df['tier'] == 2]['convert_TF'].item() - channel_df[channel_df['tier'] == 1]['convert_TF'].item()
        tier3_conv = channel_df[channel_df['tier'] == 3]['convert_TF'].item() - channel_df[channel_df['tier'] == 2]['convert_TF'].item()

        channel_df.loc[:,'marginal_convert'] = [tier1_conv, tier2_conv,tier3_conv]

        channel_df['marginal_CAC'] = channel_df['marginal_spend'] / channel_df['marginal_convert']
        
        list_of_dataframes.append(channel_df)
    
    return list_of_dataframes


# In[325]:


marginal_cac_df = pd.concat(get_marginal(tier_count_paid))


# In[326]:


marginal_cac_df


# Display is still the cheapest channel for Tier 1 and 2 at 0.50. But beyond which the CAC becomes a lot higher, so it may not be worth it to spend that extra 50 on the last tier. 
# 
# Social is the next cheapest channel for Tier 1 and 2 for 0.60. However, beyond that it also goes up to 1.28.
# 
# Email is the next cheapest channel at 0.625, and 1, and for tier 3 it is worth it to invest because its only 0.58.
# 
# I would not receommend investing in paid search or referral anymore. CAC is too high.
# 
# Based on this, I would allocate:
# 1. 100 display
# 2. 100 social
# 3. 50 email
