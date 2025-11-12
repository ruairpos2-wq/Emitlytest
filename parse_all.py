from parse_rbc import main as parse_rbc_main
from parse_telegram import main as parse_telegram_main

def main():
    print("Starting news parsing...")
    
    print("\n1. Parsing RBC news...")
    parse_rbc_main()
    
    print("\n2. Parsing Telegram channel...")
    parse_telegram_main()
    
    print("\nParsing completed!")

if __name__ == '__main__':
    main()
