from flask_wtf import FlaskForm
from wtforms import StringField, DateField, IntegerField, DecimalField, TextAreaField, SubmitField
from wtforms.validators import DataRequired, Optional, NumberRange
from datetime import date

class QuoteForm(FlaskForm):
    # Base fields
    quote_number = StringField('Quote Number', validators=[DataRequired()])
    date = DateField('Date', validators=[DataRequired()], default=date.today)
    vin_number = StringField('VIN Number', validators=[DataRequired()])
    vin_picture_link = StringField('VIN Picture', validators=[Optional()])
    year = IntegerField('Year', validators=[Optional()])
    make = StringField('Make', validators=[Optional()])
    model = StringField('Model', validators=[Optional()])
    instructions = TextAreaField('Instructions', validators=[Optional()])

    # Service fields - chips
    chips_photo_link = StringField('Chips Photo Link', validators=[Optional()])
    chips_parts_cost = DecimalField('Chips Parts Cost', validators=[Optional()], places=2)
    chips_labor_cost = DecimalField('Chips Labor Cost', validators=[Optional()], places=2)
    
    # Service fields - scratches
    scratches_photo_link = StringField('Scratches Photo Link', validators=[Optional()])
    scratches_parts_cost = DecimalField('Scratches Parts Cost', validators=[Optional()], places=2)
    scratches_labor_cost = DecimalField('Scratches Labor Cost', validators=[Optional()], places=2)
    
    # Service fields - dents
    dents_photo_link = StringField('Dents Photo Link', validators=[Optional()])
    dents_parts_cost = DecimalField('Dents Parts Cost', validators=[Optional()], places=2)
    dents_labor_cost = DecimalField('Dents Labor Cost', validators=[Optional()], places=2)
    
    # Service fields - Headlights
    headlights_photo_link = StringField('Headlights Photo Link', validators=[Optional()])
    headlights_parts_cost = DecimalField('Headlights Parts Cost', validators=[Optional()], places=2)
    headlights_labor_cost = DecimalField('Headlights Labor Cost', validators=[Optional()], places=2)
    
    # Service fields - wheels
    wheels_photo_link = StringField('Wheels Photo Link', validators=[Optional()])
    wheels_parts_cost = DecimalField('Wheels Parts Cost', validators=[Optional()], places=2)
    wheels_labor_cost = DecimalField('Wheels Labor Cost', validators=[Optional()], places=2)
    
    # Service fields - interior
    interior_photo_link = StringField('Interior Photo Link', validators=[Optional()])
    interior_parts_cost = DecimalField('Interior Parts Cost', validators=[Optional()], places=2)
    interior_labor_cost = DecimalField('Interior Labor Cost', validators=[Optional()], places=2)
    
    # Service fields - detail
    detail_photo_link = StringField('Detail Photo Link', validators=[Optional()])
    detail_parts_cost = DecimalField('Detail Parts Cost', validators=[Optional()], places=2)
    detail_labor_cost = DecimalField('Detail Labor Cost', validators=[Optional()], places=2)
    
    # Service fields - carspabasic
    carspabasic_photo_link = StringField('CarsPA Basic Photo Link', validators=[Optional()])
    carspabasic_parts_cost = DecimalField('CarsPA Basic Parts Cost', validators=[Optional()], places=2)
    carspabasic_labor_cost = DecimalField('CarsPA Basic Labor Cost', validators=[Optional()], places=2)
    
    # Service fields - carspaplus
    carspaplus_photo_link = StringField('CarsPA Plus Photo Link', validators=[Optional()])
    carspaplus_parts_cost = DecimalField('CarsPA Plus Parts Cost', validators=[Optional()], places=2)
    carspaplus_labor_cost = DecimalField('CarsPA Plus Labor Cost', validators=[Optional()], places=2)
    
    # Service fields - bed_liner
    bed_liner_photo_link = StringField('Bed Liner Photo Link', validators=[Optional()])
    bed_liner_parts_cost = DecimalField('Bed Liner Parts Cost', validators=[Optional()], places=2)
    bed_liner_labor_cost = DecimalField('Bed Liner Labor Cost', validators=[Optional()], places=2)
    
    # Service fields - paint_body
    paint_body_photo_link = StringField('Paint & Body Photo Link', validators=[Optional()])
    paint_body_parts_cost = DecimalField('Paint & Body Parts Cost', validators=[Optional()], places=2)
    paint_body_labor_cost = DecimalField('Paint & Body Labor Cost', validators=[Optional()], places=2)
    
    submit = SubmitField('Save Quote')
