#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Feb 18 16:32:02 2020
@author: lalithsrinivas
"""

import pandas as pd

original_file = pd.read_csv('./database/zomato.csv', index_col=False)
all_columns = original_file.columns
rest_dict = {}
loc_table = pd.DataFrame()
loc_columns = ['location', 'listed_in(city)']

restaurant_table = pd.DataFrame()
restaurant_col = ['url', 'address', 'name', 'online_order', 'book_table', 'rate', 'votes', 'phone', 'location', 'rest_type', 'approx_cost(for two people)']
rate_list = []

dishes_table = pd.DataFrame()
dishes_list = []
dishes_col = ['dish_liked']

cuisines_table = pd.DataFrame()
cuisines_list = []
cuisines_col = ['cuisines']


rest_dish_links = pd.DataFrame()
rest_id_link1 = []
dish_id_link1 = []

rest_cuisine_links = pd.DataFrame()
rest_id_link2 = []
cuisine_id_link2 = []


user_loc_dict = {}

for i in all_columns:
    if i == 'approx_cost(for two people)':
        cost_col = []
        for j in original_file[i]:
            if not pd.isna(j):
                temp = j.split(',')
                temp_string = ""
                for k in temp:
                    temp_string = temp_string + k
                cost_col.append(temp_string)
            else:
                cost_col.append(-1)
        restaurant_table[i] = cost_col

    elif i == 'rate':
        for j in original_file[i]:
            if not (pd.isna(j) or j == 'NEW' or j=='-'):
                temp = j.split('/')
                rate_list.append(temp[0])
            else:
                rate_list.append('-1')
        restaurant_table[i] = rate_list
    elif i == 'location':
        restaurant_table[i] = original_file[i]
        loc_table[i] = original_file[i]
    elif i in loc_columns:
        for j in original_file[i]:
            if user_loc_dict.get(j) == None:
                user_loc_dict[j] = 1
        loc_table[i] = original_file[i]
    elif i in restaurant_col:
        restaurant_table[i] = original_file[i]
    elif i in cuisines_col:
        iter = 0
        for j in original_file[i]:
            if rest_dict.get(original_file['name'][iter]+original_file['address'][iter]) == None:
                if not pd.isna(j):
                    temp = j.split(', ')
                    for k in temp:
                        try:
                            index = cuisines_list.index(k)
                            rest_id_link2.append(iter)
                            cuisine_id_link2.append(index)
                        except:
                            cuisines_list.append(k)
                            rest_id_link2.append(iter)
                            cuisine_id_link2.append(len(cuisines_list) - 1)
                rest_dict[original_file['name'][iter]+original_file['address'][iter]] = 1
            iter = iter + 1


        cuisines_table[i] = cuisines_list
        rest_cuisine_links['restaurant_id'] = rest_id_link2
        rest_cuisine_links['cuisine_id'] = cuisine_id_link2
        rest_dict = {}
    elif i in dishes_col:
        iter=0
        for j in original_file[i]:
            if rest_dict.get(original_file['name'][iter]+original_file['address'][iter]) == None:
                if not pd.isna(j):
                    temp = j.split(', ')
                    for k in temp:
                        try:
                            index = dishes_list.index(k)
                            rest_id_link1.append(iter)
                            dish_id_link1.append(index)
                        except:
                            dishes_list.append(k)
                            rest_id_link1.append(iter)
                            dish_id_link1.append(len(dishes_list) - 1)
                rest_dict[original_file['name'][iter]+original_file['address'][iter]] = 1
            iter = iter + 1

        dishes_table['dish'] = dishes_list
        rest_dish_links['restaurant_id'] = rest_id_link1
        rest_dish_links['dish_id'] = dish_id_link1
        rest_dict = {}


users_file = pd.read_csv('./database/MOCKDATA.csv', index_col=False)
users_columns = users_file.columns
users_table = pd.DataFrame()

user_loc_list = list(user_loc_dict)
for i in users_columns:
    if i == 'location':
        city_list = []
        for j in users_file[i]:
            city_list.append(user_loc_list[j%(len(user_loc_list))])
        users_table[i] = city_list
    else:
        users_table[i] = users_file[i]



loc_table = loc_table.drop_duplicates(ignore_index = True)
restaurant_table = restaurant_table.drop_duplicates(subset=['address', 'name'])
cuisines_table = cuisines_table.drop_duplicates()
dishes_table = dishes_table.drop_duplicates()
rest_cuisine_links = rest_cuisine_links.drop_duplicates()
rest_dish_links = rest_dish_links.drop_duplicates()

users_table = users_table.drop_duplicates(subset = ['username'], ignore_index = True)


loc_table.to_csv('./database/location.csv', index_label='location_id')
restaurant_table.to_csv('./database/restaurant.csv', index_label='restaurant_id')
cuisines_table.to_csv('./database/cuisines.csv', index_label = 'cuisine_id')
dishes_table.to_csv('./database/dishes.csv', index_label='dish_id')
rest_cuisine_links.to_csv('./database/restaurant_cuisine_links.csv', index_label = 'link_id')
rest_dish_links.to_csv('./database/restaurant_dish_links.csv', index_label = 'link_id')


users_table.to_csv('./database/userdata.csv', index = False)
