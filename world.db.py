from sqlalchemy import create_engine, MetaData, Table, select
import pandas as pd
from contextlib import contextmanager

# Define new countries list
new_countries = [
    {
        "Code": "MTG", "Name": "Montenegro", "Continent": "Europe", "Region": "Southern Europe",
        "SurfaceArea": 13812.0, "IndepYear": 2006, "Population": 622359, "LifeExpectancy": 77.5,
        "GNP": 4867.0, "GNPOld": None, "LocalName": "Crna Gora", "GovernmentForm": "Republic",
        "HeadOfState": "Jakov Milatović", "Capital": "Podgorica", "Code2": "ME"
    },
    {
        "Code": "BHR", "Name": "Bahrain", "Continent": "Asia", "Region": "Middle East",
        "SurfaceArea": 760.0, "IndepYear": 1971, "Population": 1701575, "LifeExpectancy": 76.9,
        "GNP": 36820.0, "GNPOld": None, "LocalName": "Al-Bahrain", "GovernmentForm": "Monarchy",
        "HeadOfState": "Salman bin Hamad", "Capital": "Manama", "Code2": "BH"
    },
    {
        "Code": "SRB", "Name": "Serbia", "Continent": "Europe", "Region": "Southern Europe",
        "SurfaceArea": 88361.0, "IndepYear": 2006, "Population": 6982084, "LifeExpectancy": 75.2,
        "GNP": 51755.0, "GNPOld": None, "LocalName": "Srbija", "GovernmentForm": "Republic",
        "HeadOfState": "Aleksandar Vučić", "Capital": "Belgrade", "Code2": "RS"
    },
    {
        "Code": "TLS", "Name": "East Timor", "Continent": "Asia", "Region": "Southeast Asia",
        "SurfaceArea": 14874.0, "IndepYear": 2002, "Population": 1296311, "LifeExpectancy": 67.8,
        "GNP": 2027.0, "GNPOld": None, "LocalName": "Timor-Leste", "GovernmentForm": "Republic",
        "HeadOfState": "José Ramos-Horta", "Capital": "Dili", "Code2": "TL"
    },
    {
        "Code": "PLW", "Name": "Palau", "Continent": "Oceania", "Region": "Micronesia",
        "SurfaceArea": 459.0, "IndepYear": 1994, "Population": 18092, "LifeExpectancy": 72.3,
        "GNP": 268.0, "GNPOld": None, "LocalName": "Belau", "GovernmentForm": "Republic",
        "HeadOfState": "Surangel Whipps Jr.", "Capital": "Ngerulmud", "Code2": "PW"
    }
]

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
