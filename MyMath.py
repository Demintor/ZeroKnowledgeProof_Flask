import random

# Тест Миллера-Рабина
def isPrime(n, k=100):
    if n < 2: return False
    for p in [2, 3, 5, 7, 11, 13, 17, 19, 23, 29]:
        if n % p == 0: 
            return n == p
    s, d = 0, n - 1
    while d % 2 == 0:
        s, d = s + 1, d / 2
    for i in range(k):
        x = pow(random.randint(2, n - 1), int(d), n)
        if x == 1 or x == n - 1: 
            continue
        for r in range(1, s):
            x = (x * x) % n
            if x == 1: 
                return False
            if x == n - 1: 
                break
        else: 
            return False
    return True

# НОД, с помощью алгоритма Евклида
def NOD(a, b): 
    while a != 0 and b != 0:
        if a > b:
            a %= b
        else:
            b %= a
    gcd = a + b  
    return (gcd)

# Функция Эйлера для произведения двух простых чисел
def euler(p, q):
    return ((p - 1) * (q - 1))

# Расширенный алгоритм Евклида
def bezout(a, b):
    oldB = b
    x, xx, y, yy = 1, 0, 0, 1
    while b:
        q = a // b
        a, b = b, a % b
        x, xx = xx, x - xx*q
        y, yy = yy, y - yy*q
    if(x < 0):
        x = x + oldB
    return (x)


