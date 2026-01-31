from flask import Blueprint, request, jsonify
from models.report import ExpenseReport, expense_reports_collection
from models.user import User
from bson import ObjectId
from models.category import category_collection,Category

report_bp = Blueprint('report', __name__)

# Helper function to verify user token
def verify_token(auth_header):
    if not auth_header or not auth_header.startswith("Bearer "):
        return None
    token = auth_header.split(" ")[1]
    return User.find_by_token(token)

# API to Add a New Report
@report_bp.route('/report', methods=['POST'])
def add_report():
    data = request.get_json()
    auth_header = request.headers.get('Authorization')

    try:
        # Verify user token
        user = verify_token(auth_header)
        if not user:
            return jsonify({'error': 'Unauthorized: Invalid or missing token'}), 401

        title = data.get('title')
        merchant_name = data.get('merchant_name')
        description = data.get('description')
        date = data.get('date')
        report_type = data.get('type')  # Make sure this key is 'type', not 'report_type'
        category_id = data.get('category')
        amount = data.get('amount')
        bill_image = data.get('bill_image', None)

        # Check if all required fields are provided
        if not all([title, merchant_name, description, date, report_type, category_id, amount, bill_image]):
            return jsonify({'error': 'All required fields must be provided'}), 400

        # Validate category ID (check if category exists)
        category = Category.find_by_id(category_id)
        if not category:
            return jsonify({'error': 'Invalid category ID'}), 400

        # Create the ExpenseReport object
        report = ExpenseReport(
            title=title,
            merchant_name=merchant_name,
            description=description,
            date=date,
            report_type=report_type,  # Store report type
            category=category_id,  # Store the category ID
            amount=float(amount),
            bill_image=bill_image,
            user_id=str(user['_id'])  # Store the user ID
        )

        # Save the report (this should update the report object with _id)
        report.save()

        # Return the success message along with the report ID
        return jsonify({
            'message': 'Report added successfully!',
            'report_id': str(report._id)
        }), 201

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@report_bp.route('/reports', methods=['GET'])
def get_all_reports():
    auth_header = request.headers.get('Authorization')

    try:
        # Verify token and get user details
        user = verify_token(auth_header)
        if not user:
            return jsonify({'error': 'Unauthorized: Invalid or missing token'}), 401

        # Find all reports for the authenticated user
        reports = expense_reports_collection.find({"user_id": str(user['_id'])})

        # Get category details for each report
        report_list = []
        for report in reports:
            # Check if the category exists for the report
            category_id = report.get('category')
            category = category_collection.find_one({"_id": ObjectId(category_id)})

            # Check if category exists
            if category is None:
                return jsonify({'error': f'Category with id {category_id} not found'}), 404

            # If the report exists, proceed with preparing the response data
            report_data = {
                'id': str(report['_id']),
                'title': report.get('title'),
                'merchant_name': report.get('merchant_name'),
                'description': report.get('description'),
                'date': report.get('date'),
                'report_type': report.get('report_type'),  # Make sure it's 'report_type', not 'type'
                'amount': report.get('amount'),
                'bill_image': report.get('bill_image', None),
                'created_at': report.get('created_at'),
                'category': {
                    'id': str(category['_id']),
                    'name': category.get('name'),
                    'icon': category.get('icon'),
                    'type': category.get('type')
                }
            }
            report_list.append(report_data)

        return jsonify({
            'reports': report_list
        }), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@report_bp.route('/report/update', methods=['PUT'])
def update_report():
    data = request.get_json()
    auth_header = request.headers.get('Authorization')

    try:
        # Verify user token
        user = verify_token(auth_header)
        if not user:
            return jsonify({'error': 'Unauthorized: Invalid or missing token'}), 401

        # Extract report ID from the request body
        report_id = data.get('id')  # Assuming the report ID is passed in the body

        # Find the report by ID
        report = ExpenseReport.find_by_id(report_id)
        if not report:
            return jsonify({'error': 'Report not found'}), 404

        # Check if the user is the owner of the report (to prevent unauthorized updates)
        if report.user_id != str(user['_id']):
            return jsonify({'error': 'Unauthorized: You cannot update this report'}), 403

        # Update fields with data from the request body
        report.title = data.get('title', report.title)  # Correctly update using dot notation
        report.merchant_name = data.get('merchant_name', report.merchant_name)
        report.description = data.get('description', report.description)
        report.date = data.get('date', report.date)
        report.report_type = data.get('report_type', report.report_type)
        report.category = data.get('category', report.category)
        report.amount = data.get('amount', report.amount)
        report.bill_image = data.get('bill_image', report.bill_image)

        # Save the updated report
        report.save()  # Call the save method to persist the changes

        return jsonify({
            'message': 'Report updated successfully!',
            'report': ExpenseReport.to_dict(report)  # Ensure correct serialization
        }), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500


# API to Delete a Report
@report_bp.route('/report/delete', methods=['DELETE'])
def delete_report():
    auth_header = request.headers.get('Authorization')
    report_id = request.headers.get('Report-ID')

    try:
        # Verify user token
        user = verify_token(auth_header)
        if not user:
            return jsonify({'error': 'Unauthorized: Invalid or missing token'}), 401

        # Ensure report ID is provided
        if not report_id:
            return jsonify({'error': 'Report ID is required'}), 400

        # Find the report by ID
        report = ExpenseReport.find_by_id(report_id)
        if not report:
            return jsonify({'error': 'Report not found'}), 404

        # Check if the user is the owner of the report
        if report.user_id != str(user['_id']):
            return jsonify({'error': 'Unauthorized: You cannot delete this report'}), 403

        # Delete the report
        report.delete(report_id)

        return jsonify({'message': 'Report deleted successfully!'}), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500

# @report_bp.route('/report/search', methods=['GET'])
# def search_report():
#     search_term = request.args.get('search_term', '').strip()  # Get the search term from query params
    
#     if not search_term:
#         return jsonify({'error': 'Search term is required'}), 400
    
#     try:
#         # Perform a case-insensitive regex search for the title and merchant_name
#         reports_cursor = expense_reports_collection.find({
#             "$or": [
#                 {"title": {"$regex": search_term, "$options": "i"}},  # Match in title (case-insensitive)
#                 {"merchant_name": {"$regex": search_term, "$options": "i"}}  # Match in merchant_name (case-insensitive)
#             ]
#         })

#         # Get the count of the reports
#         reports_count = expense_reports_collection.count_documents({
#             "$or": [
#                 {"title": {"$regex": search_term, "$options": "i"}},
#                 {"merchant_name": {"$regex": search_term, "$options": "i"}}
#             ]
#         })

#         # If no reports found
#         if reports_count == 0:
#             return jsonify({'message': 'No reports found matching the search term'}), 404

#         # Convert the reports to ExpenseReport objects
#         report_list = [ExpenseReport.to_dict(ExpenseReport(**report)) for report in reports_cursor]

#         return jsonify({
#             'message': 'Reports fetched successfully',
#             'reports': report_list
#         }), 200

#     except Exception as e:
#         return jsonify({'error': str(e)}), 500
