import os
os.makedirs('../Database', exist_ok=True)

def insert_data(date, time, license_plate_number, vehicle_type, violation_type, latitude, longitude, street_name):
    try:
        with open('../Database/violations_detected.csv', 'a') as file:
            file.write(f"{date},{time},{license_plate_number},{vehicle_type},{violation_type},{latitude},{longitude},{street_name}\n")
            print('Data inserted')

    except Exception as e:
        print(f"Error: {e}")

