# coding=utf-8
import unittest
from FormBinder import FormBuilder, FormItem, Types
from bottle import html_escape

class Item():
    def __init__(self):
        self._id = None
        self.title = None
        self.content = None
        self.tagIds = None

class FormBinderTest(unittest.TestCase):

    def __init__(self, *a, **kw):
        self.tags = [
            (0, 'Apples'),
            (1, 'Bananas'),
            (2, 'Pears'),
        ]

        super(self.__class__, self).__init__(*a, **kw)

    def create_form(self):
        formitems = []
        formitems.append(FormItem(Types.HIDDEN_TYPE, '_id', id='_id'))
        formitems.append(FormItem(Types.TEXT_TYPE, 'title', id='title', label_text='Title', class_name="form-control", required=True))
        formitems.append(FormItem(Types.TEXTAREA_TYPE, 'content', id='content', label_text='Content', class_name="form-control"))
        formitems.append(FormItem(Types.TEXTAREA_TYPE, 'content_html', id='content_html', label_text='Content', class_name="form-control", html=True))
        formitems.append(FormItem(Types.MULTI_SELECT_TYPE, 'tagIds', id='tagIds', label_text='Tags', class_name="form-control", select_list_items=self.tags))
        formitems.append(FormItem(Types.TEXT_TYPE, 'newTag', id='newTag', label_text='New Tag', class_name="form-control"))

        return (FormBuilder(formitems), formitems)


    def test_create_form(self):
        f, formitems = self.create_form()

        self.assertTrue(isinstance(f, FormBuilder))
        self.assertEqual(len(f.formitems), len(formitems))


    def test_bind_values(self):
        f, formitems = self.create_form()

        values = {
            '_id':('7489107348902', '7489107348902'),
            'title':('This is a title', 'This is a title'),
            'content':('<a href="/a/url?with=values&more=values">a link</a>','&lt;a href=&quot;/a/url?with=values&amp;more=values&quot;&gt;a link&lt;/a&gt;'),
            'content_html':('<a href="/a/url?with=values&more=values">a link</a>','&lt;a href=&quot;/a/url?with=values&amp;more=values&quot;&gt;a link&lt;/a&gt;'),
            'tagIds':([1,2, '<tag>is this escaped?</tag>'], [1,2, '&lt;tag&gt;is this escaped?&lt;/tag&gt;']),
            'newTag':('A new tag','A new tag'),
        }

        for item in f.formitems:
            item.bind_value(values[item.name][0]) #bind the unescaped values

        for name, value in values.iteritems():
            self.assertEqual(f.get_value(name), value[1]) #check that they match the escaped version

        html_with_values = '<form action="/url" method="get" id="form-id" class="form-class" ><div class="form-group"><input type="hidden" name="_id"  id="_id" value="7489107348902" /></div><div class="form-group"><label for="title">Title</label><input type="text" name="title" class="form-control" id="title" value="This is a title"  /></div><div class="form-group"><label for="content">Content</label><textarea name="content" class="form-control" id="content">&lt;a href=&quot;/a/url?with=values&amp;more=values&quot;&gt;a link&lt;/a&gt;</textarea></div><div class="form-group"><label for="content_html">Content</label><textarea name="content_html" class="form-control" id="content_html">&lt;a href=&quot;/a/url?with=values&amp;more=values&quot;&gt;a link&lt;/a&gt;</textarea></div><div class="form-group"><label for="tagIds">Tags</label><select name="tagIds" class="form-control" id="tagIds" multiple><option value="0" >Apples</option><option value="1" selected="selected">Bananas</option><option value="2" selected="selected">Pears</option></select></div><div class="form-group"><label for="newTag">New Tag</label><input type="text" name="newTag" class="form-control" id="newTag" value="A new tag"  /></div><div class="form-group"><input type="submit" value="Save button" class="submit-class" /></div></form>'
        form_html = f.get_html(action='/url', method='get', row_class='form-group', form_id='form-id'\
                                ,form_class='form-class', submit_btn_class='submit-class', submit_btn_text='Save button')
        
        self.assertEqual(form_html, html_with_values)


    def test_set_values(self):
        f, formitems = self.create_form()

        values = {
            '_id':('7489107348902', '7489107348902'),
            'title':('This is a title', 'This is a title'),
            'content':('<a href="/a/url?with=values&more=values">a link</a>','&lt;a href=&quot;/a/url?with=values&amp;more=values&quot;&gt;a link&lt;/a&gt;'),
            'content_html':('<a href="/a/url?with=values&more=values">a link</a>','&lt;a href=&quot;/a/url?with=values&amp;more=values&quot;&gt;a link&lt;/a&gt;'),
            'tagIds':([1,2, '<tag>is this escaped?</tag>'], [1,2, '&lt;tag&gt;is this escaped?&lt;/tag&gt;']),
            'newTag':('A new tag','A new tag'),
        }

        for item in f.formitems:
            f.set_value(item.name, values[item.name][0]) #set the unescaped values

        for name, value in values.iteritems():
            self.assertEqual(f.get_value(name), value[1]) #check that they match the escaped version


    def test_is_valid(self):
        f, formitems = self.create_form()

        self.assertFalse(f.is_valid())

        f.set_value('title', 'This is required')

        self.assertTrue(f.is_valid())


    def test_hydrate_entity(self):
        f, formitems = self.create_form()

        values = {
            '_id':('7489107348902', '7489107348902'),
            'title':('This is a title', 'This is a title'),
            'content':('<a href="/a/url?with=values&more=values">a link</a>','&lt;a href=&quot;/a/url?with=values&amp;more=values&quot;&gt;a link&lt;/a&gt;'),
            'content_html':('<a href="/a/url?with=values&more=values">a link</a>','&lt;a href=&quot;/a/url?with=values&amp;more=values&quot;&gt;a link&lt;/a&gt;'),
            'tagIds':([1,2, '<tag>is this escaped?</tag>'], [1,2, '&lt;tag&gt;is this escaped?&lt;/tag&gt;']),
            'newTag':('A new tag','A new tag'),
        }

        for item in f.formitems:
            f.set_value(item.name, values[item.name][0]) #set the unescaped values

        i = f.hydrate_entity(Item())

        self.assertEqual(i._id, f.get_value('_id'))
        self.assertEqual(i.title, f.get_value('title'))
        self.assertEqual(html_escape(i.content), f.get_value('content'))
        self.assertEqual(html_escape(i.content), f.get_value('content_html'))
        self.assertEqual(i.tagIds[0], f.get_value('tagIds')[0])
        self.assertEqual(i.tagIds[1], f.get_value('tagIds')[1])
        self.assertEqual(html_escape(i.tagIds[2]), f.get_value('tagIds')[2])


    def test_custom_validator(self):
        def validator(form):
            errors = []
            if form.get_value('password') != form.get_value('passwordconf'):
                errors.append('Passwords do not match')

            return errors

        formitems = []
        formitems.append(FormItem(Types.PASSWORD_TYPE, 'password', required=True))
        formitems.append(FormItem(Types.PASSWORD_TYPE, 'passwordconf', required=True))

        f = FormBuilder(formitems, validator=validator)        

        self.assertFalse(f.is_valid())

        f.set_value('password', 'pass')
        f.set_value('passwordconf', 'differentpass')

        self.assertFalse(f.is_valid())

        f.set_value('passwordconf', 'pass')        

        self.assertTrue(f.is_valid())


    def test_entity_in_constructor(self):

        i = Item()
        i._id = '2436728647829'
        i.title = 'Test title'
        i.content = 'escapable <content></content>'
        i.tagIds = [1,2,3]
    
        formitems = []
        formitems.append(FormItem(Types.HIDDEN_TYPE, '_id', id='_id'))
        formitems.append(FormItem(Types.TEXT_TYPE, 'title', id='title', label_text='Title', class_name="form-control", required=True))
        formitems.append(FormItem(Types.TEXTAREA_TYPE, 'content', id='content', label_text='Content', class_name="form-control"))
        formitems.append(FormItem(Types.MULTI_SELECT_TYPE, 'tagIds', id='tagIds', label_text='Tags', class_name="form-control", select_list_items=self.tags))
        formitems.append(FormItem(Types.TEXT_TYPE, 'newTag', id='newTag', label_text='New Tag', class_name="form-control"))

        f = FormBuilder(formitems, entity=i)

        #test that the form values have been populated from the entity
        self.assertEqual(i._id, f.get_value('_id'))
        self.assertEqual(i.title, f.get_value('title'))
        self.assertEqual(html_escape(i.content), f.get_value('content'))
        self.assertEqual(i.tagIds, f.get_value('tagIds'))





if __name__ == '__main__':
    unittest.main()
