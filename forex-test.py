import sys
import datetime
import time

from forex_python.converter import CurrencyRates


if __name__ == "__main__":
    c = CurrencyRates()


    # 아무 파라미터가 없을 경우 현재 달러/원 환율을 보여줍니다
    if len(sys.argv) == 2: 
        result = round(c.convert('USD', 'KRW', 1), 2)
        print(f'{result} 원')
    # 가격 없이 order가 'l'이면 환율흐름을 보여줍니다
    #elif len(sys.argv) == 3:  # 5가 아니어도 그냥 order값만 있는 것으로 판단하기로 합니다
    elif len(sys.argv) == 3 and sys.argv[2] == 'l':  
        today = datetime.date.today()
        results = []
        for i in range(0,7):
            #l = dates.append(today - datetime.timedelta(days=i))
            #print('\033[10C', end='')
            print(f'\rfetching {i+1}...', end='')
            time.sleep(0.01)
            d = today - datetime.timedelta(days=i)
            results.append(round(c.convert('USD', 'KRW', 1, d), 2))
        print(f'\r Completed           ')
        #print('')
        for result in results:
            print(f'{result} 원')

    else:
        try:
            order = int(sys.argv[1])
            price = int(sys.argv[2])
            #result = c.get_rate('USD', 'KRW')
            # 달러를 원으로 변환합니다
            if order == 0: 
                result = c.convert('USD', 'KRW', int(price))
                result = round(float(result), 2)
                print(f'{result} 원')
            else: 
                result = c.convert('KRW', 'USD',int(price))
                result = round(float(result), 2)
                print(f'{result} dollars')

        except:
            print(f'error occurred')

#c.convert('
