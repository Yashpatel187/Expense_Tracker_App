from datetime import datetime
from bson import ObjectId
from database import db

# Use the 'expense_reports' collection from the database
expense_reports_collection = db['reports']

class ExpenseReport:
    def __init__(self, _id=None, title=None, merchant_name=None, description=None, date=None,
                 report_type=None, category=None, amount=None, bill_image=None, user_id=None, created_at=None):
        self._id = _id  # Handle _id separately as it's assigned by MongoDB
        self.title = title
        self.merchant_name = merchant_name
        self.description = description
        self.date = date
        self.report_type = report_type
        self.category = category
        self.amount = amount
        self.bill_image = bill_image
        self.user_id = user_id
        self.created_at = created_at or datetime.utcnow()  # Automatically set created_at if not provided

    def save(self):
        # Prepare the report data to be saved
        report_data = {
            'title': self.title,
            'merchant_name': self.merchant_name,
            'description': self.description,
            'date': self.date,
            'report_type': self.report_type,
            'category': self.category,
            'amount': self.amount,
            'bill_image': self.bill_image,
            'user_id': self.user_id,
            'created_at': self.created_at
        }

        # Save to the database
        if self._id:
            # Update the existing report if _id is provided
            expense_reports_collection.update_one({"_id": ObjectId(self._id)}, {"$set": report_data})
        else:
            # Insert a new report if _id is not provided
            result = expense_reports_collection.insert_one(report_data)
            self._id = result.inserted_id

    @staticmethod
    def find_by_id(report_id):
        report_data = expense_reports_collection.find_one({"_id": ObjectId(report_id)})
        if report_data:
            return ExpenseReport(**report_data)  # Create and return an instance of ExpenseReport
        return None

    @staticmethod
    def delete(report_id):
        expense_reports_collection.delete_one({"_id": ObjectId(report_id)})

    @staticmethod
    def to_dict(report):
        return {
            'id': str(report._id),
            'title': report.title,
            'merchant_name': report.merchant_name,
            'description': report.description,
            'date': report.date,
            'report_type': report.report_type,
            'category': report.category,
            'amount': report.amount,
            'bill_image': report.bill_image,
            'created_at': report.created_at,
            'user_id': report.user_id
        }
