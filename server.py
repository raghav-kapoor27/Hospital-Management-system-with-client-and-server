import mysql.connector
import socket
import json
import threading
from datetime import datetime

DATE_FORMAT = "%Y-%m-%d"

def get_db_connection():
    return mysql.connector.connect(
        host="localhost", 
        user="root", 
        password="",
        database="hospital_doctor_patients_record", 
        charset='utf8'
    )

def parse_date_value(value, field_name):
    if value is None:
        raise ValueError(f"{field_name} is required.")

    value = str(value).strip()
    if not value:
        raise ValueError(f"{field_name} is required.")

    try:
        return datetime.strptime(value, DATE_FORMAT).date()
    except ValueError as exc:
        raise ValueError(f"{field_name} must be a valid date in YYYY-MM-DD format.") from exc

def init_database():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("CREATE TABLE IF NOT EXISTS doctors_record "
                   "(DOCTOR_ID INT(5) PRIMARY KEY, DOCTOR_NAME VARCHAR(255), "
                   "DOCTOR_SPECIALITY VARCHAR(255), DATE_BIRTH DATE)")
    cursor.execute("CREATE TABLE IF NOT EXISTS patients_record "
                   "(patient_ID INT(10) AUTO_INCREMENT PRIMARY KEY, patient_name VARCHAR(255), "
                   "father_name VARCHAR(255), mother_name VARCHAR(255), past_history VARCHAR(255), "
                   "patient_complaint VARCHAR(255), date_of_arrival DATE, doctor_code INT(5), "
                   "parent_history VARCHAR(255), doctor_name VARCHAR(255))")
    cursor.execute("CREATE TABLE IF NOT EXISTS doctor_patient_record "
                   "(DOCTOR_ID INT(5), PATIENT_ID INT(10), "
                   "STATUS VARCHAR(255), ADMIT VARCHAR(255), MEDICINE_PRESCRIBED VARCHAR(255), "
                   "ADVICE VARCHAR(255), "
                   "FOREIGN KEY (DOCTOR_ID) REFERENCES doctors_record(DOCTOR_ID), "
                   "FOREIGN KEY (PATIENT_ID) REFERENCES patients_record(patient_ID))")
    conn.close()
def handle_request(data):
    cursor = None
    conn = None
    try:
        request = json.loads(data)
        operation = request.get('operation')
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        if operation == 'insert_doctor':
            doctor_id = request['doctor_id']
            doctor_name = request['doctor_name']
            speciality = request['speciality']
            dob = parse_date_value(request['dob'], "Date of Birth")
            
            cursor.execute("INSERT INTO doctors_record "
                          "(DOCTOR_ID, DOCTOR_NAME, DOCTOR_SPECIALITY, DATE_BIRTH) "
                          "VALUES (%s, %s, %s, %s)",
                          (doctor_id, doctor_name, speciality, dob))
            conn.commit()
            return {"status": "success", "message": f"Doctor '{doctor_name}' added successfully!"}
        
        elif operation == 'get_doctor':
            doctor_name = request['doctor_name']
            cursor.execute("SELECT * FROM doctors_record WHERE doctor_name = %s", (doctor_name,))
            result = cursor.fetchall()
            
            if result:
                doctors = []
                for row in result:
                    doctors.append({"id": row[0], "name": row[1], "speciality": row[2], "dob": str(row[3])})
                return {"status": "success", "data": doctors}
            else:
                return {"status": "error", "message": f"No doctor found with name '{doctor_name}'"}
        
        elif operation == 'delete_doctor':
            doctor_name = request['doctor_name']
            cursor.execute("DELETE FROM doctors_record WHERE doctor_name = %s", (doctor_name,))
            conn.commit()
            return {"status": "success", "message": f"Doctor '{doctor_name}' deleted!"}
        
        elif operation == 'update_doctor':
            doctor_name = request['doctor_name']
            field = request['field']
            value = request['value']
            
            valid_fields = ["DOCTOR_NAME", "DOCTOR_SPECIALITY", "DATE_BIRTH"]
            if field not in valid_fields:
                return {"status": "error", "message": "Invalid field"}
            if field == "DATE_BIRTH":
                value = parse_date_value(value, "Date of Birth")
            
            cursor.execute(f"UPDATE doctors_record SET {field} = %s WHERE DOCTOR_NAME = %s",
                          (value, doctor_name))
            conn.commit()
            return {"status": "success", "message": f"Doctor updated!"}
        
        elif operation == 'insert_patient':
            arrival_date = parse_date_value(request['date'], "Date of Arrival")
            cursor.execute("INSERT INTO patients_record "
                          "(patient_name, father_name, mother_name, past_history, "
                          "patient_complaint, date_of_arrival, doctor_code, parent_history, doctor_name) "
                          "VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)",
                          (request['name'], request['father'], request['mother'], 
                           request['history'], request['complaint'], arrival_date,
                           request['doctor_id'], request['parent_history'], request['doctor_name']))
            conn.commit()
            return {"status": "success", "message": f"Patient '{request['name']}' registered!"}
        
        elif operation == 'get_patient':
            patient_name = request['patient_name']
            cursor.execute("SELECT * FROM patients_record WHERE patient_name = %s", (patient_name,))
            result = cursor.fetchall()
            
            if result:
                patients = []
                for row in result:
                    patients.append({
                        "id": row[0], "name": row[1], "father": row[2], "mother": row[3],
                        "history": row[4], "complaint": row[5], "date": str(row[6]),
                        "doctor_id": row[7], "doctor_name": row[9]
                    })
                return {"status": "success", "data": patients}
            else:
                return {"status": "error", "message": f"No patient found with name '{patient_name}'"}
        
        elif operation == 'delete_patient':
            patient_name = request['patient_name']
            cursor.execute("DELETE FROM patients_record WHERE patient_name = %s", (patient_name,))
            conn.commit()
            return {"status": "success", "message": f"Patient '{patient_name}' deleted!"}
        
        elif operation == 'update_patient':
            patient_name = request['patient_name']
            field = request['field']
            value = request['value']
            
            valid_fields = ["patient_name", "father_name", "mother_name", "past_history",
                          "patient_complaint", "date_of_arrival", "doctor_code", 
                          "parent_history", "doctor_name"]
            if field not in valid_fields:
                return {"status": "error", "message": "Invalid field"}
            if field == "date_of_arrival":
                value = parse_date_value(value, "Date of Arrival")
            
            cursor.execute(f"UPDATE patients_record SET {field} = %s WHERE patient_name = %s",
                          (value, patient_name))
            conn.commit()
            return {"status": "success", "message": "Patient updated!"}
        
        elif operation == 'insert_link':
            cursor.execute("INSERT INTO doctor_patient_record "
                          "(DOCTOR_ID, PATIENT_ID, STATUS, ADMIT, MEDICINE_PRESCRIBED, ADVICE) "
                          "VALUES (%s, %s, %s, %s, %s, %s)",
                          (request['doctor_id'], request['patient_id'], request['status'],
                           request['admit'], request['medicine'], request['advice']))
            conn.commit()
            return {"status": "success", "message": "Doctor-Patient link created!"}
        
        elif operation == 'get_link':
            doctor_id = request['doctor_id']
            patient_id = request['patient_id']
            cursor.execute("SELECT * FROM doctor_patient_record WHERE DOCTOR_ID = %s AND PATIENT_ID = %s",
                          (doctor_id, patient_id))
            result = cursor.fetchall()
            
            if result:
                return {"status": "success", "data": {"status": result[0][2], "admit": result[0][3],
                                                      "medicine": result[0][4], "advice": result[0][5]}}
            else:
                return {"status": "error", "message": "No record found"}
        
        elif operation == 'delete_link':
            cursor.execute("DELETE FROM doctor_patient_record WHERE DOCTOR_ID = %s AND PATIENT_ID = %s",
                          (request['doctor_id'], request['patient_id']))
            conn.commit()
            return {"status": "success", "message": "Link deleted!"}
        
        elif operation == 'update_link':
            doctor_id = request['doctor_id']
            patient_id = request['patient_id']
            field = request['field']
            value = request['value']
            
            valid_fields = ["STATUS", "ADMIT", "MEDICINE_PRESCRIBED", "ADVICE"]
            if field not in valid_fields:
                return {"status": "error", "message": "Invalid field"}
            
            cursor.execute(f"UPDATE doctor_patient_record SET {field} = %s "
                          "WHERE DOCTOR_ID = %s AND PATIENT_ID = %s",
                          (value, doctor_id, patient_id))
            conn.commit()
            return {"status": "success", "message": "Link updated!"}
        
        else:
            return {"status": "error", "message": "Unknown operation"}
    
    except Exception as e:
        return {"status": "error", "message": str(e)}
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

def client_handler(client_socket, address):
    print(f"\nClient connected from {address[0]}:{address[1]}")
    try:
        while True:
            data = client_socket.recv(4096).decode('utf-8')
            if not data:
                break
            
            response = handle_request(data)
            client_socket.send(json.dumps(response).encode('utf-8'))
    
    except Exception as e:
        print(f"Error: {e}")
    finally:
        client_socket.close()
        print(f"Client disconnected from {address[0]}:{address[1]}")

def start_server():
    print("\n" + "="*70)
    print("SR HOSPITAL - SERVER (Database Handler)")
    print("="*70 + "\n")
    
    init_database()
    print("Database initialized\n")
    
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind(('0.0.0.0', 9999))
    server.listen(5)
    
    print("Server started on PORT 9999")
    print("Waiting for client connections...\n")
    
    try:
        while True:
            client_socket, address = server.accept()
            thread = threading.Thread(target=client_handler, args=(client_socket, address))
            thread.daemon = True
            thread.start()
    except KeyboardInterrupt:
        print("\n\nServer shutting down...")
    finally:
        server.close()

if __name__ == "__main__":
    start_server()
