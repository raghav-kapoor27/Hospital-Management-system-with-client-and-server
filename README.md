# SR Hospital Management System

A Python-based Client-Server Hospital Management System for managing doctor records, patient information, and treatment details using MySQL and TCP Socket Programming.

## Features

### Doctor Management

* Add, Search, Update, Delete Doctors
* Store specialization and date of birth

### Patient Management

* Register and manage patients
* Maintain medical history and complaints
* Assign doctors to patients

### Treatment Management

* Create doctor-patient links
* Record treatment status
* Store medicines and medical advice
* Manage admission details

### Technical Features

* Client-Server Architecture
* TCP Socket Communication
* Multi-threaded Server
* MySQL Database Integration
* JSON-based Data Exchange
* Input Validation and Error Handling

## Tech Stack

* Python
* MySQL
* MySQL Connector
* Socket Programming
* Multithreading
* JSON

## Project Structure

```text
├── client.py
├── server.py
└── README.md
```

## Setup

### Install Dependency

```bash
pip install mysql-connector-python
```

### Create Database

```sql
CREATE DATABASE hospital_doctor_patients_record;
```

### Run Server

```bash
python server.py
```

### Run Client

```bash
python client.py
```

## Database Tables

* doctors_record
* patients_record
* doctor_patient_record

## Core Operations

* Doctor CRUD Operations
* Patient CRUD Operations
* Treatment Record Management
* Doctor-Patient Association

## Future Improvements

* Authentication System
* GUI Interface
* Appointment Scheduling
* REST API Support
* Medical Report Generation

## License

Developed for educational and academic purposes.
