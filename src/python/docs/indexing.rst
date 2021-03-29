Indexing
**************************
The indexing module creates indices over the data model in memory.  For
example, users may want to quickly reference all of a particular type of device in the model.
Creating an index allows you to reference all resistors created in the data model.  There
are two types of indices:

#. **StatementIndex:** This is the standard index definition.  These types 
   of indices are built over a field in the indexed objects. You can constrain 
   the types that the index will observe.  For example, an index may only be 
   over Devices, but not over Commands.  Further, you can add on optional sorting 
   preference.  For example, you could index over Device types (resistors, 
   capacitors, etc...) and each list of a specific type can be sorted by 
   the Device's name.
#. **MasterIndex:** A MasterIndex object holds a list of all StatementIndex objects that
   are defined in the data model.  It is the MasterIndex's responsibility to handle 
   additions and deletions of objects to all indices under the MasterIndex.

StatementIndex generally extends the GEN_STATEMENT_INDEX.  This class provides
most of the framework for creating general indices over an object's field.  However,
you can create a GEN_STATEMENT_INDEX directly.

You can also write a custom index class for the index defined above.


Parsing and Indexing
=========================
The parser is responsible for populating the index.  There are, in reality, several layers in 
between.  However, generally, the parser will read in statements
and add them line by line.  In some instances, the parser may not know if a reference
exists or not.

Parsers also must track scoping.  This is tracked using the push_scope() and
pop_scope() functions provided by the NAME_SCOPE_INDEX.  See :ref:`push_scope() <push-scope>`
for an example.

Writing and indexing
=========================
Indices are also used to simplify the writing process.  The SRC_LINE_INDEX
was made for this purpose.  It keeps track of the source file and line number(s)
of each statement.

Abstract indices
=========================
The following indices are abstract and should not be created.  All indices extend 
one of these abstract classes.

StatementIndex
-------------------------
.. automodule:: xdm.index.StatementIndex
   :members:

MasterIndex
-------------------------
.. automodule:: xdm.index.MasterIndex
   :members:

General Indices
=========================
The Indices can be initialized directly.  Typically, all indices that extend
StatementIndes extend the GEN_STATEMENT_INDEX as this provides the general 
framework for basic indices.

GEN_STATEMENT_INDEX
-------------------------
.. automodule:: xdm.index.GEN_STATEMENT_INDEX
   :members:

DEVICES_INDEX
-------------------------
.. automodule:: xdm.index.DEVICES_INDEX
   :members:

COMMANDS_INDEX
-------------------------
.. automodule:: xdm.index.COMMANDS_INDEX
   :members:

COMMENTS_INDEX
-------------------------
.. automodule:: xdm.index.COMMENTS_INDEX
   :members:

REFS_INDEX
-------------------------
.. automodule:: xdm.index.REFS_INDEX
   :members:

SRC_LINE_INDEX
-------------------------
.. automodule:: xdm.index.SRC_LINE_INDEX
   :members:

LAZY_STATEMENT_INDEX
-------------------------
.. automodule:: xdm.index.LAZY_STATEMENT_INDEX
   :members:

NAME_SCOPE_INDEX
-------------------------
.. automodule:: xdm.index.NAME_SCOPE_INDEX
   :members:

UID
-------------------------
.. automodule:: xdm.index.UID
   :members:
