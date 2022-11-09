# Using Dynamic Time Warping as Indicator to Predict Future Stock Movements

## Project Overview
Use Dynamic Time Warping (DTW) to compare n (day) sized stock signals to historical signals of the same size to try and predict the next Day stock movement. The closer the signals match a historical signal, the lower the cost to dynamically warp the signal. Future stock predictions were on the scale of whether they will be overall positive or negative. This script does not go into price predicting.

## Motivation
I wanted to test if matching past signals to current stock signals can be used to accurately predict next day profitability. 

## Dynamic Time Warping
DTW is an algorithm used to measure similarity between two signals which may vary in speed. These signals are warped non-linearly to determine a measure of their similarity independent of certain non-linear variations in the time dimension. 
<br> This method is commonly used for gait analysis and speech recognition.

## Code Overview
1. Pull historical data for inputted ticker and S&P 500
2. Divide historical data into signals we want to predict next day for vs signals we want to compare the prediction to
3. Take one prediction signal of size n and compare to compare signals of size n, moving signal n+win_move for each new comparison
4. If cost to dynamically time warp is less than a threshold value, collect:
- Average cost to dynamically time warp the prediction signal to compare signal
- Next day percent up after compare signal
- Next day percent up after prediction signal (actual precent up)
5. Evaluate predicted data based on:
- If average next day from historical is positive
- If average next day S&P from historical is positive
6. Evaluate profitability

## Dyanimc Time Warping Function
#### For each signal window
Signal is converted to percent change from first day closing price.
<br> One is the signal we are trying to predict the next day for
<br> Other is the historical signal we are currently comparing the prediction signal to.
<br> Both are the same window size or same number of days.
<br>
#### Both Signals are inputted into DTW function
<br> Dynamic time warping will get cost to move a single point to all other points on compare signal. 
<br> Each cell relates to distance between these points in the two signals combined. 
<br>
#### A cost matrix and least cost path is outputted
<br> Once a matrix is created the path of least cost between point (0,0) and (n,m) where n is the length of prediction signal array and m is the length of compare signal array. In this case it is the least cost path between (0,0) and (20,20).
<br> Signals will be moved n points over and comparison will be repeated until there are no more signals in historical data.
<br>

## Input Parameter Testing
#### Input Parameters Overview
stock_list - stock list
<br> win_size - window size
<br> win_move - window step size
<br> cost_compare_value - cost value we have to be below in order to save data and justify correlated signals
<br> train_perc - percentage of data allocated to training data or historic data we compare against
<br> start_date - start date we pull stock data from

#### Window Size
Tested window size 20-90 by steps of 10.
<br> Tested on 'AAPL'
|win size|profit|win perc|
|--------|------|--------|
|20|\-\$52|51.12%|
|30|\$77|54.09%|
|40|\-\$51|51.72%|
|50|\$89|60.60%|
|60|\$75|58.06%|
|70|\-\$27|51.55%|
|80|\-\$119|51.00%|
|90|\$63|57.58%|

#### Cost Compare Value
Tested cost compare value 0.1-2.0 with -0.1 step size to see value with best returns.
<br> Tested on 'AAPL'
|costCompareVal|profit|winPerc|
|--------------|------|-------|
|0.1|\-\$82|54.10%|
|0.2|\-\$13|49.35%|
|0.3|\-\$35|49.35%|
|0.4|\-\$47|52.56%|
|0.5|\$89|60.60%|
|0.6|\$40|53.33%|
|0.7|\-\$54|47.05%|
|0.8|\$6|48.61%|
|0.9|\$13|52.50%|
|1.0|\$44|53.84%|
|1.1|\$45|52.08%|
|1.2|\$33|53.46%|
|1.3|\$50|55.44%|
|1.4|\$75|54.20%|
|1.5|\$51|54.05%|
|1.6|\-\$35|51.75%|
|1.7|\$61|54.31%|
|1.8|\-\$1|52.99%|
|1.9|\-\$78|51.64%|
|2.0|\-\$43|52.76%|

## Conclusion
#### Results
Tested parameters:
<br> buy amount per trade = \$1000
<br> cost compare value = 0.5
<br> start date = 2018-01-01
<br> train data = 80%
<br> window size = 50
<br> ticker list = 12 companies from S&P
|Ticker|profit|winPerc|totalGuess|totalCorrect|
|------|------|-------|----------|------------|
|TSLA|\$40|42.85%|7|3|
|AAPL|\$10|53.22%|62|33|
|AMZN|\$23|100.00%|1|1|
|META|\$97|68.42%|19|13|
|GOOGL|\-\$69|44.90%|49|22|
|NVDA|\$1|53.33%|15|18|
|V|\$5|66.67%|3|2|
|MA|\$25.14|50.00%|4|2|
|HD|\$25|49.31%|7|3|
|PEP|\$52|51.51%|99|51|
|COST|\-\$9|49.31%|73|36|

|Total Profit|
|------------|
|\$111.11|

#### Last Thoughts
With the current backtesting setup, this does not look to be a profitable strategy. 