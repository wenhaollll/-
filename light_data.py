import pymysql
import time
import random
from datetime import datetime
import os
import sys

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
import solar_calc

DB_CONFIG = {
    'host': '8.137.33.218',
    'port': 3306,
    'user': 'hardware',
    'password': 'Hardware@2024',
    'database': 'solor',
    'charset': 'utf8mb4'
}

DEVICE_ID = 'CTGU-Light-001'
DEVICE_NAME = 'CTGU-Smart-Light'
DEVICE_AREA = 'CQ-Wz'
LONGITUDE = 108.4325
LATITUDE = 30.8697

def ensure_device_exists():
    conn = None
    try:
        conn = pymysql.connect(**DB_CONFIG)
        with conn.cursor() as cursor:
            cursor.execute("SELECT COUNT(*) FROM lamps WHERE light_id = %s", (DEVICE_ID,))
            if cursor.fetchone()[0] == 0:
                sql = """
                INSERT INTO lamps (
                    light_id, byname, area, x, y, 
                    status, lamp_status, mode, location_time, deleted
                ) VALUES (%s, %s, %s, %s, %s, 1, 0, 1, NOW(), 0)
                """
                cursor.execute(sql, (DEVICE_ID, DEVICE_NAME, DEVICE_AREA, LONGITUDE, LATITUDE))
                conn.commit()
                print(f"new shebei: {DEVICE_ID}")
            else:
                print(f"have shebei: {DEVICE_ID}")
        return True
    except Exception as e:
        print(f"chushihua failed: {e}")
        return False
    finally:
        if conn:
            conn.close()

def upload_data():
    conn = None
    try:
        real_height, real_azimuth = solar_calc.get_current_sun_position()
        mock_battery = random.randint(80, 100)

        print(f"real sun -> high:{real_height:.2f}, fanwei:{real_azimuth:.2f}, power:{mock_battery}")

        conn = pymysql.connect(**DB_CONFIG)
        with conn.cursor() as cursor:
            sql = """
            UPDATE lamps SET
                status = 1,
                battray_pack_one_charge = %s,
                current_high_angel = %s,
                current_direction_angel = %s,
                location_time = NOW(),
                duration = '1.5'
            WHERE light_id = %s
            """
            rows_affected = cursor.execute(sql, (
                str(mock_battery),
                str(real_height),
                str(real_azimuth),
                DEVICE_ID
            ))

            if rows_affected == 0:
                print("shebei no set")
                return False

        conn.commit()
        print("data up successed")
        return True

    except Exception as e:
        print(f"data up failed: {e}")
        return False
    finally:
        if conn:
            conn.close()
            
if __name__ == '__main__':
    print("=" * 50)
    print("Smart Light - Environment Data Uploader")
    print("=" * 50)

    if not ensure_device_exists():
        print("chushihua failed")
        exit(1)

    print("\nstart data up every 1 hour (Ctrl+C to stop)...")
    print("-" * 50)

    count = 0
    try:
        while True:
            count += 1
            print(f"\n[ {count} ] time: {datetime.now().strftime('%H:%M:%S')}")
            upload_data()
            time.sleep(3600)
    except KeyboardInterrupt:
        print("\nstop")

