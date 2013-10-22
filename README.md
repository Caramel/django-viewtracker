# django-viewtracker #

`django-viewtracker` is a simple Django application to allow you to do view tracking on objects.  The primary purpose of the module is so that a user can determine what objects they have already seen.

It contains some additional "smarts" for dealing with updates as well - so if you haven't read it since an update, then you haven't read it at all.

The module is generic, and can be applied to any model you like.

Unlike some other view tracking modules for Django, this one stores it's data in a `Model` (instead of the session), and thus only works for users who are registered.  Unregistered users won't have any view tracking at all, and all objects will appear as read for them.  The advantage of doing this is that view tracking works across all devices/browsers that someone uses.

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

## Using ##

First, track views of your object in your view (normally object detail view):

```python
from viewtracker.models import ViewTracker
from .models import Car


class CarDetailView(View):
	def get(self, request, object_id):
		# Get the instance of the object to view
		# (Though in reality you'd probably use the Django Generic CBVs instead
		# of this.)
		car = get_object_or_404(Car, id=object_id)

		# Create an instance of the tracker for this user
		# If they are anonymous, then everything is viewed.
		tracking = ViewTracker(request.user)

		# Mark the instance viewed by this user
		tracking.mark_instance_viewed(car)

		# Render the template to display the object.
		return render(request, 'my_app/car_detail.html', dict(car=car, user=user))
```

You can then look up if an object has some changed data.  You could show this in a list:

```python
from django_globals import globals as django_globals


class Car(models.Model):
	# ... other fields ..

	# Use the name "last_updated" as the app will automatically to use this
	# field name
	last_updated = models.DateTimeField(auto_now=True)

	def has_viewed(self):
		tracker = ViewTracker(django_globals.request.user)
		
		# Here we've manually supplied the updated field name.
		return tracking.has_viewed(self, updated_field='last_updated')
```

Then in the template, you would have something like:

```html
{% for car in car_list %}
	{# ... #}
	<td>
		<a href="{{ car.get_absolute_url }}">Listing #{{ car.id }}</a>
		{% if not car.has_viewed %}
			<img src="{{ STATIC_URL }}img/new.png" alt="New!" />
		{% endif %}
	</td>
	{# ... #}
{% endfor %}
```

There are also some built-in views, which you can use for marking all objects read, or all instances of a model as read:

```python
url(
	r'^cars/mark_all_read/$',
	login_required()(viewtracker.views.mark_model_as_viewed),
	dict(model=Car),
	name='mark_all_cars_as_viewed'
),
```

Then call it in your template with something like:

```html
<form method="post" action="{% url 'mark_all_cars_as_viewed' %}">
	{% csrf_token %}
	<input type="submit" value="Mark all cars as viewed" />
</form>
```


