import numpy as np


def baseline(HeartRateRanges: list, SpO2ranges: list, TemperatureRanges: list):
    #find the baseline value from list of ranges with standard deviation
    heartRateBaseline = round(float(np.mean(HeartRateRanges)), 2)
    spO2Baseline = round(float(np.mean(SpO2ranges)), 2)
    temperatureBaseline = round(float(np.mean(TemperatureRanges)), 2)

    HeartRateStandardDeviation = round(float(np.std(HeartRateRanges)), 2)
    spO2StandardDeviation = round(float(np.std(SpO2ranges)), 2)
    temperatureStandardDeviation = round(float(np.std(TemperatureRanges)), 2)


    return heartRateBaseline, spO2Baseline, temperatureBaseline, HeartRateStandardDeviation, spO2StandardDeviation, temperatureStandardDeviation

print(baseline([70, 72, 75, 80, 78], [95, 96, 97, 98, 99], [36.5, 36.7, 36.8, 37.0, 37.2]))