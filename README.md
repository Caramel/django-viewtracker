# django-viewtracker #

`django-viewtracker` is a simple Django application to allow you to do view tracking on objects.  The primary purpose of the module is so that a user can determine what objects they have already seen.

It contains some additional "smarts" for dealing with updates as well - so if you haven't read it since an update, then you haven't read it at all.

The module is generic, and can be applied to any model you like.

Unlike some other view tracking modules for Django, this one stores it's data in a `Model` (instead of the session), and thus only works for users who are registered.  Unregistered users won't have any view tracking at all, and all objects will appear as read for them.

## Installation ##

Install the module with the normal `sudo ./setup.py install`.

Add `viewtracker` to your `INSTALLED_APPS` in the `settings.py` of your application.

You'll need to `./manage.py syncdb` so that viewtracker's modules can be installed.

Now you're ready to use it.

## Design ##

The system has three levels of view tracking.  It will check each of these in order to determine if an object has been viewed.

The first level is "all view" tracking.  Your application may allow a user to mark all objects as read.  This is checked first against the object's modification time.  When you mark everything as viewed, all other records of views for the user are deleted to save space.

The second level is "model view" tracking.  Your application may allow a user to mark all objects of a particular type as read.  This the second thing to be checked against the object's modification time.  When you mark all of a model as viewed, all other records of individual item views are deleted to save space.

The third level is "instance view" tracking.  A user views an object, you would use this to mark it as having being viewed.

This means to determine if an object has been viewed, it goes through three levels of checks, each increasing in complexity.  The viewtracker tables may become quite large.


