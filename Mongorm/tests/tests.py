import unittest
from EntityManager import EntityManager
from pymongo import MongoClient
from settings import DBHOST, DBNAME, DBPORT
from models import Item
from bson import ObjectId
from datetime import datetime
from time import sleep
import json

class EntityManagerTest(unittest.TestCase):

    def setUp(self):
        self.em = EntityManager()

    def save_entity(self, _id=None, title='Test', items=[]):
        i = Item()
        if _id:
            i._id = _id
        i.title = title
        i.content = 'Some content'
        i.tagIds = [1,2,3]
        i.added = datetime.now()
        i.items = items

        return self.em.save('Item', i)

    def test_save(self):
        entity = self.save_entity()
        #test 'save' returns the saved entity
        self.assertIsInstance(entity, Item)

    def test_find(self):
        self.save_entity(title='Test1')
        sleep(1)
        self.save_entity(title='Test2')

        items = self.em.find('Item')

        self.assertEqual(len(items), 2)

        items = self.em.find('Item', sort=[('added',1)])

        self.assertEqual(items[0].title, 'Test1')
        self.assertEqual(items[1].title, 'Test2')

        items2 = self.em.find('Item', sort=[('added',-1)])

        self.assertEqual(items2[0].title, 'Test2')
        self.assertEqual(items2[1].title, 'Test1')


    def test_find_raw_count(self):
        self.save_entity(title='Test1')
        self.save_entity(title='Test2')

        item_count = self.em.find_raw('Item', count=True)

        self.assertEqual(item_count, 2)


    def test_find_one_by_id(self):
        _id = ObjectId()
        self.save_entity(_id=_id)

        item = self.em.find_one_by_id('Item', _id) #test that an ObjectId _id returns correctly
        self.assertIsInstance(item, Item)
        item = self.em.find_one_by_id('Item', str(_id)) #test that a string _id returns correctly
        self.assertIsInstance(item, Item)


    def test_find_one(self):
        self.save_entity(title='Test1')
        self.save_entity(title='Test2')

        item = self.em.find_one('Item', {'title':'Test2'})

        self.assertEqual(item.title, 'Test2')


    def test_nested_objects(self):
        self.save_entity(title='Test1', items = [Item(),Item(),Item()])

        item = self.em.find_one('Item', {'title':'Test1'})

        self.assertEqual(len(item.items), 3)

        for i in item.items:
            self.assertIsInstance(i, Item)


    def test_entity_to_json_safe_dict(self):
        i = Item()
        i.title = 'Nested Item'
        self.save_entity(title='Test1', items = [i,i,i])

        item = self.em.find_one('Item', {'title':'Test1'})

        jsondict = self.em.entity_to_json_safe_dict(item)

        self.assertIsInstance(jsondict, dict)

        self.assertEqual(jsondict['title'], 'Test1')

        #test nested object are still available
        self.assertEqual(jsondict['items'][0]['title'], 'Nested Item')

        #shouldnt be able to json serialise a datetime
        self.assertRaises(TypeError, json.dumps, item) 

        #should be able to json serialise Item after entity_to_json_safe_dict call
        self.assertIsInstance(json.dumps(jsondict), str) 


    def test_remove_one(self):
        self.save_entity(title='Test1')
        self.save_entity(title='Test2')
        self.save_entity(title='Test3')

        items = self.em.find('Item')

        self.assertEqual(len(items), 3)

        self.assertEqual(items[0].title, 'Test1')
        self.assertEqual(items[1].title, 'Test2')
        self.assertEqual(items[2].title, 'Test3')

        self.em.remove_one('Item', items[1]._id)

        items = self.em.find('Item')

        self.assertEqual(len(items), 2)

        self.assertEqual(items[0].title, 'Test1')
        self.assertEqual(items[1].title, 'Test3')


    def test_fuzzy_text_search(self):
        self.save_entity(title='These are some apples')
        self.save_entity(title='these are some pears')
        self.save_entity(title='theseare some bananas')

        # case insensitive
        items = self.em.fuzzy_text_search('Item', 'These', 'title')
        self.assertEqual(len(items), 3)

        items = self.em.fuzzy_text_search('Item', 'some apple', 'title')
        self.assertEqual(len(items), 3)

        items = self.em.fuzzy_text_search('Item', 'apples', 'title')
        self.assertEqual(len(items), 1)

        # spelling mistake
        items = self.em.fuzzy_text_search('Item', 'applss', 'title')
        self.assertEqual(len(items), 1)


    def tearDown(self):
        client = MongoClient(DBHOST, port=DBPORT)
        client[DBNAME].Item.drop()



if __name__ == '__main__':
    unittest.main()
