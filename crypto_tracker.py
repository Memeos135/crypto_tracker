import requests
import json
import pyodbc
import time
import subprocess
import os
import datetime
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import pyautogui
from random import randrange

def discordWebHook(file_path, coin, text):
	url = "discord_webhook_url"

	payload={'payload_json': '{"content": ' + text + '}'}
	files=[
	  ('file_1',('55hvdovz3uq31.jpg',open(file_path,'rb'),'image/jpeg'))
	]
	headers = {
	}

	response = requests.request("POST", url, headers=headers, data=payload, files=files)

def insertDataIntoTBL(id,   symbol, name,   current_price,  market_cap, market_cap_rank,    fully_diluted_valuation,    total_volume,   high_24h,   low_24h,    price_change_24h,   price_change_percentage_24h,    market_cap_change_24h,  market_cap_change_percentage_24h,   circulating_supply, total_supply,   max_supply, ath,    ath_change_percentage,  ath_date,   atl,    atl_change_percentage,  atl_date,   roi,    last_updated,   price_change_percentage_1h_in_currency, price_change_percentage_24h_in_currency,    price_change_percentage_7d_in_currency):
	try:
		cnxn = pyodbc.connect('DRIVER={ODBC Driver 17 for SQL Server};SERVER=server_name\\SQLEXPRESS;DATABASE=tempdb;UID=sa;PWD=connection_password')
		cursor = cnxn.cursor()
		query_string = f'''INSERT INTO [tempdb].[dbo].[tbl_test] (id,   symbol, name,   current_price,  market_cap, market_cap_rank,    fully_diluted_valuation,    total_volume,   high_24h,   low_24h,    price_change_24h,   price_change_percentage_24h,    market_cap_change_24h,  market_cap_change_percentage_24h,   circulating_supply, total_supply,   max_supply, ath,    ath_change_percentage,  ath_date,   atl,    atl_change_percentage,  atl_date,   roi,    last_updated,   price_change_percentage_1h_in_currency, price_change_percentage_24h_in_currency,    price_change_percentage_7d_in_currency) VALUES ('{id}', '{symbol}', '{name}', {current_price},  {market_cap},   {market_cap_rank},  '{fully_diluted_valuation}',    {total_volume}, {high_24h}, {low_24h},  {price_change_24h}, {price_change_percentage_24h},  {market_cap_change_24h},    {market_cap_change_percentage_24h}, {circulating_supply},   '{total_supply}',   '{max_supply}', {ath},  {ath_change_percentage},    '{ath_date}',   {atl},  {atl_change_percentage},    '{atl_date}',   '{roi}',    '{last_updated}',   {price_change_percentage_1h_in_currency},   {price_change_percentage_24h_in_currency},  {price_change_percentage_7d_in_currency})'''
		cursor.execute(query_string)
		cnxn.commit()
		cnxn.close()
	except Exception as e:
		pass
		# print(query_string,"\n\n\n\n", id, " - ERROR \n\n", e, "\n\n --------------------------------------------")

def testCoinGeckoAPIFunc():
	first_url = "https://api.coingecko.com/api/v3/coins/markets?vs_currency=usd&order=market_cap_desc&per_page=250&page=1&sparkline=false&price_change_percentage=1h%2C24h%2C7d"
	second_url = 'https://api.coingecko.com/api/v3/coins/markets?vs_currency=usd&order=market_cap_desc&per_page=250&page=2&sparkline=false&price_change_percentage=1h%2C24h%2C7d'

	response_first_obj = requests.get(first_url)
	response_second_obj = requests.get(second_url)

	response_first_obj = json.loads(response_first_obj.text)
	response_second_obj = json.loads(response_second_obj.text)

	coin_merged_list = response_first_obj + response_second_obj

	return coin_merged_list


def computeRSI (data, time_window):
	diff = data.diff(1).dropna()        # diff in one field(one day)

	#this preservers dimensions off diff values
	up_chg = 0 * diff
	down_chg = 0 * diff
	
	# up change is equal to the positive difference, otherwise equal to zero
	up_chg[diff > 0] = diff[ diff>0 ]
	
	# down change is equal to negative deifference, otherwise equal to zero
	down_chg[diff < 0] = diff[ diff < 0 ]
	
	# check pandas documentation for ewm
	# https://pandas.pydata.org/pandas-docs/stable/reference/api/pandas.DataFrame.ewm.html
	# values are related to exponential decay
	# we set com=time_window-1 so we get decay alpha=1/time_window
	up_chg_avg   = up_chg.ewm(com=time_window-1 , min_periods=time_window).mean()
	down_chg_avg = down_chg.ewm(com=time_window-1 , min_periods=time_window).mean()
	
	rs = abs(up_chg_avg/down_chg_avg)
	rsi = 100 - 100/(1+rs)
	return rsi

def stochastic(data, k_window, d_window, window):
	
	# input to function is one column from df
	# containing closing price or whatever value we want to extract K and D from
	
	min_val  = data.rolling(window=window, center=False).min()
	max_val = data.rolling(window=window, center=False).max()
	
	stoch = ( (data - min_val) / (max_val - min_val) ) * 100
	
	K = stoch.rolling(window=k_window, center=False).mean() 
	#K = stoch
	
	D = K.rolling(window=d_window, center=False).mean() 


	return K, D


def screenshotPlot(price_list, stoch_k, stoch_d, coin, text):
	global file_path
	global file_name

	# DELETE PREVIOUS FILES
	if file_path:
		os.remove(file_path)

	y_axis = np.array(price_list['price'])
	x_axis = np.array(price_list['date'])
	z_axis = np.array(price_list['volume'])

	# CREATE EMA LISTS (13, 20, 50, 200)
	df_test = pd.DataFrame(price_list['price'])
	ema_20 = df_test.ewm(span=20).mean()
	ema_25 = df_test.ewm(span=25).mean()
	ema_30 = df_test.ewm(span=30).mean()
	ema_35 = df_test.ewm(span=35).mean()
	ema_40 = df_test.ewm(span=40).mean()
	ema_45 = df_test.ewm(span=45).mean()
	ema_50 = df_test.ewm(span=50).mean()

	# CREATE SUBPLOT FRAME
	figure, axis = plt.subplots(3, figsize=(25,10))
	plt.subplots_adjust(wspace=0, hspace=0)

	manager = plt.get_current_fig_manager()
	manager.full_screen_toggle()

	# PLOT PRICE AND EMA CHART
	axis[0].plot(x_axis, y_axis, label='PRICE')
	axis[0].plot(x_axis, ema_20, label='EMA_20')
	axis[0].plot(x_axis, ema_25, label='EMA_25')
	axis[0].plot(x_axis, ema_30, label='EMA_30')
	axis[0].plot(x_axis, ema_35, label='EMA_35')
	axis[0].plot(x_axis, ema_40, label='EMA_40')
	axis[0].plot(x_axis, ema_45, label='EMA_45')
	axis[0].plot(x_axis, ema_50, label='EMA_50')
	axis[0].legend(loc='right', bbox_to_anchor=(1.1, 0.5),ncol=1)
	axis[0].set_title(text)

	# COLOR VOLUME BARS
	last_index = 0
	colors = []
	for i in z_axis:
		if i == 0 or i > last_index:
			colors.append('green')
			last_index = i
		else:
			colors.append('red')
			last_index = i

	# PLOT VOLUME CHART
	axis[1].bar(x_axis, z_axis, color=colors, label='VOLUME')
	axis[1].legend(loc='right', bbox_to_anchor=(1.1, 0.5),ncol=1)

	axis[2].plot(np.delete(x_axis, 0), stoch_k, label='STOCH_K_RSI_14')
	axis[2].plot(np.delete(x_axis, 0), stoch_d, label='STOCH_D_RSI_14')
	axis[2].axhline(30, linestyle='--')
	axis[2].axhline(70, linestyle='--')
	axis[2].legend(loc='right', bbox_to_anchor=(1.1, 0.5),ncol=1)

	# FILL RSI AREA WITH COLOR
	plt.fill_between(x_axis, 30, 70, color='green', alpha='0.1')

	# SET GRID FOR ALL SUBPLOTS
	axis[0].grid()
	axis[1].grid()
	axis[2].grid()

	axis[0].margins(0.05)

	plt.show(block=False)
	plt.pause(2)
	myScreenshot = pyautogui.screenshot()

	rand = str(randrange(0,1000))
	file_name = coin+rand+'.PNG'
	file_path = r'.\file_name_'+coin+rand+'.PNG'

	myScreenshot.save(file_path)
	plt.close()

	# RUN OTHER PYTHON FILE WITH ARGS
	discordWebHook(file_path, coin, text)

def prepareData():
	query_string = "SELECT * FROM tempdb.dbo.TBL_TEST WHERE MARKET_CAP > 250000000 AND (name NOT LIKE '%USD%' AND name NOT LIKE '%Dollar%' AND name NOT LIKE '%dollar%') AND symbol NOT IN ('usdt', 'busd') AND price_change_percentage_1h_in_currency > 0 ORDER BY MARKET_CAP DESC"
	cursor.execute(query_string)

	result = cursor.fetchall()

	for i in result:

		coin = str(i[1]).upper()
		url = "https://api.coingecko.com/api/v3/coins/"+i[0]+"/market_chart?vs_currency=usd&days=365"
		response = requests.get(url)
		data = json.loads(response.text)

		price_list = {"price": [], "date": [], "volume": [], "13_ema": [], "20_ema": [], "50_ema": [], "200_ema": []}

		# GET PRICES AND THEIR CORRESPONDENT DATES
		for i in data['prices']:
			price_list['price'].append(i[1])
			date = datetime.datetime.fromtimestamp(i[0]/1000)
			price_list['date'].append(date)

		# GET VOLUMES AND THEIR CORRESPONDENT DATES
		for i in data['total_volumes']:
			price_list['volume'].append(i[1])


		# COMPUTE RSI AND STOCHASTIC RSI DATA
		rsi_data = computeRSI(pd.DataFrame(price_list['price']), 14)
		stoch_k = []
		stoch_d = []
		stoch_k, stoch_d = stochastic(rsi_data, 3, 3, 14)

		# FILTER DATA FROM DATAFRAME
		stoch_k_d_diff = stoch_k - stoch_d
		stoch_k_d_diff_last = (stoch_k_d_diff[-1:])[0].values[0]
		stoch_k_last = (stoch_k[-1:])[0].values[0]

		# CHECK IF STOCH_K - STOCH_D LIES BETWEEN 0 & 5 RANGE
		stoch_k_d_diff_last_zone = 0 < stoch_k_d_diff_last < 5
		
		# CHECK IF GOLDEN ZONE
		if stoch_k_d_diff_last_zone and stoch_k_last <= 60:
			text = "POTENTIAL BUY - {" + coin + "} STOCH_RSI_DIFF = [" + str(stoch_k_d_diff_last_zone) + " (" + str(stoch_k_d_diff_last) + ") " + "], STOCH_RSI_K = [" + str(stoch_k_last) + "]"
			print(text)
			screenshotPlot(price_list, stoch_k, stoch_d, coin, text)
		else:
			text = "BAD BUY - {" + coin + "} STOCH_RSI_DIFF = [" + str(stoch_k_d_diff_last_zone) + " (" + str(stoch_k_d_diff_last) + ") " + "], STOCH_RSI_K = [" + str(stoch_k_last) + "]"
			print(text)
			time.sleep(2)

# --------------------------------------------------------------------------------------------------------------------------------

pid_list = []
file_name = ''
file_path = ''

while 1:    

	# OPEN DATABASE CONNECTION
	cnxn = pyodbc.connect('DRIVER={ODBC Driver 17 for SQL Server};SERVER=server_name\\SQLEXPRESS;DATABASE=tempdb;UID=sa;PWD=connection_password')
	cursor = cnxn.cursor()

	# REMOVE HISTORICAL DATA FROM DATABASE
	try:
		query_string = "DELETE FROM [tempdb].[dbo].[tbl_test]"
		cursor.execute(query_string)
		cnxn.commit()
	except Exception as e:
		pass

	# FETCH COINGECKO COIN DATA
	coin_list = testCoinGeckoAPIFunc()


	# INSERT COINGECKO COIN DATA INTO DATABASE
	for i in coin_list:
		insertDataIntoTBL(i['id'],  i['symbol'],    i['name'],  i['current_price'], i['market_cap'],    i['market_cap_rank'],   i['fully_diluted_valuation'],   i['total_volume'],  i['high_24h'],  i['low_24h'],   i['price_change_24h'],  i['price_change_percentage_24h'],   i['market_cap_change_24h'], i['market_cap_change_percentage_24h'],  i['circulating_supply'],    i['total_supply'],  i['max_supply'],    i['ath'],   i['ath_change_percentage'], i['ath_date'],  i['atl'],   i['atl_change_percentage'], i['atl_date'],  "NULL", i['last_updated'],  i['price_change_percentage_1h_in_currency'],    i['price_change_percentage_24h_in_currency'],   i['price_change_percentage_7d_in_currency'])

	# FETCH COIN PRICE DATA AND COMPUTE POTENTIAL BUYS
	prepareData()
	cursor = cnxn.cursor()
	time.sleep(1800)
