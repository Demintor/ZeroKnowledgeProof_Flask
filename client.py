from flask import Flask, jsonify, request
from flask_cors import CORS
import random
from dataclasses import dataclass
import math
import hashlib
from sympy.ntheory import randprime, isprime
from sympy.ntheory.primetest import mr


from MyMath import *

app = Flask(__name__)
CORS(app)

#-------------------Протокол Фиата-Шамира----------------------------------
# Запрос для клиента, генерация пароля (для регистрации)
@app.route('/FiatShamir/client/GenerationKey',  methods=['GET'])
def FiatShamirGenerationKey():
    # Генерируем два простых числа и вычисляем их произведение
    p = randprime(2 ** 139, 2 ** 140)
    q = randprime(2 ** 139, 2 ** 140)      
    n = p * q
    # Выбираем s, взаимно-простое с mod, и вычисляем V
    s = random.randint(1, n)
    while(NOD(s, n) != 1):
        s = s + 1
    v = pow(s, 2, n)   
    return jsonify({"n": str(n), "s": str(s), "v": str(v)})

# Запрос для клиента, строит массивы x, y
@app.route('/FiatShamir/client/CreateAuthData',  methods=['POST'])
def FiatShamirCreateAuthData():
    """
        Нужно передать модуль системы, массив битов и кол-во итераций аккредитации
        Если считать, что это доверенный центр, 
            и данные не могут быть перехвачены - то еще передаем секретный ключ,
            иначе формируем массив Y на стороне клиента 
    """
    # Извлекаем данные
    data = request.get_json()
    n = int(data.get('n'))
    size = int(data.get('size'))
    bits = [int(bit) for bit in (data.get('bits'))]
    s = int(data.get('s'))
    # Строим массивы x и y
    X = []
    Y = []
    for i in range(size):       
        r = random.randint(1, (n-1))
        X.append(pow(r, 2, n))        
        if (bits[i] == 0):
            Y.append(r)
        if (bits[i] == 1):
            Y.append((r * s) % n)        
    outX = [str(x) for x in (X)]
    outY = [str(y) for y in (Y)]
    return jsonify({"X": outX,"Y": outY})

# Запрос для сервера, генерирует массив битов, 
# должен принять кол-во итераций аккредитации
@app.route('/FiatShamir/server/GenerationBits', methods=['POST'])
def FiatShamirGenerationBits():
    # Извлекаем данные
    data = request.get_json()
    size = int(data.get('size'))
    #Генерируем массив битов
    bits = []
    for i in range(size):
        bit = random.randint(0, 1)
        bits.append(bit)   
    return jsonify({"bits": bits})

# Запрос для сервера, проводит аккредитацию, 
# должен принять n, size, bits, X, Y, v
@app.route('/FiatShamir/server/Check', methods=['POST'])
def Check():
    # Извлекаем данные
    data = request.get_json()
    n = int(data.get('n'))
    size = int(data.get('size'))
    bits = [int(bit) for bit in (data.get('bits'))]
    X = [int(x) for x in (data.get('X'))]
    Y = [int(x) for x in (data.get('Y'))]
    v = int(data.get('v'))
    # Проводим аккредитацию
    error = False
    for i in range(size):
        if (bits[i] == 0 and pow(Y[i], 2, n) != X[i] % n):
            error = True
        if (bits[i] == 1 and pow(Y[i], 2, n) != (X[i] * v) % n):
            error = True   
    return jsonify({"result": error})
#-------------------------------------------------------------------

#----------------------Протокол Гиллу-Кискатра--------------------------------
# Запрос для клиента, генерирует ключи, 
# должен принять строку атрибутов (имя, логин, почта,....)
@app.route('/GuillouQuisquater/client/GenerationKey',  methods=['POST'])
def GuillouQuisquaterGenerationKey():
    # Вытаскиваем данные из json
    data = request.get_json()
    attr = str(data.get('attr'))
    # Генерируем простые p и q из диапазона
    p = randprime(2 ** 139, 2 ** 140)
    q = randprime(2 ** 139, 2 ** 140)
    # Вычисляем произведение
    n = p * q
    # Вычисляем функцию эйлера для n
    f = euler(p,q)
    # Вычисляем e из [1, fn], взаимно простое с fn
    e = random.randint(1, f)  
    while(NOD(e, f) != 1):
        e = e + 1
    # Вычисляем s
    s = bezout(e,f) 
    att = bytes(attr, 'utf-8')
    hashAttr = hashlib.sha1(att)
    J = int(hashAttr.hexdigest(), 16)
    # Вычисляем закрытый ключ x и y
    x = pow(bezout(J, n), s, n)
    y = pow(x, e, n)
    return jsonify({"n": str(n), "e": str(e), "y": str(y), "x": str(x)})

# Запрос для клиента, строит данные для аутентификации (значения a и z)
# должен принять n, e, x, c
@app.route('/GuillouQuisquater/client/CreateAuthData',  methods=['POST'])
def GuillouQuisquaterCreateAuthData():
    # Вытаскиваем данные из json
    data = request.get_json()
    n = int(data.get('n'))
    e = int(data.get('e'))
    x = int(data.get('x'))
    c = int(data.get('c'))
    # Вычисляем a и z
    r = random.randint(1, n - 1)
    a = pow(r, e, n)
    z = (r * pow(x, c, n)) % n
    return jsonify({"a": str(a), "z": str(z)})

# Запрос для сервера, генерирует с из [0, e - 1]
# Должен принять значение e
@app.route('/GuillouQuisquater/server/GenerationValue',  methods=['POST'])
def GuillouQuisquaterGenerationValue():
    # Вытаскиваем данные из json
    data = request.get_json()
    e = int(data.get('e'))
    # Генерируем c
    c = random.randint(0, e - 1)
    return jsonify({"c": str(c)})

# Запрос для сервера, выполняет аккредитацию,
# должен принять z, e, a, y, c, n
# проверяет, что z^e = a * y^c (mod n)
@app.route('/GuillouQuisquater/server/check',  methods=['POST'])
def GuillouQuisquaterCheck():
    # Вытаскиваем данные из json
    data = request.get_json()
    z = int(data.get('z'))
    e = int(data.get('e'))
    a = int(data.get('a'))
    y = int(data.get('y'))
    c = int(data.get('c'))
    n = int(data.get('n'))
    # Проверка
    error = False
    c1 = pow(z, e, n)
    c2 = (a * pow(y, c, n)) % n
    if(c1 != c2):
        error = True
    return jsonify({"result": error})
#-----------------------------------------------------------------------------

#------------------------Схема-Шнорра------------------------------------------
# Запрос для клиента, генерирует ключи
@app.route('/Schnorr/client/GenerationKey',  methods=['GET'])
def SchnorrGenerationKey():
    # Генерируем простое число из диапазона
    q = randprime(2 ** 139, 2 ** 140)
    # Генерируем целое число
    rand = random.randint(2 ** 371, 2 ** 372)
    # Произведение
    testP = q * rand
    # Пока testP+1 не станет простым, генерируем заново и считаем произведение
    # в итоге получим, что простое q - делитель p - 1, а p - простое
    while(mr(testP + 1, [31, 72]) == False):
        q = randprime(2 ** 139, 2 ** 140)
        rand = random.randint(2 ** 371, 2 ** 372)
        testP = q * rand   
    p = testP + 1
    # Ищем g, мультипликативный порядок по модулю p которого равен q (g^q = (1 mod p))
    h = random.randint(1, p - 1)
    g = pow (h, (p - 1) // q, p)
    while(g == 1):
        h = random.randint(1, p - 1)
        g = pow (h, (p - 1) // q, p)
    # Вычисляем параметры w и y
    w = random.randint(0, q - 1)
    y = pow(bezout(g, p), w, p)
    return jsonify({"p": str(p), "q": str(q), "g": str(g), "y": str(y), "w": str(w)})

# Запрос для клиента, строит данные для аутентификации (значения x и s)
# Должен принять p, q, g, w, e
@app.route('/Schnorr/client/CreateAuthData',  methods=['POST'])
def SchnorrCreateAuthData():
    # Вытаскиваем данные из json
    data = request.get_json()
    p = int(data.get('p'))
    q = int(data.get('q'))
    g = int(data.get('g'))
    w = int(data.get('w'))
    e = int(data.get('e'))
    # Строим значение x и s
    r = random.randint(0, q - 1)
    x = pow(g, r, p)
    s = (r + w * e) % q
    return jsonify({"x": str(x), "s": str(s)})

# Запрос для сервера, генерирует значение e из [0, 2^t - 1]
@app.route('/Schnorr/server/GenerationValue',  methods=['GET'])
def SchnorrGenerationValue():
    # Устанавливаем константу в 72 и генерируем e из [0, 2^72 - 1]
    t = 72
    e = random.randint(0, 2 ** t - 1)
    return jsonify({"e": str(e)})

# Запрос для сервера, запрашивает проверку
# Должен принять x, g, s, y, e, p
# Проверяет, что x = g^s * y^e (mod p)
@app.route('/Schnorr/server/check',  methods=['POST'])
def SchnorrCheck():
    # Вытаскиваем данные из json
    data = request.get_json()
    x = int(data.get('x'))
    g = int(data.get('g'))
    s = int(data.get('s'))
    y = int(data.get('y'))
    e = int(data.get('e'))
    p = int(data.get('p'))
    # Проверка
    error = False
    c1 = x % p
    c2 = (pow(g, s, p) * pow(y, e, p)) % p
    if(c1 != c2):
        error = True
    return jsonify({"result": error})
#-------------------------------------------------------------------------------
if __name__ == '__main__':
    app.run(debug=True)

#set FLASK_APP=hello.py
#python -m flask run