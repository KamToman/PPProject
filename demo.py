#!/usr/bin/env python3
"""
Demo script to showcase the Production Time Tracking Application functionality
"""
import requests
import time

BASE_URL = "http://localhost:5000"

def print_header(text):
    print("\n" + "="*60)
    print(f"  {text}")
    print("="*60)

def demo():
    print_header("Production Time Tracking Application Demo")
    
    # 1. Create an order
    print_header("1. Creating a new order (Designer Panel)")
    order_data = {
        "order_number": "DEMO-2024-001",
        "description": "Demo order for testing the system"
    }
    response = requests.post(f"{BASE_URL}/api/orders", json=order_data)
    if response.status_code == 201:
        order = response.json()
        print(f"✓ Order created successfully!")
        print(f"  Order Number: {order['order_number']}")
        print(f"  Description: {order['description']}")
        order_id = order['id']
    else:
        print(f"✗ Failed to create order: {response.json()}")
        return
    
    # 2. Get production stages
    print_header("2. Fetching production stages")
    response = requests.get(f"{BASE_URL}/api/stages")
    stages = response.json()
    print(f"✓ Found {len(stages)} production stages:")
    for stage in stages:
        print(f"  - {stage['name']}: {stage['description']}")
    
    # 3. Start work on the order (Worker Panel)
    print_header("3. Starting work on the order (Worker Panel)")
    scan_data = {
        "qr_data": f"ORDER:{order['order_number']}",
        "worker_name": "Anna Nowak",
        "stage_id": stages[0]['id'],
        "action": "start"
    }
    response = requests.post(f"{BASE_URL}/api/scan", json=scan_data)
    if response.status_code == 201:
        result = response.json()
        print(f"✓ Work started!")
        print(f"  Worker: Anna Nowak")
        print(f"  Order: {result['order_number']}")
        print(f"  Stage: {result['stage']}")
        print(f"  Start time: {result['start_time']}")
    
    # Simulate work time
    print("\n⏱  Simulating work time (3 seconds)...")
    time.sleep(3)
    
    # 4. Stop work on the order
    print_header("4. Stopping work on the order (Worker Panel)")
    scan_data['action'] = 'stop'
    response = requests.post(f"{BASE_URL}/api/scan", json=scan_data)
    if response.status_code == 200:
        result = response.json()
        print(f"✓ Work stopped!")
        print(f"  Order: {result['order_number']}")
        print(f"  Stage: {result['stage']}")
        print(f"  Duration: {result['duration_minutes']} minutes")
    
    # 5. Start another work session on a different stage
    print_header("5. Starting work on a different stage")
    scan_data = {
        "qr_data": f"ORDER:{order['order_number']}",
        "worker_name": "Jan Kowalski",
        "stage_id": stages[2]['id'],  # Montaż stage
        "action": "start"
    }
    response = requests.post(f"{BASE_URL}/api/scan", json=scan_data)
    if response.status_code == 201:
        result = response.json()
        print(f"✓ Work started!")
        print(f"  Worker: Jan Kowalski")
        print(f"  Stage: {result['stage']}")
    
    time.sleep(2)
    
    scan_data['action'] = 'stop'
    response = requests.post(f"{BASE_URL}/api/scan", json=scan_data)
    if response.status_code == 200:
        result = response.json()
        print(f"✓ Work stopped!")
        print(f"  Duration: {result['duration_minutes']} minutes")
    
    # 6. View reports (Manager Panel)
    print_header("6. Viewing Reports (Manager Panel)")
    
    # Order times report
    print("\n📊 Order Times Report:")
    response = requests.get(f"{BASE_URL}/api/reports/order-times")
    report = response.json()
    for item in report:
        print(f"  Order: {item['order_number']}")
        print(f"    Stage: {item['stage_name']}")
        print(f"    Sessions: {item['work_sessions']}")
        print(f"    Total time: {item['total_minutes']} minutes ({item['total_hours']} hours)")
        print()
    
    # Worker productivity report
    print("📊 Worker Productivity Report:")
    response = requests.get(f"{BASE_URL}/api/reports/worker-productivity")
    report = response.json()
    for item in report:
        print(f"  Worker: {item['worker_name']}")
        print(f"    Sessions: {item['work_sessions']}")
        print(f"    Total time: {item['total_minutes']} minutes ({item['total_hours']} hours)")
        print()
    
    # Stage efficiency report
    print("📊 Stage Efficiency Report:")
    response = requests.get(f"{BASE_URL}/api/reports/stage-efficiency")
    report = response.json()
    for item in report:
        print(f"  Stage: {item['stage_name']}")
        print(f"    Sessions: {item['work_sessions']}")
        print(f"    Average time: {item['avg_minutes']} minutes")
        print(f"    Total time: {item['total_minutes']} minutes")
        print()
    
    print_header("Demo completed successfully!")
    print("\nNext steps:")
    print("1. Open http://localhost:5000 in your browser")
    print("2. Try the Designer Panel to create orders and generate QR codes")
    print("3. Use the Worker Panel to scan codes and track time")
    print("4. View detailed reports in the Manager Panel")

if __name__ == "__main__":
    try:
        demo()
    except requests.exceptions.ConnectionError:
        print("\n✗ Error: Cannot connect to the application.")
        print("Please make sure the Flask application is running:")
        print("  python app.py")
    except Exception as e:
        print(f"\n✗ Error: {e}")
