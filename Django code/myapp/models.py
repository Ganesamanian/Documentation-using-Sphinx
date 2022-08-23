# from django.db import models

#$$$$$$$$$$$$$$$$$$$$$$$$$$$Reference$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$

# # Create your models here.
#from neomodel import (StructuredNode, StringProperty,
# IntegerProperty,UniqueIdProperty, RelationshipTo)

# # Create your models here.


#class City(StructuredNode):
#     code = StringProperty(unique_index=True, required=True)
#     name = StringProperty(index=True, default="city")

#class Person(StructuredNode):
#     uid = UniqueIdProperty()
#     name = StringProperty(unique_index=True)
#     age = IntegerProperty(index=True, default=0)

#     # Relations :
#     city = RelationshipTo(City, 'LIVES_IN')
#     friends = RelationshipTo('Person','FRIEND')

#$$$$$$$$$$$$$$$$$$$$$$$$$$$Reference$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$

#!/usr/bin/env python
# coding: utf-8


from neomodel import (StructuredNode, StringProperty, IntegerProperty,
    UniqueIdProperty, RelationshipTo, RelationshipFrom)

class Page(StructuredNode):
    
    """
    This class specifies node properties and relation

    Inputs:
        page_uid: unique identification for node
        page_name: name of the node
        page_url: url of the node
        relation: connection between the node

    Returns:
        None

    Output:
        Creation of node in Neo4j
    """

    #page_uid = UniqueIdProperty()
    page_name = StringProperty(unique_index=True)
    page_url = StringProperty(index=True, default=" ")
    # html = StringProperty(index=True, default=" ")    

    #Relations
    relation = RelationshipTo('Page', 'LINKED_TO')






