import StockHistory
import matplotlib.pylab as plt

if __name__ == "__main__":
    dt = StockHistory.get_namad_history(28864540805361867)
    dt['SimpleRateOfReturn'] = (dt["ClosePrice"] / dt["ClosePrice"].shift(1)) - 1
    dt['SimpleRateOfReturn'].plot(figsize=(15, 6))
    plt.show()
