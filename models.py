from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class Quote(db.Model):
    __tablename__ = 'quotes'
    
    id = db.Column(db.Integer, primary_key=True)
    
    # Base columns (7 total including id)
    quote_number = db.Column(db.String(50), nullable=False, unique=True)
    date = db.Column(db.Date, nullable=False)
    vin_number = db.Column(db.String(17), nullable=False)
    vin_picture_link = db.Column(db.String(500))
    year = db.Column(db.Integer)
    make = db.Column(db.String(50))
    model = db.Column(db.String(50))
    instructions = db.Column(db.Text, nullable=True)

    # Service columns - chips
    chips_photo_link = db.Column(db.String(500))
    chips_parts_cost = db.Column(db.Numeric(10, 2), default=0.00)
    chips_labor_cost = db.Column(db.Numeric(10, 2), default=0.00)
    
    # Service columns - scratches
    scratches_photo_link = db.Column(db.String(500))
    scratches_parts_cost = db.Column(db.Numeric(10, 2), default=0.00)
    scratches_labor_cost = db.Column(db.Numeric(10, 2), default=0.00)
    
    # Service columns - dents
    dents_photo_link = db.Column(db.String(500))
    dents_parts_cost = db.Column(db.Numeric(10, 2), default=0.00)
    dents_labor_cost = db.Column(db.Numeric(10, 2), default=0.00)
    
    # Service columns - Headlights
    headlights_photo_link = db.Column(db.String(500))
    headlights_parts_cost = db.Column(db.Numeric(10, 2), default=0.00)
    headlights_labor_cost = db.Column(db.Numeric(10, 2), default=0.00)
    
    # Service columns - wheels
    wheels_photo_link = db.Column(db.String(500))
    wheels_parts_cost = db.Column(db.Numeric(10, 2), default=0.00)
    wheels_labor_cost = db.Column(db.Numeric(10, 2), default=0.00)
    
    # Service columns - interior
    interior_photo_link = db.Column(db.String(500))
    interior_parts_cost = db.Column(db.Numeric(10, 2), default=0.00)
    interior_labor_cost = db.Column(db.Numeric(10, 2), default=0.00)
    
    # Service columns - detail
    detail_photo_link = db.Column(db.String(500))
    detail_parts_cost = db.Column(db.Numeric(10, 2), default=0.00)
    detail_labor_cost = db.Column(db.Numeric(10, 2), default=0.00)
    
    # Service columns - carspabasic
    carspabasic_photo_link = db.Column(db.String(500))
    carspabasic_parts_cost = db.Column(db.Numeric(10, 2), default=0.00)
    carspabasic_labor_cost = db.Column(db.Numeric(10, 2), default=0.00)
    
    # Service columns - carspaplus
    carspaplus_photo_link = db.Column(db.String(500))
    carspaplus_parts_cost = db.Column(db.Numeric(10, 2), default=0.00)
    carspaplus_labor_cost = db.Column(db.Numeric(10, 2), default=0.00)
    
    # Service columns - bed_liner
    bed_liner_photo_link = db.Column(db.String(500))
    bed_liner_parts_cost = db.Column(db.Numeric(10, 2), default=0.00)
    bed_liner_labor_cost = db.Column(db.Numeric(10, 2), default=0.00)
    
    # Service columns - paint_body
    paint_body_photo_link = db.Column(db.String(500))
    paint_body_parts_cost = db.Column(db.Numeric(10, 2), default=0.00)
    paint_body_labor_cost = db.Column(db.Numeric(10, 2), default=0.00)
    
    def get_service_total(self, service_name):
        """Calculate total for a specific service (parts + labor)"""
        parts = getattr(self, f'{service_name}_parts_cost', 0) or 0
        labor = getattr(self, f'{service_name}_labor_cost', 0) or 0
        return float(parts) + float(labor)
    
    def get_grand_total(self):
        """Calculate grand total across all services"""
        services = ['chips', 'scratches', 'dents', 'headlights', 'wheels', 
                 'interior', 'detail', 'carspabasic', 'carspaplus', 'bed_liner', 'paint_body']
        total = 0.0
        for service in services:
            total += self.get_service_total(service)
        return total
    
    def __repr__(self):
        return f'<Quote {self.quote_number}>'
