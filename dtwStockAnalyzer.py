import yfinance as yf
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from dtw import *
from tqdm import tqdm
        
class Utils():
    
    def pullStockData(ticker=str, start_date=0):
        
        print(f"Downloading data for ticker: {ticker}")

        if start_date==0:
            raw_stock_df = yf.download(ticker,index=0)
        else:
            raw_stock_df = yf.download(ticker,index=0,start=start_date)

        if raw_stock_df.empty:
            print(f"Unable to get data for ticker: {ticker}")
            return 0

        return raw_stock_df.reset_index(drop=False)
    
    def matchDfLen(snp_df, stock_df):
        
        if len(snp_df.index) == len(stock_df.index):
            return snp_df, stock_df   
        
        max_index = snp_df.loc[snp_df["Date"] == stock_df["Date"].iat[-1]].index
        min_index = snp_df.loc[snp_df["Date"] == stock_df["Date"].iat[0]].index
        
        if(len(min_index) == 0):
            min_index = stock_df.loc[stock_df["Date"] == snp_df["Date"].iat[0]].index
            max_index = stock_df.loc[stock_df["Date"] == snp_df["Date"].iat[-1]].index
            
            stock_df = stock_df[min_index.values[0]:max_index.values[0]].reset_index(drop=True)
        
        else:
            snp_df = snp_df[min_index.values[0]:max_index.values[0]].reset_index(drop=True)
            
        return snp_df, stock_df
    
    def splitData(stock_df, train_perc):
        
        df = stock_df
        training_data = df[int(len(df)*(1-train_perc)):]
        prediction_data = df[0:int(len(df)*(1-train_perc))]

        training_data = training_data.reset_index()
        prediction_data = prediction_data.reset_index()

        return training_data, prediction_data
  
    def zeroData(signal):
        return signal/signal[0]

    
class DtwAnalysis():
    def __init__(self, win_size=int, win_move=int, 
                 cost_compare=float, train_perc=float, buy_amount=float,
                 start_date=0):
        
        self.prediction_dict = {
            "avgCost":[],
            "avgNextDay":[],"avgSnpNextDay":[],"actNextDay":[]
        }
        
        self.win_size = win_size
        self.win_move = win_move
        self.cost_compare_value = cost_compare
        self.train_perc = train_perc
        self.start_date = start_date
        self.buy_amount = buy_amount
        
    def getRollingAnalysis(base_params, stock_past_data, raw_snp_df, base_signal):
        
        dtw_dict = {
            "indexStart":[],"indexEnd":[],"totalCost":[],
            "nextDay":[],"snpNextDay":[]
        }
        
        for j in range(0,int(len(stock_past_data)-2*base_params.win_size),base_params.win_move):
            compare_signal = Utils.zeroData(np.array(stock_past_data["Open"][j:j+base_params.win_size]))
            
            #Get DTW Values
            cost_matrix, path = DtwAnalysis.getDtw(base_signal, compare_signal)

            sumPath = DtwAnalysis.getSumPath(cost_matrix, path)
    
            if (sumPath < base_params.cost_compare_value):
                dtw_dict["indexStart"].append(j)
                dtw_dict["indexEnd"].append(j+base_params.win_size)
                dtw_dict["totalCost"].append(sumPath)
                dtw_dict["nextDay"].append(1-(stock_past_data["Open"][j+base_params.win_size+1]/stock_past_data["Close"][j+base_params.win_size+1]))
                dtw_dict["snpNextDay"].append(1-(raw_snp_df["Open"][j+base_params.win_size+1]/raw_snp_df["Close"][j+base_params.win_size+1]))
            
        return pd.DataFrame.from_dict(dtw_dict)
                
                
                
    def getDtw(base_signal, compare_signal):
        norm_12 = lambda base_signal, compare_signal:(base_signal-compare_signal)**2
        dist,cost_matrix,acc_cost_matrix,path = dtw(base_signal,compare_signal,norm_12)
        
        return cost_matrix, path
    
    def getSumPath(cost_matrix, path):
        sumPath = 0
        for i in range(len(path[0])):
            sumPath = sumPath+cost_matrix[path[0][i]][path[1][i]]
            
        return sumPath  
    
    def refineResults(act_next_day, prediction_df, analyzed_dtw_df):
        df = analyzed_dtw_df
        
        prediction_df["avgCost"].append(sum(df["totalCost"])/len(df["totalCost"]))
        prediction_df["avgNextDay"].append(sum(df["nextDay"])/len(df["nextDay"]))
        prediction_df["avgSnpNextDay"].append(sum(df["snpNextDay"])/len(df["snpNextDay"]))
        prediction_df["actNextDay"].append(float(1-(act_next_day["Open"]/act_next_day["Close"])))
        
        return prediction_df
    
    def formResults(base_params, ticker, final_results):
        df = pd.DataFrame.from_dict(base_params.prediction_dict)
        
        profit = 0
        total_guesses = 0
        sum_of_correct = 0
        buy_amount = base_params.buy_amount
        
        for i in range(len(df)):
            if df["avgNextDay"][i]>=0 and df["avgSnpNextDay"][i]>=0:
                profit = profit+buy_amount*df["actNextDay"][i]
                total_guesses+=1
                if df["actNextDay"][i] > 0:
                    sum_of_correct+=1
        if total_guesses == 0 or sum_of_correct == 0:
            win_perc = 0
        else:
            win_perc = sum_of_correct/total_guesses
            
        final_results["ticker"].append(ticker)
        final_results["profit"].append(profit)
        final_results["winPerc"].append(win_perc)
        final_results["totalGuesses"].append(total_guesses)
        final_results["sumOfCorrect"].append(sum_of_correct)
        
        return final_results
        
    def printResults(df):
        print(f"{df}")
                   

if  __name__ == "__main__":
    
    # Setup base parameters and stock list
    stock_list = [
        'AMZN',
        'TSLA',
        'META',
        'WDC'
    ]
    final_results = {
        "ticker":[], "profit":[], "winPerc":[],
        "totalGuesses":[], "sumOfCorrect":[]
    }
    base_params = DtwAnalysis(50,1,0.5,0.80,1000,'2018-01-01')
    # Download S&P data to use in analysis
    raw_snp_df = Utils.pullStockData('SPY',base_params.start_date)
    
    for i in range(0, len(stock_list)):
        try:
            # pull raw stock df from stock_list[i] ticker
            raw_stock_df = Utils.pullStockData(stock_list[i],base_params.start_date)
            
            if base_params.start_date == 0:
                # make sure S&P and stock data are within same date range
                raw_snp_df, raw_stock_df = Utils.matchDfLen(raw_snp_df, raw_stock_df)

            # Split data into signals we want to compare and signals we want to compare against
            stock_past_data, stock_predict_data = Utils.splitData(raw_stock_df, base_params.train_perc)

            for k in tqdm(range(0,len(stock_predict_data)-base_params.win_size-1,base_params.win_move)):
                # Collect a base signal we will compare to past signals
                base_signal = Utils.zeroData(np.array(stock_predict_data["Open"][k:k+base_params.win_size]))

                analyzed_dtw_df = DtwAnalysis.getRollingAnalysis(base_params, stock_past_data, raw_snp_df, base_signal)

                act_next_day = stock_predict_data.iloc[base_params.win_size+k]

                base_params.prediction_dict = DtwAnalysis.refineResults(act_next_day, base_params.prediction_dict, analyzed_dtw_df)

            final_results = DtwAnalysis.formResults(base_params,stock_list[i],final_results)
            
            
        except:
            print(f"Unable to perform analysis for ticker: {ticker}\n")
            print(f"Moving to next ticker\n")
            pass

    DtwAnalysis.printResults(pd.DataFrame.from_dict(final_results))
    