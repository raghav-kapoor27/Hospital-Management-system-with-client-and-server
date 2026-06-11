import socket
import json
from datetime import datetime

DATE_FORMAT = "%Y-%m-%d"

class HospitalClient:
    def __init__(self, server_ip, server_port=9999):
        self.server_ip = server_ip
        self.server_port = server_port
        self.socket = None
    
    def connect(self):
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.connect((self.server_ip, self.server_port))
            print(f"\nConnected to server at {self.server_ip}:{self.server_port}\n")
            return True
        except Exception as e:
            print(f"\nFailed to connect to server: {e}\n")
            return False
    
    def send_request(self, request):
        try:
            self.socket.send(json.dumps(request).encode('utf-8'))
            response = self.socket.recv(4096).decode('utf-8')
            return json.loads(response)
        except Exception as e:
            print(f"Error: {e}")
            return {"status": "error", "message": str(e)}
    
    def close(self):
        if self.socket:
            self.socket.close()

def print_header(title):
    print("\n" + "="*70)
    print(f"  {title}")
    print("="*70 + "\n")

def print_section(title):
    print(f"\n{title}")
    print("-" * 40)

def normalize_date_input(value, field_name):
    value = value.strip()
    if not value:
        raise ValueError(f"{field_name} is required.")

    try:
        return datetime.strptime(value, DATE_FORMAT).date().isoformat()
    except ValueError as exc:
        raise ValueError(f"{field_name} must be a valid date in YYYY-MM-DD format.") from exc

def format_input_error(error):
    message = str(error).strip()
    if "invalid literal for int()" in message:
        return "Numeric fields must contain numbers."
    return message or "Invalid input!"

def main():
    print("\n" + "="*70)
    print("SR HOSPITAL - CLIENT (Patient/Doctor Management)")
    print("="*70 + "\n")
    
    server_ip = "10.121.122.13"
    print(f"Connecting to Server at {server_ip}...")
    
    client = HospitalClient(server_ip)
    
    if not client.connect():
        return
    
    try:
        while True:
            print("\nMain Menu:")
            print("  1️⃣  Doctor Management")
            print("  2️⃣  Patient Management")
            print("  3️⃣  Doctor-Patient Linkage")
            print("  4️⃣  Exit\n")
            
            choice = input("Select option (1/2/3/4): ").strip()
            
            if choice == '1':
                doctor_menu(client)
            elif choice == '2':
                patient_menu(client)
            elif choice == '3':
                linkage_menu(client)
            elif choice == '4':
                print("\nExiting...\n")
                break
            else:
                print("\nInvalid option!")
    
    finally:
        client.close()

def doctor_menu(client):
    while True:
        print_header("DOCTOR MANAGEMENT")
        print("Available Operations:")
        print("  1️⃣  Add Doctor")
        print("  2️⃣  Search Doctor")
        print("  3️⃣  Delete Doctor")
        print("  4️⃣  Update Doctor")
        print("  5️⃣  Back to Main Menu\n")
        
        choice = input("Select operation (1/2/3/4/5): ").strip()
        
        if choice == '1':
            print_section("ADD NEW DOCTOR")
            try:
                doctor_id = int(input("Doctor ID: "))
                doctor_name = input("Doctor Name: ")
                speciality = input("Speciality: ")
                dob = normalize_date_input(input("Date of Birth (YYYY-MM-DD): "), "Date of Birth")
                
                request = {
                    'operation': 'insert_doctor',
                    'doctor_id': doctor_id,
                    'doctor_name': doctor_name,
                    'speciality': speciality,
                    'dob': dob
                }
                
                response = client.send_request(request)
                if response['status'] == 'success':
                    print(f"\n{response['message']}\n")
                else:
                    print(f"\n{response['message']}\n")
            except ValueError as error:
                print(f"\n{format_input_error(error)}\n")
        
        elif choice == '2':
            print_section("SEARCH DOCTOR")
            doctor_name = input("Enter Doctor Name: ")
            
            request = {'operation': 'get_doctor', 'doctor_name': doctor_name}
            response = client.send_request(request)
            
            if response['status'] == 'success':
                print("\nDOCTOR RECORDS:\n")
                for doc in response['data']:
                    print(f"ID: {doc['id']} | Name: {doc['name']}")
                    print(f"Speciality: {doc['speciality']} | DOB: {doc['dob']}\n")
            else:
                print(f"\n{response['message']}\n")
        
        elif choice == '3':
            print_section("DELETE DOCTOR")
            doctor_name = input("Enter Doctor Name to delete: ")
            
            confirm = input("Are you sure? (Y/N): ").strip().upper()
            if confirm == 'Y':
                request = {'operation': 'delete_doctor', 'doctor_name': doctor_name}
                response = client.send_request(request)
                print(f"\n{response['message']}\n")
            else:
                print("\nCancelled\n")
        
        elif choice == '4':
            print_section("UPDATE DOCTOR")
            doctor_name = input("Enter Doctor Name to update: ")
            print("\nUpdatable Fields: DOCTOR_NAME, DOCTOR_SPECIALITY, DATE_BIRTH")
            field = input("Field to update: ").strip().upper()
            value = input("New value: ")
            if field == "DATE_BIRTH":
                try:
                    value = normalize_date_input(value, "Date of Birth")
                except ValueError as error:
                    print(f"\n{error}\n")
                    continue
            
            request = {
                'operation': 'update_doctor',
                'doctor_name': doctor_name,
                'field': field,
                'value': value
            }
            
            response = client.send_request(request)
            if response['status'] == 'success':
                print(f"\n{response['message']}\n")
            else:
                print(f"\n{response['message']}\n")
        
        elif choice == '5':
            break
        else:
            print("\nInvalid option!\n")

def patient_menu(client):
    while True:
        print_header("PATIENT MANAGEMENT")
        print("Available Operations:")
        print("  1️⃣  Add Patient")
        print("  2️⃣  Search Patient")
        print("  3️⃣  Delete Patient")
        print("  4️⃣  Update Patient")
        print("  5️⃣  Back to Main Menu\n")
        
        choice = input("Select operation (1/2/3/4/5): ").strip()
        
        if choice == '1':
            print_section("ADD NEW PATIENT")
            try:
                patient_name = input("Patient Name: ")
                father_name = input("Father Name: ")
                mother_name = input("Mother Name: ")
                history = input("Medical History: ")
                complaint = input("Current Complaint: ")
                date = normalize_date_input(input("Date of Arrival (YYYY-MM-DD): "), "Date of Arrival")
                doctor_id = int(input("Assigned Doctor ID: "))
                parent_history = input("Family History: ")
                doctor_name = input("Assigned Doctor Name: ")
                
                request = {
                    'operation': 'insert_patient',
                    'name': patient_name,
                    'father': father_name,
                    'mother': mother_name,
                    'history': history,
                    'complaint': complaint,
                    'date': date,
                    'doctor_id': doctor_id,
                    'parent_history': parent_history,
                    'doctor_name': doctor_name
                }
                
                response = client.send_request(request)
                if response['status'] == 'success':
                    print(f"\n{response['message']}\n")
                else:
                    print(f"\n{response['message']}\n")
            except ValueError as error:
                print(f"\n{format_input_error(error)}\n")
        
        elif choice == '2':
            print_section("SEARCH PATIENT")
            patient_name = input("Enter Patient Name: ")
            
            request = {'operation': 'get_patient', 'patient_name': patient_name}
            response = client.send_request(request)
            
            if response['status'] == 'success':
                print("\nPATIENT RECORDS:\n")
                for patient in response['data']:
                    print(f"ID: {patient['id']} | Name: {patient['name']}")
                    print(f"Father: {patient['father']} | Mother: {patient['mother']}")
                    print(f"Complaint: {patient['complaint']} | Doctor: {patient['doctor_name']}\n")
            else:
                print(f"\n{response['message']}\n")
        
        elif choice == '3':
            print_section("DELETE PATIENT")
            patient_name = input("Enter Patient Name to delete: ")
            
            confirm = input("Are you sure? (Y/N): ").strip().upper()
            if confirm == 'Y':
                request = {'operation': 'delete_patient', 'patient_name': patient_name}
                response = client.send_request(request)
                print(f"\n{response['message']}\n")
            else:
                print("\nCancelled\n")
        
        elif choice == '4':
            print_section("UPDATE PATIENT")
            patient_name = input("Enter Patient Name to update: ")
            print("\nUpdatable Fields:")
            print("  • patient_name, father_name, mother_name")
            print("  • past_history, patient_complaint, date_of_arrival")
            print("  • doctor_code, parent_history, doctor_name\n")
            field = input("Field to update: ").strip().lower()
            value = input("New value: ")
            if field == "date_of_arrival":
                try:
                    value = normalize_date_input(value, "Date of Arrival")
                except ValueError as error:
                    print(f"\n{error}\n")
                    continue
            
            request = {
                'operation': 'update_patient',
                'patient_name': patient_name,
                'field': field,
                'value': value
            }
            
            response = client.send_request(request)
            if response['status'] == 'success':
                print(f"\n{response['message']}\n")
            else:
                print(f"\n{response['message']}\n")
        
        elif choice == '5':
            break
        else:
            print("\nInvalid option!\n")

def linkage_menu(client):
    while True:
        print_header("DOCTOR-PATIENT LINKAGE")
        print("Available Operations:")
        print("  1️⃣  Create Link (with treatment)")
        print("  2️⃣  View Treatment Records")
        print("  3️⃣  Delete Link")
        print("  4️⃣  Update Treatment Info")
        print("  5️⃣  Back to Main Menu\n")
        
        choice = input("Select operation (1/2/3/4/5): ").strip()
        
        if choice == '1':
            print_section("CREATE DOCTOR-PATIENT LINK")
            try:
                doctor_id = int(input("Doctor ID: "))
                patient_id = int(input("Patient ID: "))
                status = input("Patient Status: ")
                admit = input("Admission Status: ")
                medicine = input("Medicines Prescribed: ")
                advice = input("Medical Advice: ")
                
                request = {
                    'operation': 'insert_link',
                    'doctor_id': doctor_id,
                    'patient_id': patient_id,
                    'status': status,
                    'admit': admit,
                    'medicine': medicine,
                    'advice': advice
                }
                
                response = client.send_request(request)
                if response['status'] == 'success':
                    print(f"\n{response['message']}\n")
                else:
                    print(f"\n{response['message']}\n")
            except ValueError:
                print("\nInvalid input!\n")
        
        elif choice == '2':
            print_section("VIEW TREATMENT RECORDS")
            try:
                doctor_id = int(input("Doctor ID: "))
                patient_id = int(input("Patient ID: "))
                
                request = {
                    'operation': 'get_link',
                    'doctor_id': doctor_id,
                    'patient_id': patient_id
                }
                
                response = client.send_request(request)
                if response['status'] == 'success':
                    data = response['data']
                    print("\nTREATMENT RECORDS:\n")
                    print(f"Status: {data['status']}")
                    print(f"Admission: {data['admit']}")
                    print(f"Medicine: {data['medicine']}")
                    print(f"Advice: {data['advice']}\n")
                else:
                    print(f"\n{response['message']}\n")
            except ValueError:
                print("\nInvalid input!\n")
        
        elif choice == '3':
            print_section("DELETE LINK")
            try:
                doctor_id = int(input("Doctor ID: "))
                patient_id = int(input("Patient ID: "))
                
                confirm = input("Are you sure? (Y/N): ").strip().upper()
                if confirm == 'Y':
                    request = {
                        'operation': 'delete_link',
                        'doctor_id': doctor_id,
                        'patient_id': patient_id
                    }
                    
                    response = client.send_request(request)
                    print(f"\n{response['message']}\n")
                else:
                    print("\nCancelled\n")
            except ValueError:
                print("\nInvalid input!\n")
        
        elif choice == '4':
            print_section("UPDATE TREATMENT INFO")
            try:
                doctor_id = int(input("Doctor ID: "))
                patient_id = int(input("Patient ID: "))
                print("\nUpdatable Fields: STATUS, ADMIT, MEDICINE_PRESCRIBED, ADVICE")
                field = input("Field to update: ").strip().upper()
                value = input("New value: ")
                
                request = {
                    'operation': 'update_link',
                    'doctor_id': doctor_id,
                    'patient_id': patient_id,
                    'field': field,
                    'value': value
                }
                
                response = client.send_request(request)
                if response['status'] == 'success':
                    print(f"\n{response['message']}\n")
                else:
                    print(f"\n{response['message']}\n")
            except ValueError:
                print("\nInvalid input!\n")
        
        elif choice == '5':
            break
        else:
            print("\nInvalid option!\n")

if __name__ == "__main__":
    main()
