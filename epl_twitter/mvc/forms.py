from django import forms
from django.forms.extras.widgets import SelectDateWidget
import datetime

#Database began collecting data on 4-30-2015
DB_START_DATE = datetime.date(2015, 4, 30)

class DatesForm(forms.Form):
	start_date = forms.DateField(
		widget = forms.DateInput(attrs={'class':'date_picker'}))
	end_date = forms.DateField(
		widget = forms.DateInput(attrs={'class':'date_picker'}))

	def clean_start_date(self):
		input_date = self.cleaned_data['start_date']
		if input_date < DB_START_DATE:
			raise forms.ValidationError(
				"Start date must be after 4/30/2015")
		return input_date

	def clean(self):
		cleaned_data = super(DatesForm, self).clean()
		start = cleaned_data.get('start_date')
		end = cleaned_data.get('end_date')

		print start, end

		if start and end:
			#only proceed if both fields are valid so far
			if end < start:
				raise forms.ValidationError(
					"End date must be after start date")
