from flask_wtf import FlaskForm
from wtforms import StringField, DateField, DecimalField, TextAreaField, SubmitField
from wtforms.validators import DataRequired, Optional, NumberRange
from datetime import date

class QuoteForm(FlaskForm):
    # Base fields
    invoice_number = StringField('Invoice Number', validators=[DataRequired()])
    date = DateField('Date', validators=[DataRequired()], default=date.today)
    date_promised = DateField('Date Promised', validators=[Optional()])
    date_delivered = DateField('Date Delivered', validators=[Optional()])
    stock_number = StringField('Stock #', validators=[Optional()])
    to_name = StringField('To', validators=[Optional()])
    tag_number = StringField('Tag #', validators=[Optional()])
    color = StringField('Color', validators=[Optional()])
    vehicle = StringField('Vehicle (Year / Make / Model)', validators=[Optional()])
    instructions = TextAreaField('Instructions', validators=[Optional()])

    # Service fields - headlights_resurfacing
    headlights_resurfacing_photo_link = StringField('Headlights Re-surfacing Photo Link', validators=[Optional()])
    headlights_resurfacing_parts_cost = DecimalField('Headlights Re-surfacing Parts Cost', validators=[Optional()], places=2)
    headlights_resurfacing_labor_cost = DecimalField('Headlights Re-surfacing Labor Cost', validators=[Optional()], places=2)

    # Service fields - headlights_ceramic
    headlights_ceramic_photo_link = StringField('Headlights Ceramic Coating Photo Link', validators=[Optional()])
    headlights_ceramic_parts_cost = DecimalField('Headlights Ceramic Coating Parts Cost', validators=[Optional()], places=2)
    headlights_ceramic_labor_cost = DecimalField('Headlights Ceramic Coating Labor Cost', validators=[Optional()], places=2)

    # Service fields - trim_ceramic
    trim_ceramic_photo_link = StringField('Trim Ceramic Coating Photo Link', validators=[Optional()])
    trim_ceramic_parts_cost = DecimalField('Trim Ceramic Coating Parts Cost', validators=[Optional()], places=2)
    trim_ceramic_labor_cost = DecimalField('Trim Ceramic Coating Labor Cost', validators=[Optional()], places=2)

    # Service fields - car_wizard_diy
    car_wizard_diy_photo_link = StringField('Car Wizard DIY Kit Photo Link', validators=[Optional()])
    car_wizard_diy_parts_cost = DecimalField('Car Wizard DIY Kit Parts Cost', validators=[Optional()], places=2)
    car_wizard_diy_labor_cost = DecimalField('Car Wizard DIY Kit Labor Cost', validators=[Optional()], places=2)

    # Service fields - carspa_sealant
    carspa_sealant_photo_link = StringField('Car Spa (Sealant) Photo Link', validators=[Optional()])
    carspa_sealant_parts_cost = DecimalField('Car Spa (Sealant) Parts Cost', validators=[Optional()], places=2)
    carspa_sealant_labor_cost = DecimalField('Car Spa (Sealant) Labor Cost', validators=[Optional()], places=2)

    # Service fields - carspa_ceramic
    carspa_ceramic_photo_link = StringField('Car Spa (Plus Ceramic) Photo Link', validators=[Optional()])
    carspa_ceramic_parts_cost = DecimalField('Car Spa (Plus Ceramic) Parts Cost', validators=[Optional()], places=2)
    carspa_ceramic_labor_cost = DecimalField('Car Spa (Plus Ceramic) Labor Cost', validators=[Optional()], places=2)

    # Service fields - mechanical
    mechanical_photo_link = StringField('Mechanical Photo Link', validators=[Optional()])
    mechanical_parts_cost = DecimalField('Mechanical Parts Cost', validators=[Optional()], places=2)
    mechanical_labor_cost = DecimalField('Mechanical Labor Cost', validators=[Optional()], places=2)

    # Service fields - glass
    glass_photo_link = StringField('Glass Photo Link', validators=[Optional()])
    glass_parts_cost = DecimalField('Glass Parts Cost', validators=[Optional()], places=2)
    glass_labor_cost = DecimalField('Glass Labor Cost', validators=[Optional()], places=2)

    # Service fields - tint
    tint_photo_link = StringField('Tint Photo Link', validators=[Optional()])
    tint_parts_cost = DecimalField('Tint Parts Cost', validators=[Optional()], places=2)
    tint_labor_cost = DecimalField('Tint Labor Cost', validators=[Optional()], places=2)

    # Service fields - misc
    misc_photo_link = StringField('Misc Photo Link', validators=[Optional()])
    misc_parts_cost = DecimalField('Misc Parts Cost', validators=[Optional()], places=2)
    misc_labor_cost = DecimalField('Misc Labor Cost', validators=[Optional()], places=2)
    
    submit = SubmitField('Save Quote')
