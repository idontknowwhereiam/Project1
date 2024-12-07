from sqlalchemy import create_engine, MetaData, Table, select
import pandas as pd
from contextlib import contextmanager

@contextmanager
def get_connection(engine):
    connection = engine.connect()
    transaction = connection.begin()
    try:
        yield connection
        transaction.commit()
    except:
        transaction.rollback()
        raise
    finally:
        connection.close()

def add_new_countries(engine):
    with get_connection(engine) as conn:
        for country in new_countries:
            try:
                stmt = select([country_table.c.Code]).where(
                    country_table.c.Code == country["Code"])
                result = conn.execute(stmt).fetchone()
                
                if result is None:
                    conn.execute(country_table.insert().values(**country))
                    print(f"Inserted: {country['Name']} ({country['Code']})")
            except Exception as e:
                print(f"Error inserting {country['Code']}: {str(e)}")

def verify_and_print(engine):
    with get_connection(engine) as conn:
        query = select([
            country_table.c.Name.label("Country"),
            city_table.c.Name.label("City"),
            country_table.c.Region,
        ]).select_from(
            country_table.outerjoin(
                city_table, 
                country_table.c.Code == city_table.c.CountryCode
            )
        ).order_by(country_table.c.Name)
        
        df = pd.DataFrame(conn.execute(query).fetchall(), 
                         columns=["Country", "City", "Region"])
        df = df.fillna({'City': 'No city data'})
        return df

if __name__ == "__main__":
    engine = create_engine("sqlite:///world.sqlite")
    metadata = MetaData(bind=engine)
    metadata.reflect()
    
    country_table = metadata.tables["country"]
    city_table = metadata.tables["city"]
    
    add_new_countries(engine)
    result_df = verify_and_print(engine)
    print(result_df)
