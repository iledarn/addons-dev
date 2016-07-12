=============================================
 Limit number of records for arbitrary model
=============================================

Usage
=====

* In debug mode open ``Settings / Users / Groups``
* Find there ``Limit records number / Control limits on records number`` group and add your user in the group.
* Open ``Settings / Technical / Security / Records Number Limits`` menu
* Create new recorod. For exapmle:

** Model: Users 
** Domain: [('active', '=', True)]
** Maximum Users: 3

* Save the record
* Try to create more users from ``Settings / Users``. When you try to create more than three users then you see an exception message.
The system doesn't allow you create more than three users.
