from db.models import SymbolORM
from db.session import SessionLocal

def main():
    db = SessionLocal()

    try: 
        symbols = [
            SymbolORM(symbol="AAPL", name="Apple Inc.", asset_type="stock", exchange="NASDAQ"),
            SymbolORM(symbol="MSFT", name="Microsoft Corporation", asset_type="stock", exchange="NASDAQ"),
            SymbolORM(symbol="NVDA", name="NVIDIA Corporation", asset_type="stock", exchange="NASDAQ"),
        ]

        db.add_all(symbols)
        db.commit()
        print("DB seeded.")
    finally:
        db.close()

if __name__ == "__main__":
    main()