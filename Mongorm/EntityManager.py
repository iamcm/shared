import re
from decimal import Decimal
from pymongo import MongoClient
from bson.objectid import ObjectId
import models
from settings import DBHOST, DBPORT, DBNAME, DBDEBUG
import Auth.auth
from Helpers.logger import log_to_file
from collections import OrderedDict

class EntityManager:

    def __init__(self, db=None, debug=False):
        client = MongoClient(DBHOST, port=DBPORT)
        self.db = client[db or DBNAME]
        self.debug = DBDEBUG or debug
        

    def _hydate(self, data):
        """
        Use the given data to identify and populate and instance an entity
        """
        entity = self._unicode_to_class_instance(data.get('__instanceOf__'))
        setattr(entity, '_id', data.get('_id'))

        #for each property in this entity class
        for prop in dir(entity):
            #we dont want anything callable e.g. methods, __doc__, etc
            if not callable(getattr(entity, prop)) and not prop.startswith('__'):
                #get this property's type
                proptype = type(getattr(entity, prop))
                #get the value from the data for this property
                propvalue = data.get(prop)

                #if this is a list then iterate each list item and
                #hydrate any entities if necessary
                if proptype == list:
                    items = []
                    for item in propvalue:
                        #we can tell if this is an entity that we need to hydrate by
                        #looking for dict's with our signature __instanceOf__ item
                        if type(item)==dict and item.has_key('__instanceOf__'):
                            #hydrate this item
                            entityinstance = self._unicode_to_class_name(item['__instanceOf__'])
                            entityid = item['_id']

                            #add this item to the list of hydrated items
                            item = self.find_one(entityinstance, entityid)

                        items.append(item)

                    #set this property value to be the list of processed items
                    propvalue = items

                #else if this is a dict that we need to hydrate
                elif type(propvalue)==dict and propvalue.has_key('__instanceOf__'):
                    #hydrate this item
                    entityinstance = self._unicode_to_class_name(propvalue['__instanceOf__'])
                    entityid = propvalue['_id']

                    propvalue = self.find_one(entityinstance, entityid)

                #now assign our final propvalue to our entity
                setattr(entity, prop, propvalue)

        return entity


    def _entity_to_dict(self, entity, saveChildEntities=False):
        """
        Convert an entity class to a dict in order to persist it to the database
        Note we cant just call entity.__dict__ because we want to find any entity 
        instances inside this class, eg User.groups = [<GroupInstance>, <GroupInstance>]
        and convert these as well.
        saveChildEntities determines whether or not to automatically save any child entities 
        found inside this class, it is always True when called from this classes save method
        but False by default to allow for this method to be called in a debugging context so that
        nothing gets written to the database
        """
        obj = {}
        #for each property in this entity class
        for prop in dir(entity):
            #we dont want anything callable e.g. methods, __doc__, etc
            if not callable(getattr(entity, prop)) and not prop.startswith('__'):
                #get this property's type
                proptype = type(getattr(entity, prop))
                #get the value from the data for this property
                propvalue = getattr(entity, prop)

                #eg User.groups = [<GroupEntity>,<GroupEntity>,<GroupEntity>]
                if proptype == list:
                    items = []

                    for item in propvalue:
                        #if the items in this list are entities then convert them to an object as well
                        if hasattr(item, '_presave') and saveChildEntities:
                            #save the entity
                            item = self.save(self._unicode_to_class_name(str(item.__class__)), item)
                            #convert this entity
                            item = self._entity_to_dict(item)
                        
                        #add this item to the list of processed items
                        items.append(item)

                    #set this property value to be the list of processed items
                    propvalue = items

                #eg User.role = <UserRoleEntity>
                elif hasattr(propvalue, '_presave') and saveChildEntities:
                    #save the entity
                    propvalue = self.save(self._unicode_to_class_name(str(propvalue.__class__)), propvalue)
                    #convert this entity
                    propvalue = self._entity_to_dict(propvalue)

                obj[prop] = propvalue


        # add __class__ as metadata with the name of __instanceOf__ so we can grab it when
        # hydrating an entity
        obj['__instanceOf__'] = str(entity.__class__)

        return obj


    def entity_to_json_safe_dict(self, entity):
        obj = {}
        #for each property in this entity class
        for prop in dir(entity):
            #we dont want anything callable e.g. methods, __doc__, etc
            if not callable(getattr(entity, prop)) and not prop.startswith('__'):
                #get this property's type
                proptype = type(getattr(entity, prop))
                #get the value from the data for this property
                propvalue = getattr(entity, prop)

            
                if proptype == list:
                    items = []

                    for item in propvalue:
                        #if the items in this list are entities then convert them to an object as well
                        if hasattr(item, '_presave'):
                            #convert this entity
                            item = self.entity_to_json_safe_dict(item)
                        
                        #add this item to the list of processed items
                        items.append(item)

                    #set this property value to be the list of processed items
                    propvalue = items

                #eg User.role = <UserRoleEntity>
                elif hasattr(propvalue, '_presave'):
                    #convert this entity
                    propvalue = self.entity_to_json_safe_dict(propvalue)

                obj[prop] = str(propvalue)
            
        return obj



    def _unicode_to_class_instance(self, string):
        """
        Takes the output of <class>.__class__ and returns an instance of that class

        eg:
        Item.__class__ returns:
            <class 'models.Item.Item'>
        so calling _unicode_to_class_instance on this would return an instance of: 
            models.Item.Item
        """
        return eval(string[string.find("'")+1:string.rfind("'")]+'()')


    def _unicode_to_class_name(self, string):
        """
        Takes the output of <class>.__class__ and returns a string describing that class
        without its namespace 

        eg:
        Item.__class__ returns:
            <class 'models.Item.Item'>
        so calling _unicode_to_class_name on this would return: 
            'Item'
        which can be used to call other methods on this class:
            self.find_one('Item', '<itemid>')
        """
        return str(string[string.rfind(".")+1:string.rfind("'")])


    def find_raw(self, collectionname, objfilter=None, sort=None):
        """
        Find all entries for a given collection
        """
        if self.debug: log_to_file("db.%s.find(%s, sort=%s)" % (collectionname, objfilter, sort))
        return self.db[collectionname].find(objfilter, sort=sort)


    def find(self, collectionname, objfilter=None, sort=None):
        """
        Find all entries for a given collection and return them as a instances of the given entity
        """
        items = []
        for item in self.find_raw(collectionname, objfilter, sort):
            items.append(self._hydate(item))

        return items


    def find_one_raw(self, collectionname, id=None, objfilter=None):
        """
        Find one for a given collection
        """
        if id:
            if self.debug: log_to_file("db.%s.find_one({'_id':ObjectId(%s)})" % (collectionname, id))
            item = self.db[collectionname].find_one({'_id':ObjectId(id)})
        else:
            if self.debug: log_to_file("db.%s.find_one(%s)" % (collectionname, objfilter))
            item = self.db[collectionname].find_one(objfilter)

        return item


    def find_one(self, collectionname, objfilter):
        """
        Find one for a given collection and return it as an instance of the given entity
        """
        item = self.find_one_raw(collectionname, objfilter=objfilter)
        if item:
            item = self._hydate(item)
        return item


    def find_one_by_id(self, collectionname, id):
        """
        Find one for a given collection and return it as an instance of the given entity
        """
        item = self.find_one_raw(collectionname, id=id)
        if item:
            item = self._hydate(item)
        return item


    def save(self, collectionname,  entity):
        """
        Insert or Update a single entity, set the entity-s _id and return the saved entity
        """
        #call the pre-save hook
        entity._presave(self)

        obj = self._entity_to_dict(entity, True)
        
        if self.debug: log_to_file("db.%s.save(%s)" % (collectionname, obj))

        entity._id = self.db[collectionname].save(obj)

        #call the post-save hook
        entity._postsave(self)

        return entity


    def remove_one(self, collectionname, id):
        """
        Delete one entity by id
        """
        if self.debug: log_to_file("db.%s.remove({'_id':ObjectId(%s)}" % (collectionname, id))
        self.db[collectionname].remove({'_id':ObjectId(id)})


    def _stem(self, word):
        parts = []

        for i in range(len(word)):
            try:
                parts.append(word[i:i+3])
            except:
                pass

        return [p for p in parts if len(p) > 2]


    def fuzzy_text_search(self, collectionname, searchterm, field):
        """
        Performs a fuzzy text search on a given entity.

        searchterm should be one or more space seperated words

        field should be a string naming a field to search

        e.g.
        searchterm = 'This is a test'
        items = EntityManager().fuzzy_text_search('Item', searchterm, 'title')        
        """
        matches = {} #for raw matches
        goodmatches = [] #for matches that are accurate
        compiledre = re.compile('\W|_') #match all non-alphanumeric characters
        
        # replace non-alphanumeric characters with spaces
        searchterm = compiledre.sub(' ', searchterm)

        # search a single word at a time
        for word in searchterm.split(' '):
            #split the word into parts
            stems = self._stem(word)
            #run a search for each part
            for term in stems:
                # construct mongo command to search for the part in the given field
                filter_criteria={field:{'$regex':term, '$options': 'i' }}                   

                # add each result to the 'matches' list, or increment its count if it already exists
                for result in self.find_raw(collectionname, filter_criteria):
                    #get the actual word(s) that matched

                    #replace non-alphanumeric characters with spaces
                    matched_content = compiledre.sub(' ', result[field])

                    for _word in matched_content.split(' '):
                        if term in _word:
                            try:
                                matches[str(result['_id']) +':'+ _word]['count'] += 1
                            except:
                                matches[str(result['_id']) +':'+ _word] = {'entity':result, 'count':1}
    


            # if we have any stems
            if len(stems) > 0:
                # for each match calculate its accuracy and add it to the 'goodmatches' list if applicable
                for m, entity_count_dict in matches.items():
                    c = entity_count_dict['count']
                    m = m.split(':')[1]
                    """
                    if the percentage of stems that matched is greater than 70 
                    eg 'TIME' would stem to 'ti','im','me', so a search for 'tide' would only match two stems out of three
                    with a percentage of 66%
                    --OR--
                    the percentage of stems that matched is only 20% but the length of word that matched is the same or two characters
                    longer than the search word
                    eg the example above would pass now because i assume that the words are similar based on a partial stem match and a similar 
                    word length
                    """

                    if Decimal(c) / Decimal(len(stems)) * 100 > 70 \
                        or (len(m) < len(word)+2 and len(m) >= len(word) and Decimal(c) / Decimal(len(stems)) * 100 > 30):
                        
                        #Logger.log_to_file(m)
                        #Logger.log_to_file(100*c)
                        #Logger.log_to_file(100-len(m))
                        """
                        this is a good match so add it to the list along with some weighting fields to order the results by. 

                        The first weight is the number of stems that this word matched multiplied by 100 (this carries the heaviest weight because
                        if all stems were matched then this must be the exact word!) Multiplying by 100 ensures that this weight has the greatest 
                        impact on the final calculation.

                        The second weight is 100 minus the length of the matched word, this is because a search for 'chris' needs to return
                        'chris' before 'christopher','christine','christian' but they would all score the same on the number of stems matched.
                        The second weight is subtracted from 100 to give a 'higher is better' result that is consistent with the first weight...
                        eg 'chris' (100-5=95) should be better than 'christopher' (100-11=89). 100 was chosen because its longer than any word
                        that could be searched and is less than or equal to the multiplier used for the first weight
                        """
                        goodmatches.append((entity_count_dict['entity'], 100*c, 100-len(m)))

        # finally add the two weights together to get an integer and order the results with the highest first
        final = sorted( goodmatches, key=lambda x:x[1] + x[2], reverse=True )

        # convert final matches into proper entity objects
        entities = []
        processed_ids = []
        for result in final:
            if result[0]['_id'] not in processed_ids:
                processed_ids.append(result[0]['_id'])
                entities.append(self._hydate(result[0]))
        
        return entities
        


    def geospatial_near(self, collectionname, field, coords, maxDistance):
        """
        Requires a 2dsphere index:
        db.<collection>.ensureIndex( { <location field> : "2dsphere" } )

        eg:
        items = em.geospatial_near('Location', 'location', [50.0, 3.65], 100)
        """

        criteria = OrderedDict({
                                    '$near' :
                                    { 
                                        '$geometry' :
                                        { 
                                            'type' : "Point" ,
                                            'coordinates' : coords 
                                        } 
                                    }
                                })
        #mongodb requires $near to be the first item in the dict, so we need to 
        #use an OrderedDict and add $maxDistance after $near in order to 
        #use it
        criteria.update({'$maxDistance':maxDistance})

        criteria = { field : criteria}

        items = []
        for item in self.find_raw(collectionname, criteria):
            items.append(self._hydate(item))

        return items

