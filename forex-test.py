
import sys

from forex_python.converter import CurrencyRates



if __name__ == "__main__":
    c = CurrencyRates()

    # 가격이 없을 경우 현재 달러/원 환율을 보여줍니다
    if len(sys.argv) == 2: 
        result = round(c.convert('USD', 'KRW', 1), 2)
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
