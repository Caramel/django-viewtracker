from django.db import models
from django.auth.models import User
from datetime import datetime

class AllViewTracker(models.Model):
	user = models.ForeignKey(User, unique=True)
	last_view = models.DateTimeField(auto_now_add=True)
	
	def save():
		last_view = datetime.now()
		super(AllViewTracker, self).save()
		
		# delete all ModelViewTracker and InstanceViewTracker instances that are
		# for this user
		ModelViewTracker.objects.filter(user=self.user).delete()
		InstanceViewTracker.objects.filter(user=self.user).delete()
		

class ModelViewTracker(models.Model):
	user = models.ForeignKey(User)
	model = models.CharField(max_length=256)
	last_view = models.DateTimeField(auto_now_add=True)
	
	def save():
		last_view = datetime.now()
		super(ModelViewTracker, self).save()
		
		# delete all InstanceViewTracker instances that are for this user
		InstanceViewTracker.objects.filter(user=self.user, model=self.model).delete()

class InstanceViewTracker(models.Model):
	user = models.ForeignKey(User)
	model = models.CharField(max_length=256)
	model_pk = models.IntegerField()
	
	def save():
		last_view = datetime.now()
		super(InstanceViewTracker, self).save()

class ViewTracker(object):
	def __init__(self, user):
		if user == None or user.is_anonymous():
			# anonymous user.  make everything return being read, and disable tracking.
			self.mark_instance_read = self.mark_model_read = self.mark_all_read = self.has_read = (lambda *args, **kwargs: True)
		else:
			self.user = user
	
	def mark_instance_read(self, instance):
		"Marks the instance of the model as read."
		vt = models.InstanceViewTracker.objects.get_or_create(user=self.user, model=instance._meta.db_table, model_pk=instance.pk)
		vt.save()
	
	def mark_model_read(self, model):
		"Marks all instances of the model as read."
		vt = models.ModelViewTracker.objects.get_or_create(user=self.user, model=instance._meta.db_table)
		vt.save()
		
	def mark_all_read(self):
		"Mark all items as read."
		vt = models.AllViewTracker(user=self.user)
		vt.save()
		
	def has_read(self, instance, last_update=None, updated_field='last_modified'):
		"""Determine if an instance of a model has been read.  Takes parameters:
		
			instance: The instance of the model that is being looked up.
			
		Requires only ONE of the following parameters:
			
			last_update: When the instance was last updated.
			
			updated_field: The name of the field on the object that stores when it was last updated.  If it is callable, it will be called instead.
		"""
		if last_update == None:
			# update time not supplied, try to look it up
			if hasattr(instance, updated_field):
				last_update = getattr(instance, updated_field)
				if callable(last_update):
					last_update = last_update()
			else:
				# fail
				raise Exception("You must supply either last_update or updated_field parameter to is_instance_read.  You supplied neither, and no field %s was found on the instance." % updated_field)
		
		# test to see if it is a datetime
		if not isinstance(last_update, datetime):
			raise Exception("The last_updated value must be an instance of datetime.datetime.  Instead it was a %s." % type(last_update))
		
		# now we can check.
		# stage 1: see if it was updated since the AllViewTracker for the user.
		try:
			AllViewTracker.objects.get(user=self.user, last_view__gte=last_update)
			# success, there was a matching object.  this means the object has been read.
			return True
		except:
			pass
			
		# Hasn't been read since the last "AllViewTracker" instance for the user.
		
		# Stage 2: see if it was updated since the ModelViewTracker for the user
		# and model.
		try:
			ModelViewTracker.objects.get(user=self.user, model=instance._meta.db_table, last_view__gte=last_update)
			return True
		except:
			pass
			
		# Hasn't been read since the last "ModelViewTracker" instance for the user
		# and model.
		
		# Stage 3: see if it was updated since the last InstanceViewTracker for the
		# user and instance.
		try:
			InstanceViewTracker.objects.get(user=self.user, model=instance._meta.db_table, last_view__gte=last_update)
			return True
		except:
			# unread
			return False
			
