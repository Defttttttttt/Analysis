import numpy as np

def fft(x):
    """
    实现FFT算法，输入x为时域信号序列
    """
    n = len(x)
    if n == 1:
        return x
    else:
        # 计算偶数项和奇数项分别进行FFT
        even = fft(x[0::2])
        odd = fft(x[1::2])
        # 合并结果
        t = np.exp(-2j * np.pi * np.arange(n) / n)
        return np.concatenate([even + t[:n // 2] * odd, even + t[n // 2:] * odd])

# 示例
x = [0, 1, 2, 3, 4, 5, 6, 7]
y = fft(x)
print(y)

import numpy as np

def dft(x):
    """
    实现DFT算法，输入x为时域信号序列
    """
    n = len(x)
    output = []
    for k in range(n):
        s = 0
        for m in range(n):
            s += x[m] * np.exp(-2j * np.pi * k * m / n)
        output.append(s)
    return output

# 示例
x = [0, 1, 2, 3, 4, 5, 6, 7]
y = dft(x)
print(y)
