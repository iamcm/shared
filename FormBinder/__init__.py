import bottle
from bottle import html_escape

class Types:
	HIDDEN_TYPE = "hidden"
	INT_TYPE = "int"
	TEXT_TYPE = "text"
	PASSWORD_TYPE = "password"
	TEXTAREA_TYPE = "textarea"
	CHECKBOX_TYPE = "checkbox"
	RADIO_TYPE = "radio"
	SELECT_TYPE = "select"
	MULTI_SELECT_TYPE = "multiselect"
	FILE_TYPE = "file"


class FormBuilder:
	def __init__(self, formitems=[], validator=None, entity=None):
		self.formitems = formitems
		self.errors = []
		self.validator = validator

		if entity:
			for item in formitems:
				if hasattr(entity, item.name):
					item.bind_value(getattr(entity, item.name))


	def get_value(self, name):
		for item in self.formitems:
			if item.name == name:
				return item.value

		return None


	def set_value(self, name, value):
		for item in self.formitems:
			if item.name == name:
				item.bind_value(value)


	def hydrate_entity(self, entity):
		for item in self.formitems:
			if hasattr(entity, item.name) or item.name == '_id':
				setattr(entity, item.name, item.value)

		return entity


	def is_valid(self):
		self.errors = []
		for item in self.formitems:
			if not item.is_valid():
				if item.error_message not in self.errors:
					self.errors.append(item.error_message)

		if self.validator:
			self.errors.extend(self.validator(self))

		return len(self.errors) == 0

	def get_html(self, action='', method='post', row_class=None, form_id=None, form_class=None\
					,submit_btn_class=None, submit_btn_text='Save'):
		errorshtml = ''

		idhtml = ''
		if form_id:
			idhtml = 'id="%s"' % form_id

		formclasshtml = ''
		if form_class:
			formclasshtml = 'class="%s"' % form_class

		formhtml = '<form action="%s" method="%s" %s %s>' % (action, method, idhtml, formclasshtml)
		for item in self.formitems:
			formhtml += item.get_html(row_class)


		submitclasshtml = ''
		if submit_btn_class:
			submitclasshtml = 'class="%s"' % submit_btn_class


		rowclasshtml = ''
		if row_class:
			rowclasshtml = 'class="%s"' % row_class

		formhtml += '<div %s><input type="submit" value="%s" %s /></div>' % (rowclasshtml, submit_btn_text, submitclasshtml)
		formhtml += '</form>'

		if len(self.errors) > 0 != '':
			errorshtml = '<div class="alert alert-danger"><ul>'
			for error in self.errors:
				errorshtml += '<li>%s</li>' % error
			errorshtml += '</ul></div>'
			self._is_valid = False

		return errorshtml + formhtml


class FormItem:
	def __init__(self, type, name, class_name=None, id=None, label_text=None, select_list_items=[], required=False, html=False):
		self.type = type
		self.name = name
		self.class_name = class_name
		self.id = id
		self.label_text = label_text
		self.select_list_items = select_list_items
		self.required = required
		self.value = None
		self.error_message = ''
		self.html = html

	def is_valid(self):
		if self.label_text:
			text = self.label_text
		else:
			text = self.name

		if self.required and (self.value is None or str(self.value).strip() == ''):
			self.error_message = '%s is a required field' % text
			return False

		elif self.required and self.type == Types.INT_TYPE:
			try:
				int(self.value)
				return True

			except:
				self.error_message = '%s must be an integer' % text
				return False
		else:
			return True

	def bind_value(self, value):
		if value and type(value) == str and not self.html:
			value = html_escape(value.strip())
		elif value and type(value) == list:
			escaped_list = []
			for i in value:
				if type(i) == str and not self.html:
					escaped_list.append(html_escape(i))
				else:
					escaped_list.append(i)
			value = escaped_list

		self.value = value

	def get_html(self, row_class=None):

		classhtml = ''
		if self.class_name:
			classhtml = 'class="%s"' % self.class_name

		idhtml = ''
		if self.id:
			idhtml = 'id="%s"' % self.id

		template = ""

		if self.type == Types.HIDDEN_TYPE:
			if self.value:
				valuehtml = 'value="%s"' % self.value
			else:
				valuehtml = ''

			template += '<input type="hidden" name="%s" %s %s %s />' % (self.name, classhtml, idhtml, valuehtml)

		elif self.type == Types.TEXT_TYPE or self.type == Types.INT_TYPE:
			if self.value:
				valuehtml = 'value="%s"' % self.value
			else:
				valuehtml = ''

			if self.label_text and self.id:
				template += '<label for="%s">%s</label>' % (self.id, self.label_text)
			template += '<input type="text" name="%s" %s %s %s />' % (self.name, classhtml, idhtml, valuehtml)

		elif self.type == Types.PASSWORD_TYPE:

			if self.label_text and self.id:
				template += '<label for="%s">%s</label>' % (self.id, self.label_text)
			template += '<input type="password" name="%s" %s %s />' % (self.name, classhtml, idhtml)

		elif self.type == Types.TEXTAREA_TYPE:
			if self.value:
				valuehtml = self.value
			else:
				valuehtml = ''

			if self.label_text and self.id:
				template += '<label for="%s">%s</label>' % (self.id, self.label_text)
			template += '<textarea name="%s" %s %s>%s</textarea>' % (self.name, classhtml, idhtml, valuehtml)


		elif self.type == Types.CHECKBOX_TYPE:
			if self.value and (self.value=='1' or self.value==True):
				valuehtml = 'checked="checked"'
			else:
				valuehtml = ''

			if self.label_text and self.id:
				template += '<label for="%s">%s</label>' % (self.id, self.label_text)
			template += '<input type="checkbox" name="%s" %s %s %s />' % (self.name, classhtml, idhtml, valuehtml)



		elif self.type == Types.RADIO_TYPE:
			if self.value and (self.value=='1' or self.value==True):
				valuehtml = 'checked="checked"'
			else:
				valuehtml = ''

			if self.label_text and self.id:
				template += '<label for="%s">%s</label>' % (self.id, self.label_text)
			template += '<input type="radio" name="%s" %s %s %s />' % (self.name, classhtml, idhtml, valuehtml)



		elif self.type == Types.SELECT_TYPE:
			if self.label_text and self.id:
				template += '<label for="%s">%s</label>' % (self.id, self.label_text)
				
			template += '<select name="%s" %s %s>' % (self.name, classhtml, idhtml)

			for item in self.select_list_items:
				if self.value and str(self.value) == str(item[0]):
					valuehtml = 'selected="selected"'
				else:
					valuehtml = ''

				template += '<option value="%s" %s>%s</option>' % (item[0], valuehtml, item[1])

			template += '</select>'



		elif self.type == Types.MULTI_SELECT_TYPE:
			if self.label_text and self.id:
				template += '<label for="%s">%s</label>' % (self.id, self.label_text)
				
			template += '<select name="%s" %s %s multiple>' % (self.name, classhtml, idhtml)

			for item in self.select_list_items:
				if self.value and len([v for v in self.value if str(v)==str(item[0])]) > 0:
					valuehtml = 'selected="selected"'
				else:
					valuehtml = ''

				template += '<option value="%s" %s>%s</option>' % (item[0], valuehtml, item[1])

			template += '</select>'

		elif self.type == Types.FILE_TYPE:
			if self.value:
				valuehtml = 'value="%s"' % self.value
			else:
				valuehtml = ''

			if self.label_text and self.id:
				template += '<label for="%s">%s</label>' % (self.id, self.label_text)
			template += '<input type="file" name="%s" %s %s %s />' % (self.name, classhtml, idhtml, valuehtml)


		rowclasshtml = ''
		if row_class:
			rowclasshtml = 'class="%s"' % row_class

		return '<div %s>%s</div>' % (rowclasshtml, template)




"""
Bottle plugin
"""
class FormBinderPlugin(object):
    name = 'form_binder'
    api  = 2

    def __init__(self):
        pass

    def apply(self, callback, route):

        def wrapper(*a, **ka):
            form = route.config.get('form')()
            for formitem in form.formitems:
                if bottle.request.params.get(formitem.name):
                    if formitem.type == Types.MULTI_SELECT_TYPE:
                        try:
                            formitem.bind_value(bottle.request.params.getall(formitem.name))
                        except:
                            pass

                    elif formitem.type == Types.INT_TYPE:
                        try:
                            formitem.bind_value(int(bottle.request.params.get(formitem.name)))
                        except:
                            pass

                    else:
                        try:
                            formitem.bind_value(str(bottle.request.params.get(formitem.name)))
                        except:
                            pass

            bottle.request.form = form

            return callback(*a, **ka)

        return wrapper