from database import database_connect, dictfetchall
from flask import *

import pg8000
import configparser
import sys

'''
Adds aircraft to the table 
'''
def add_aircraft(aircraft_id, icao_code, aircraft_registration, manufacturer, model, capacity):
    if aircraft_exists(aircraft_id):
        print(f"Error: fail to add aircraft. {aircraft_id} already exists")
        flash(f"Error: Aircraft with ID {aircraft_id} already exists.", "error")
        return
    if (int(aircraft_id) < 0):
        flash(f"Error: Aircraft ID {aircraft_id} cannot be negative.", "error")
        return
    try:
        conn = database_connect()
        cursor = conn.cursor()
        
        cursor.execute(
            """
            INSERT INTO Aircraft (AircraftID, ICAOCode, AircraftRegistration, Manufacturer, Model, Capacity)
            VALUES (%s, %s, %s, %s, %s, %s)
            """,
            (aircraft_id, icao_code, aircraft_registration, manufacturer, model, capacity)
        )
        
        conn.commit()
        print("Aircraft added successfully.")
        
    except Exception as e:
        print(f"Error: fail to add aircraft {aircraft_id} + {e}")
        conn.rollback()
    finally:
        cursor.close()
        conn.close()

'''
Remove an aircraft by id 
'''
def remove_aircraft(aircraft_id):
    if not aircraft_exists(aircraft_id):
        print(f"Error: fail to remove aircraft. {aircraft_id} does not exist")
        return
    try:
        conn = database_connect()
        cursor = conn.cursor()
        
        cursor.execute(
            "DELETE FROM Aircraft WHERE AircraftID = %s", 
            (aircraft_id,)
        )
        
        conn.commit()
        print("Aircraft removed successfully.")
        
    except Exception as e:  
        print(f"Error: fail to remove aircraft {aircraft_id}. Exception: {e}")
        conn.rollback()
    finally:
        cursor.close()
        conn.close()

'''
Edits an existing aircraft with a given id 
'''
def modify_aircraft(aircraft_id, icao_code=None, aircraft_registration=None, manufacturer=None, model=None, capacity=None):
    print("modifying aircraft")
    if not aircraft_exists(aircraft_id):
        print(f"Error: fail to modify aircraft. {aircraft_id} does not exist")
        return

    try:
        conn = database_connect()
        cursor = conn.cursor()

        update_fields = []
        update_values = []

        if icao_code and icao_code.strip():
            update_fields.append("ICAOCode = %s")
            update_values.append(icao_code)
        
        if aircraft_registration and aircraft_registration.strip():
            update_fields.append("AircraftRegistration = %s")
            update_values.append(aircraft_registration)
        
        if manufacturer and manufacturer.strip():
            update_fields.append("Manufacturer = %s")
            update_values.append(manufacturer)
        
        if model and model.strip():
            update_fields.append("Model = %s")
            update_values.append(model)
        
        if capacity and capacity.strip(): 
            update_fields.append("Capacity = %s")
            update_values.append(capacity)

        if not update_fields:
            print("Error: No fields provided to update.")
            return

        update_values.append(aircraft_id)

        sql = f"UPDATE Aircraft SET {', '.join(update_fields)} WHERE AircraftID = %s"
        
        cursor.execute(sql, tuple(update_values))
        
        conn.commit()
        print("Aircraft updated successfully.")

    except:
        print(f"Error: Failed to update aircraft due to {aircraft_id}")
        conn.rollback() 
    
    finally:
        cursor.close()
        conn.close()


'''
Gets a list of manufacturers
'''
def get_unique_manufacturers():
    manufacturers = [] 
    conn = None
    cursor = None

    try:
        conn = database_connect()
        cursor = conn.cursor()
        
        cursor.execute(
            "SELECT DISTINCT Manufacturer FROM Aircraft"
        )
        
        manufacturers = cursor.fetchall()
        manufacturers = [manufacturer[0] for manufacturer in manufacturers]
        
    except Exception as e:
        manufacturers = [] 
        print(f"Error: fail to get manufacturers: {e}")
    finally:
        cursor.close()
        conn.close()

    return manufacturers

'''
Get number of aircraft manufactured by each manufacturer
'''
def get_aircraft_count_by_manufacturer():
    counts = [] 
    conn = None
    cursor = None

    try:
        conn = database_connect() 
        cursor = conn.cursor()
        
        cursor.execute(
            """
            SELECT Manufacturer, COUNT(*) AS AircraftCount 
            FROM Aircraft 
            GROUP BY Manufacturer 
            ORDER BY AircraftCount DESC
            """
        )
        
        results = cursor.fetchall() 

        if results:
            for manufacturer, count in results:
                counts.append((manufacturer, count))
        
    except Exception as e:
        print(f"Error: failed to get aircraft counts: {e}")
        counts = [] 
        
    finally:
        cursor.close()
        conn.close() 
    
    return counts  

'''
lists all aircrafts in database
'''
def list_aircrafts():
    conn = database_connect()
    if conn is None:
        return None
    
    cur = conn.cursor()
    returndict = None

    try:
        sql = """SELECT *
                   FROM Aircraft"""
        
        returndict = dictfetchall(cur, sql)

    except:
        import traceback
        traceback.print_exc()
        print("Error: fail to get aircrafts from database", sys.exc_info()[0])

    cur.close()
    conn.close()

    return returndict

'''
Gets aircraft details by aircraft ID
'''
def get_aircraft_by_id(aircraft_id):
    aircraft = None
    try:
        conn = database_connect()
        cursor = conn.cursor()
        
        cursor.execute(
            "SELECT * FROM Aircraft WHERE AircraftID = %s", 
            (aircraft_id,)
        )
        
        aircraft = cursor.fetchone()
        
        if aircraft:
            aircraft = {
                "AircraftID": aircraft[0],
                "ICAOCode": aircraft[1],
                "AircraftRegistration": aircraft[2],
                "Manufacturer": aircraft[3],
                "Model": aircraft[4],
                "Capacity": aircraft[5]
            }
        else:
            print(f"Error: Aircraft with ID {aircraft_id} does not exist.")
        
    except Exception as e:
        print(f"Error: failed to get aircraft by ID {e}")
    finally:
        cursor.close()
        conn.close()

    print("AIRCRAFT WITH ID: ", aircraft)
    return aircraft

'''
checks if an aircraft ID exists in the table
'''
def aircraft_exists(aircraft_id):
    try:
        conn = database_connect()
        cursor = conn.cursor()
        
        cursor.execute(
            "SELECT COUNT(*) FROM Aircraft WHERE AircraftID = %s", 
            (aircraft_id,)
        )
        
        count = cursor.fetchone()[0]
        
        if count > 0:
            return True
        else:
            return False
        
    except Exception as e:
        print(f"Error: fail to check aircraft ID {e}")
        return False
    finally:
        cursor.close()
        conn.close()

