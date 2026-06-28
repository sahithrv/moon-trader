from db.models import SymbolORM
from db.session import SessionLocal

def main():
    db = SessionLocal()

    try:
        symbols = db.query(SymbolORM).all()

        for symbol in symbols:
            print(symbol.id, symbol.symbol, symbol.name, symbol.asset_type, symbol.enabled)
    
    finally:
        db.close()

if __name__ == "__main__":
    main()