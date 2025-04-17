from datetime import datetime
from flask_sqlalchemy import SQLAlchemy

db=SQLAlchemy()


class Administrator(db.Model):
    admin_id = db.Column(db.Integer(), primary_key=True, autoincrement=True)
    admin_firstname = db.Column(db.String(100), nullable=False)
    admin_lastname = db.Column(db.String(100), nullable=False)
    admin_username = db.Column(db.String(100), nullable=False)
    admin_password = db.Column(db.String(255), nullable=False)
    admin_email = db.Column(db.String(255), nullable=False, unique=True)
    admin_phone_number = db.Column(db.String(20), nullable=False)
    admin_image = db.Column(db.String(255))
    is_verified = db.Column(db.Enum("True","False"), server_default="False")
    admin_login_time = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f"<Administrator {self.admin_firstname} - {self.admin_lastname}>"
    
    
class Customer(db.Model):
    cust_id = db.Column(db.Integer(), primary_key=True, autoincrement=True)
    cust_firstname = db.Column(db.String(255), nullable=False)
    cust_lastname = db.Column(db.String(255), nullable=False)
    cust_password = db.Column(db.String(255), nullable=False)
    cust_email = db.Column(db.String(255), nullable=False, unique=True)
    cust_phone_number = db.Column(db.String(20), nullable=False)
    cust_image = db.Column(db.String(255))
    cust_bill_address = db.Column(db.String(255), nullable=False)
    cust_status = db.Column(db.Enum("active","disabled"), server_default="active")
    cust_created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    orders = db.relationship('Order', backref='customer', lazy=True)
    
    def __repr__(self):
        return f"<Customer {self.cust_firstname} - {self.cust_lastname}>"
    
    
class Driver(db.Model):
    driver_id = db.Column(db.Integer, primary_key=True)
    driver_full_name = db.Column(db.String(255), nullable=False)
    driver_phone_number = db.Column(db.String(20), nullable=False)
    driver_email = db.Column(db.String(255), unique=True, nullable=False)
    driver_license_number = db.Column(db.String(50), unique=True, nullable=False)
    driver_status = db.Column(db.Enum('available', 'on_trip', 'inactive', name='driver_status'), default='available')

    assignment = db.relationship('Assignment', backref='driver', lazy=True)

    def __repr__(self):
        return f"<Driver {self.driver_full_name} - {self.driver_status}>"
    
    
class Order(db.Model):
    order_id = db.Column(db.Integer(), primary_key=True, autoincrement=True)
    order_date = db.Column(db.DateTime, default=datetime.utcnow)
    order_status = db.Column(db.Enum("pending","confirmed","shipped","delivered","cancelled"), server_default="pending")
    order_total_amt = db.Column(db.Numeric(10,2), nullable=False)
    order_cust_id = db.Column(db.Integer(), db.ForeignKey("customer.cust_id"), nullable=False)
    order_ship_id = db.Column(db.Integer(), db.ForeignKey("shipping.ship_id"), nullable=False)
    order_state_id = db.Column(db.Integer,db.ForeignKey('state.state_id'), nullable=False)
    order_reference_no = db.Column(db.String(255), unique=True)
    order_created_at = db.Column(db.DateTime,default=datetime.utcnow)
    order_payment_status = db.Column(db.Enum("pending","paid","failed"), server_default="pending")
    
    payments = db.relationship('Payment',backref='order', lazy=True)
    
    def __repr__(self):
        return f"<Order {self.order_reference_no} - {self.order_status}>"
    
    
class Shipping(db.Model):
    ship_id = db.Column(db.Integer(), primary_key=True, autoincrement=True)
    ship_fees_amt = db.Column(db.Numeric(10,2)) 
    ship_state_id = db.Column(db.Integer,db.ForeignKey('state.state_id'))
    
    order = db.relationship("Order", backref="shipping")
    assignment = db.relationship("Assignment", backref="shipping", lazy=True)
    
    def __repr__(self):
        return f"<Shipping {self.ship_id} - {self.ship_fees_amt}>"
    
    
class Payment(db.Model):
    pay_id = db.Column(db.Integer,primary_key=True,autoincrement=True)
    pay_date = db.Column(db.DateTime,default=datetime.utcnow)
    pay_amount = db.Column(db.Numeric(10,2))
    pay_method = db.Column(db.String(255))
    pay_status = db.Column(db.Enum('successful','pending','declined'),server_default=("pending"))
    pay_reference = db.Column(db.String(255), unique=True)
    pay_order_id = db.Column(db.Integer,db.ForeignKey('order.order_id'))
    
    def __repr__(self):
        return f"<Payment {self.pay_id} - {self.pay_amount}>"


class State(db.Model):
    state_id = db.Column(db.Integer, primary_key=True)
    state_name = db.Column(db.String(255), nullable=False)
    state_code = db.Column(db.String(10), nullable=False)
    
    orders = db.relationship("Order", backref="state", lazy=True)
    shipping = db.relationship("Shipping", backref="state", lazy=True)
    
    def __repr__(self):
        return f"<State {self.state_name} - {self.state_code}>"
    

class Assignment(db.Model):
    assign_id = db.Column(db.Integer, primary_key=True)
    assign_ship_id = db.Column(db.Integer, db.ForeignKey('shipping.ship_id'), nullable=False)
    assign_driver_id = db.Column(db.Integer, db.ForeignKey('driver.driver_id'), nullable=False)
    assign_vehicle_id = db.Column(db.Integer, db.ForeignKey('vehicle.vehicle_id'), nullable=False)
    assign_status = db.Column(db.Enum('assigned', 'in_transit', 'completed', 'cancelled'), server_default='assigned')
    assign_created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<Assignment {self.assign_id} - {self.assign_status}>"


class Vehicle(db.Model):
    vehicle_id = db.Column(db.Integer, primary_key=True)
    vehicle_type = db.Column(db.String(255), nullable=False)
    vehicle_plate_num = db.Column(db.String(50), unique=True, nullable=False)
    vehicle_status = db.Column(db.Enum('available', 'in_use', 'maintenance'), server_default='available')
    
    assignment = db.relationship("Assignment", backref="vehicle", lazy=True)
    
    def __repr__(self):
        return f"<Vehicle {self.vehicle_type} - {self.vehicle_plate_num}>"


