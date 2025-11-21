from flask import Flask, render_template, request, jsonify, send_file, redirect, url_for
from models import db, Order, ProductionStage, TimeLog
from datetime import datetime
import qrcode
import io
import os
import secrets

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///production.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
# Use environment variable for SECRET_KEY in production, generate random one for development
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY') or secrets.token_hex(32)

db.init_app(app)

# Create QR codes directory
QR_CODE_DIR = os.path.join(app.root_path, 'static', 'qr_codes')
os.makedirs(QR_CODE_DIR, exist_ok=True)


@app.route('/')
def index():
    """Home page with navigation to different panels"""
    return render_template('index.html')


# ========== Designer Panel ==========

@app.route('/designer')
def designer_panel():
    """Designer panel for creating orders and generating QR codes"""
    orders = Order.query.order_by(Order.created_at.desc()).all()
    return render_template('designer.html', orders=orders)


@app.route('/api/orders', methods=['POST'])
def create_order():
    """API endpoint to create a new order"""
    data = request.json
    order_number = data.get('order_number')
    description = data.get('description', '')
    
    if not order_number:
        return jsonify({'error': 'Order number is required'}), 400
    
    # Check if order already exists
    existing_order = Order.query.filter_by(order_number=order_number).first()
    if existing_order:
        return jsonify({'error': 'Order number already exists'}), 400
    
    order = Order(order_number=order_number, description=description)
    db.session.add(order)
    db.session.commit()
    
    return jsonify({
        'id': order.id,
        'order_number': order.order_number,
        'description': order.description,
        'created_at': order.created_at.isoformat()
    }), 201


@app.route('/api/orders/<int:order_id>/qrcode')
def generate_qr_code(order_id):
    """Generate QR code for an order"""
    order = Order.query.get_or_404(order_id)
    
    # Generate QR code
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(f"ORDER:{order.order_number}")
    qr.make(fit=True)
    
    img = qr.make_image(fill_color="black", back_color="white")
    
    # Save to bytes
    img_io = io.BytesIO()
    img.save(img_io, 'PNG')
    img_io.seek(0)
    
    return send_file(img_io, mimetype='image/png', as_attachment=True, 
                     download_name=f'qr_order_{order.order_number}.png')


# ========== Worker Panel ==========

@app.route('/worker')
def worker_panel():
    """Worker panel for scanning QR codes and tracking time"""
    stages = ProductionStage.query.all()
    return render_template('worker.html', stages=stages)


@app.route('/api/scan', methods=['POST'])
def process_scan():
    """Process QR code scan and start/stop time tracking"""
    data = request.json
    qr_data = data.get('qr_data')
    worker_name = data.get('worker_name')
    stage_id = data.get('stage_id')
    action = data.get('action')  # 'start' or 'stop'
    
    if not all([qr_data, worker_name, stage_id, action]):
        return jsonify({'error': 'Missing required fields'}), 400
    
    # Extract order number from QR code
    if not qr_data.startswith('ORDER:'):
        return jsonify({'error': 'Invalid QR code format'}), 400
    
    order_number = qr_data.replace('ORDER:', '')
    order = Order.query.filter_by(order_number=order_number).first()
    
    if not order:
        return jsonify({'error': 'Order not found'}), 404
    
    stage = ProductionStage.query.get(stage_id)
    if not stage:
        return jsonify({'error': 'Production stage not found'}), 404
    
    if action == 'start':
        # Check if there's already an active session
        active_log = TimeLog.query.filter_by(
            order_id=order.id,
            stage_id=stage_id,
            worker_name=worker_name,
            status='in_progress'
        ).first()
        
        if active_log:
            return jsonify({'error': 'You already have an active session for this order and stage'}), 400
        
        # Create new time log
        time_log = TimeLog(
            order_id=order.id,
            stage_id=stage_id,
            worker_name=worker_name,
            start_time=datetime.utcnow(),
            status='in_progress'
        )
        db.session.add(time_log)
        db.session.commit()
        
        return jsonify({
            'message': 'Work started',
            'log_id': time_log.id,
            'order_number': order.order_number,
            'stage': stage.name,
            'start_time': time_log.start_time.isoformat()
        }), 201
    
    elif action == 'stop':
        # Find active session
        active_log = TimeLog.query.filter_by(
            order_id=order.id,
            stage_id=stage_id,
            worker_name=worker_name,
            status='in_progress'
        ).first()
        
        if not active_log:
            return jsonify({'error': 'No active session found for this order and stage'}), 404
        
        # Stop the session
        active_log.end_time = datetime.utcnow()
        active_log.status = 'completed'
        db.session.commit()
        
        return jsonify({
            'message': 'Work stopped',
            'log_id': active_log.id,
            'order_number': order.order_number,
            'stage': stage.name,
            'duration_minutes': active_log.duration_minutes
        }), 200
    
    else:
        return jsonify({'error': 'Invalid action. Use "start" or "stop"'}), 400


@app.route('/api/worker/active-sessions')
def get_active_sessions():
    """Get all active sessions for a worker"""
    worker_name = request.args.get('worker_name')
    
    if not worker_name:
        return jsonify({'error': 'Worker name is required'}), 400
    
    active_logs = TimeLog.query.filter_by(
        worker_name=worker_name,
        status='in_progress'
    ).all()
    
    sessions = []
    for log in active_logs:
        sessions.append({
            'log_id': log.id,
            'order_number': log.order.order_number,
            'stage_name': log.stage.name,
            'start_time': log.start_time.isoformat()
        })
    
    return jsonify(sessions), 200


# ========== Manager Panel ==========

@app.route('/manager')
def manager_panel():
    """Manager panel for viewing reports and analytics"""
    orders = Order.query.all()
    stages = ProductionStage.query.all()
    return render_template('manager.html', orders=orders, stages=stages)


@app.route('/api/reports/order-times')
def get_order_times_report():
    """Get time report for all orders"""
    order_id = request.args.get('order_id', type=int)
    
    # Calculate duration in days (SQLite Julian day difference)
    duration_days = db.func.julianday(TimeLog.end_time) - db.func.julianday(TimeLog.start_time)
    
    query = db.session.query(
        Order.order_number,
        Order.description,
        ProductionStage.name.label('stage_name'),
        db.func.count(TimeLog.id).label('work_sessions'),
        db.func.sum(duration_days).label('total_days')
    ).select_from(Order)\
     .join(TimeLog, Order.id == TimeLog.order_id)\
     .join(ProductionStage, TimeLog.stage_id == ProductionStage.id)\
     .filter(TimeLog.status == 'completed')
    
    if order_id:
        query = query.filter(Order.id == order_id)
    
    query = query.group_by(Order.id, ProductionStage.id)
    
    results = query.all()
    
    report_data = []
    for row in results:
        total_minutes = (row.total_days * 24 * 60) if row.total_days else 0
        report_data.append({
            'order_number': row.order_number,
            'description': row.description,
            'stage_name': row.stage_name,
            'work_sessions': row.work_sessions,
            'total_minutes': round(total_minutes, 2),
            'total_hours': round(total_minutes / 60, 2)
        })
    
    return jsonify(report_data), 200


@app.route('/api/reports/worker-productivity')
def get_worker_productivity_report():
    """Get productivity report by worker"""
    # Calculate duration in days (SQLite Julian day difference)
    duration_days = db.func.julianday(TimeLog.end_time) - db.func.julianday(TimeLog.start_time)
    
    results = db.session.query(
        TimeLog.worker_name,
        db.func.count(TimeLog.id).label('work_sessions'),
        db.func.sum(duration_days).label('total_days')
    ).filter(TimeLog.status == 'completed')\
     .group_by(TimeLog.worker_name).all()
    
    report_data = []
    for row in results:
        total_minutes = (row.total_days * 24 * 60) if row.total_days else 0
        report_data.append({
            'worker_name': row.worker_name,
            'work_sessions': row.work_sessions,
            'total_minutes': round(total_minutes, 2),
            'total_hours': round(total_minutes / 60, 2)
        })
    
    return jsonify(report_data), 200


@app.route('/api/reports/stage-efficiency')
def get_stage_efficiency_report():
    """Get efficiency report by production stage"""
    # Calculate duration in days (SQLite Julian day difference)
    duration_days = db.func.julianday(TimeLog.end_time) - db.func.julianday(TimeLog.start_time)
    
    results = db.session.query(
        ProductionStage.name,
        db.func.count(TimeLog.id).label('work_sessions'),
        db.func.avg(duration_days).label('avg_days'),
        db.func.sum(duration_days).label('total_days')
    ).select_from(ProductionStage)\
     .join(TimeLog, TimeLog.stage_id == ProductionStage.id)\
     .filter(TimeLog.status == 'completed')\
     .group_by(ProductionStage.id).all()
    
    report_data = []
    for row in results:
        avg_minutes = (row.avg_days * 24 * 60) if row.avg_days else 0
        total_minutes = (row.total_days * 24 * 60) if row.total_days else 0
        report_data.append({
            'stage_name': row.name,
            'work_sessions': row.work_sessions,
            'avg_minutes': round(avg_minutes, 2),
            'avg_hours': round(avg_minutes / 60, 2),
            'total_minutes': round(total_minutes, 2),
            'total_hours': round(total_minutes / 60, 2)
        })
    
    return jsonify(report_data), 200


# ========== Production Stage Management ==========

@app.route('/api/stages', methods=['GET', 'POST'])
def manage_stages():
    """Get all stages or create a new stage"""
    if request.method == 'GET':
        stages = ProductionStage.query.all()
        return jsonify([{
            'id': stage.id,
            'name': stage.name,
            'description': stage.description
        } for stage in stages]), 200
    
    elif request.method == 'POST':
        data = request.json
        name = data.get('name')
        description = data.get('description', '')
        
        if not name:
            return jsonify({'error': 'Stage name is required'}), 400
        
        stage = ProductionStage(name=name, description=description)
        db.session.add(stage)
        db.session.commit()
        
        return jsonify({
            'id': stage.id,
            'name': stage.name,
            'description': stage.description
        }), 201


# Initialize database
with app.app_context():
    db.create_all()
    
    # Create default production stages if they don't exist
    if ProductionStage.query.count() == 0:
        default_stages = [
            ProductionStage(name='Projektowanie', description='Etap projektowania i przygotowania'),
            ProductionStage(name='Cięcie', description='Etap cięcia materiałów'),
            ProductionStage(name='Montaż', description='Etap montażu komponentów'),
            ProductionStage(name='Kontrola jakości', description='Etap kontroli jakości'),
            ProductionStage(name='Pakowanie', description='Etap pakowania produktu')
        ]
        db.session.add_all(default_stages)
        db.session.commit()


if __name__ == '__main__':
    # Only enable debug mode if explicitly set via environment variable
    # For production, set FLASK_ENV=production
    import os
    debug_mode = os.environ.get('FLASK_DEBUG', 'False').lower() in ('true', '1', 'yes')
    app.run(debug=debug_mode, host='0.0.0.0', port=5000)
