from flask import render_template, url_for,request,redirect, jsonify
from werkzeug.security import check_password_hash, generate_password_hash
from sqlalchemy import or_
from pkg.models import db, Administrator, Driver, Order, Shipping
from pkg import mail
from flask import current_app, make_response
from flask_jwt_extended import jwt_required, get_jwt_identity, set_access_cookies
from pkg.jwt_auth.jwt import generate_admin_verification_token, generate_admin_verification_link, create_jwt_token
from sqlalchemy.exc import SQLAlchemyError
from flask_mail import Message
import jwt
from . import adminobj


def handle_preflight():
    if request.method == "OPTIONS":
        response = make_response()
        response.headers.add("Access-Control-Allow-Origin", "http://localhost:5173")
        response.headers.add("Access-Control-Allow-Headers", "Content-Type")
        response.headers.add("Access-Control-Allow-Methods", "POST")
        response.headers.add("Access-Control-Allow-Credentials", "true")
        response.status_code = 200
        return response
            

@adminobj.route('/')
def home():
    return render_template('admin/index.html')

@adminobj.route("/admin_signup/", methods=["POST"])
def admin_signup():
    try:
        preflight = handle_preflight()
        if preflight: return preflight
        
        data = request.get_json()
        if not data:
            return jsonify({"error": "Missing JSON data"}), 400

        admin_firstname = data.get("firstname")
        admin_lastname = data.get("lastname")
        admin_username = data.get("username")
        admin_password = data.get("password")
        admin_confirm_password = data.get("confirmPassword")
        admin_email = data.get("email")
        admin_phone_number = data.get("contactNo")
        admin_image = data.get("image_url")

        if not all([admin_firstname, admin_lastname, admin_username, admin_password, admin_email, admin_phone_number, admin_image, admin_confirm_password]):
            return jsonify({"error": "All fields are required"}), 400
        
        if admin_password != admin_confirm_password:
            return jsonify({"error": "Password do not Match"}), 400

    #    filter codition
        existing_admin = Administrator.query.filter(
            (Administrator.admin_email == admin_email) | (Administrator.admin_username == admin_username)
        ).first()

        if existing_admin:
            return jsonify({"error": "Email already exists, please choose another."}), 409
        
        
        secured_password = generate_password_hash(admin_password)

        new_admin = Administrator(
            admin_firstname=admin_firstname,
            admin_lastname=admin_lastname,
            admin_username=admin_username,
            admin_password=secured_password,
            admin_email=admin_email,
            admin_phone_number=admin_phone_number,
            admin_image=admin_image
        )

        db.session.add(new_admin)
        db.session.commit()

        # Send verification email
        if new_admin.admin_email:
            admin_token = generate_admin_verification_token(new_admin.admin_email)
            verification_link = generate_admin_verification_link(admin_token)

            msg = Message("Verify Your Email", recipients=[new_admin.admin_email])
            msg.body = f"Click the link to verify your email: {verification_link}"
            
            # print("Sending email...")
            mail.send(msg)
            # print("Email sent successfully!") 

        return jsonify({"message": "Admin created successfully. Verification email sent."}), 201
    
    except SQLAlchemyError as e:
        db.session.rollback()
        return jsonify({"error": "Database error occurred", "details": str(e)}), 500

    except Exception as e:
        return jsonify({"error": f"Failed to create new admin: {str(e)}"}), 500


                 
    
    
@adminobj.route("/verify_admin_email/<token>/", methods=["GET", "POST"]) 
def verify_admin_email(token):
    try:
        jwt_key = current_app.config['JWT_SECRET_KEY']
        payload = jwt.decode(token, jwt_key, algorithms=["HS256"])

        email = payload.get("email")
        # print("Extracted Email:", email)  # Debugging
        if email:
            admin_user = Administrator.query.filter_by(admin_email=email).first()
            if admin_user:
                admin_user.is_verified = "True"
                db.session.commit()
                new_token = create_jwt_token(email)
                response = make_response(redirect("http://localhost:5173/dashboard/"))
                response.set_cookie("access_token", new_token, httponly=True, secure=True, samesite="lax")
                return response
                
            return jsonify({"message": "Invalid email"}), 401
        return jsonify({"message": "Invalid email"}), 401

    except jwt.ExpiredSignatureError:
        return jsonify({"message": "Token has expired!"}), 401
    except jwt.InvalidTokenError:
        return jsonify({"message": "Invalid Token!"}), 401
        
    
    
    
    
@adminobj.route("/admin_login/", methods=["POST", "OPTIONS"])
def admin_login():
    try:
        preflight = handle_preflight()
        if preflight: return preflight
        
        data = request.get_json()
        if not data:
            return jsonify({"error": "Missing JSON data"}), 400
        
        username = data.get("username")
        password = data.get("password")

        if not username or not password:
            return jsonify({"error": "Username and password are required"}), 400

        admin = Administrator.query.filter_by(admin_username=username).first()
        if not admin:
            return jsonify({"error": "Wrong Username"}), 401
        
        hashed_password = admin.admin_password
        if check_password_hash(hashed_password, password):
            token = create_jwt_token(admin.admin_id)
            response = make_response(jsonify({"message": "Logged in Successfully"}), 202)
            response.set_cookie("access_token", token, httponly=True, secure=True, samesite="lax")
            return response  
        
        return jsonify({"error": "Wrong Password"}), 401
    
    except KeyError:
        return jsonify({"error": "Invalid request format"}), 400
    
    except SQLAlchemyError as e:
        return jsonify({"error": "Database error occurred"}), 500
    
    except Exception as e:
        return jsonify({"error": f"An unexpected error occurred: {str(e)}"}), 500

       
       
       

@adminobj.route("/driver_informations/", methods=["GET"])
@jwt_required()
def driver_informations():
    try:
        # Get all drivers
        drivers = Driver.query.all()

        # Get user ID from JWT
        user_id = get_jwt_identity()
        print("user_id:", user_id)

        # Get admin user details
        admin_user = Administrator.query.filter_by(admin_id=user_id).first()

        # If no drivers found
        if not drivers:
            return jsonify({"message": "No drivers found"}), 200
        
        # Check if admin user exists
        admin_data = {}
        if admin_user:
            admin_data = {
                "admin_username": admin_user.admin_username,
                "admin_image": admin_user.admin_image
            }
        
        # Return drivers and admin details
        return jsonify({
            "drivers": [
                {
                    "id": driver.driver_id,
                    "fullname": driver.driver_full_name,
                    "phone_number": driver.driver_phone_number,
                    "email": driver.driver_email,
                    "license_number": driver.driver_license_number,
                    "status": driver.driver_status
                } for driver in drivers
            ],
            "admin": admin_data
        }), 200

    except SQLAlchemyError as e:
        return jsonify({"error": "Database error occurred", "details": str(e)}), 500
    
    except Exception as e:
        return jsonify({"error": "Unexpected error occurred", "details": str(e)}), 500
    
    


@adminobj.route("/orders/", methods=["GET"])
def get_orders():
    try:
        orders = db.session.query(Order).all()
        
        if not orders:
            return jsonify({"message": "No order found"}), 200
        
        id = get_jwt_identity()
        admin_user = Administrator.query.filter_by(admin_id=id).first()
        
        admin_data = {}
        if admin_user:
            admin_data = {
                "username": admin_user.admin_username,
                "image": admin_user.admin_image
            }
        return jsonify(
            {
                "order_details": [
                    {
                        "id": order.order_id,
                        "date": order.order_date,
                        "status": order.order_status,
                        "total_amt": order.order_total_amt,
                        "customer_id": order.order_cust_id,
                        "shipping_id": order.order_ship_id,
                        "state_id": order.order_state_id,
                        "reference_no": order.order_reference_no,
                        "created_at": order.order_created_at,
                        "payment_status": order.order_payment_status    
                    }
                    for order in orders
                ],
                "admin_data": admin_data
            }
        ), 200
    except SQLAlchemyError as e:
        return jsonify({"error": "Database error occurred", "details": str(e)}), 500
    
    except Exception as e:
        return jsonify({"error": "Unexpected error occurred", "details": str(e)}), 500
    
   
   
    
    
@adminobj.route("/shipping/", methods=["GET"])
def get_shipping():
    try:
        ship_details = Shipping.query.all()
        
        if not ship_details:
            return jsonify({"message": "No Shipping details found"})
        
        id = get_jwt_identity()
        admin_user = Administrator.query.filter_by(admin_id=id).first()
        
        admin_data = {}
        if admin_user:
            admin_data = {
                "username": admin_user.admin_username,
                "image": admin_user.admin_image
            }
            
        return jsonify(
            {
                "shipping_details": [
                    {
                        "id": ship_detail.ship_id,
                        "ship_fee": ship_detail.ship_fees_amt,
                        "state_id": ship_detail.ship_state_id
                    } 
                    for ship_detail in ship_details
                ],

                "admin_data": admin_data
            }
        ), 200
        
    except SQLAlchemyError as e:
        return jsonify({"error": "Database error occurred", "details": str(e)}), 500
    
    except Exception as e:
        return jsonify({"error": "An unexpected error occurred", "details": str(e)}), 500