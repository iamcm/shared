
from bottle import html_escape


HIDDEN_TYPE = "hidden"
TEXT_TYPE = "text"
PASSWORD_TYPE = "password"
TEXTAREA_TYPE = "textarea"
CHECKBOX_TYPE = "checkbox"
RADIO_TYPE = "radio"
SELECT_TYPE = "select"


class FormBuilder:
	def __init__(self, entity, formitems=[], validator=None):
		self.entity = entity
		self.formitems = formitems
		self._is_valid = True
		self.errors = []
		self.validate = False
		self.validator = validator

	def is_valid(self):
		self.validate = True
		self.errors = []
		self.get_html() #force value binding and formitem validation
		if self.validator:
			self.errors.extend(self.validator(self.entity))

		return self._is_valid

	def get_html(self, action='', method='post', row_class=None, id=None, form_class=None\
					,submit_btn_class=None, submit_btn_text='Save'):
		errorshtml = ''

		idhtml = ''
		if id:
			idhtml = 'id="%s"' % id

		formclasshtml = ''
		if form_class:
			formclasshtml = 'class="%s"' % form_class

		formhtml = '<form action="%s" method="%s" %s %s>' % (action, method, idhtml, formclasshtml)
		for item in self.formitems:
			value = getattr(self.entity, item.name)
			formhtml += item.get_html(value, row_class)
			if self.validate and not item.is_valid():
				if item.error_message() not in self.errors:
					self.errors.append(item.error_message())


		submitclasshtml = ''
		if submit_btn_class:
			submitclasshtml = 'class="%s"' % submit_btn_class

		formhtml += '<input type="submit" value="%s" %s />' % (submit_btn_text, submitclasshtml)
		formhtml += '</form>'

		if len(self.errors) > 0 != '':
			errorshtml = '<div class="alert alert-danger"><ul>'
			for error in self.errors:
				errorshtml += '<li>%s</li>' % error
			errorshtml += '</ul></div>'
			self._is_valid = False

		return errorshtml + formhtml


class FormItem:
	def __init__(self, type, name, class_name=None, id=None, label_text=None, select_list_items=[], required=False):
		self.type = type
		self.name = name
		self.class_name = class_name
		self.id = id
		self.label_text = label_text
		self.select_list_items = select_list_items
		self.required = required
		self.value = None

	def is_valid(self):
		if self.required and (self.value is None or str(self.value).strip() == ''):
			return False
		else:
			return True

	def error_message(self):
		if self.label_text:
			text = self.label_text
		else:
			text = self.name

		return '%s is a required field' % text

	def get_html(self, value=None, row_class=None):
		if value and type(value) == str:
			value = html_escape(value)
		elif value and type(value) == int:
			value = str(value)

		self.value = value

		classhtml = ''
		if self.class_name:
			classhtml = 'class="%s"' % self.class_name

		idhtml = ''
		if self.id:
			idhtml = 'id="%s"' % self.id

		template = ""

		if self.type == HIDDEN_TYPE:
			if value:
				valuehtml = 'value="%s"' % value
			else:
				valuehtml = ''

			template += '<input type="hidden" name="%s" %s %s %s />' % (self.name, classhtml, idhtml, valuehtml)

		elif self.type == TEXT_TYPE:
			if value:
				valuehtml = 'value="%s"' % value
			else:
				valuehtml = ''

			if self.label_text and self.id:
				template += '<label for="%s">%s</label>' % (self.id, self.label_text)
			template += '<input type="text" name="%s" %s %s %s />' % (self.name, classhtml, idhtml, valuehtml)

		elif self.type == PASSWORD_TYPE:

			if self.label_text and self.id:
				template += '<label for="%s">%s</label>' % (self.id, self.label_text)
			template += '<input type="password" name="%s" %s %s />' % (self.name, classhtml, idhtml)

		elif self.type == TEXTAREA_TYPE:
			if value:
				valuehtml = value
			else:
				valuehtml = ''

			if self.label_text and self.id:
				template += '<label for="%s">%s</label>' % (self.id, self.label_text)
			template += '<textarea name="%s" %s %s>%s</textarea>' % (self.name, classhtml, idhtml, valuehtml)


		elif self.type == CHECKBOX_TYPE:
			if value and (value=='1' or value==True):
				valuehtml = 'checked="checked"'
			else:
				valuehtml = ''

			if self.label_text and self.id:
				template += '<label for="%s">%s</label>' % (self.id, self.label_text)
			template += '<input type="checkbox" name="%s" %s %s %s />' % (self.name, classhtml, idhtml, valuehtml)



		elif self.type == RADIO_TYPE:
			if value and (value=='1' or value==True):
				valuehtml = 'checked="checked"'
			else:
				valuehtml = ''

			if self.label_text and self.id:
				template += '<label for="%s">%s</label>' % (self.id, self.label_text)
			template += '<input type="radio" name="%s" %s %s %s />' % (self.name, classhtml, idhtml, valuehtml)



		elif self.type == SELECT_TYPE:
			if self.label_text and self.id:
				template += '<label for="%s">%s</label>' % (self.id, self.label_text)
				template += '<select name="%s" %s %s>' % (self.name, classhtml, idhtml)

				for item in self.select_list_items:
					if value and str(value) == str(item[0]):
						valuehtml = 'selected="selected"'
					else:
						valuehtml = ''

					template += '<option value="%s" %s>%s</option>' % (item[0], valuehtml, item[1])

				template += '</select>'


		rowclasshtml = ''
		if row_class:
			rowclasshtml = 'class="%s"' % row_class

		return '<div %s>%s</div>' % (rowclasshtml, template)





