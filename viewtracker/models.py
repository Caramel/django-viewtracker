"""
viewtracker/models.py - Data models for managing view tracking in Django
Copyright 2010-2013 Caramel.

This software is licensed under the terms of the 3-clause BSD license.  See
COPYING for details.

"""
from django.db import models
from django.contrib.auth.models import User
from datetime import datetime
from django.core.exceptions import ObjectDoesNotExist

class AllViewTracker(models.Model):
	user = models.ForeignKey(User, unique=True)
	last_view = models.DateTimeField(auto_now_add=True)
	
	def save(self, *args, **kwargs):
		self.last_view = datetime.now()
		super(AllViewTracker, self).save(*args, **kwargs)
		
		# delete all ModelViewTracker and InstanceViewTracker instances that are
		# for this user
		ModelViewTracker.objects.filter(user=self.user).delete()
		InstanceViewTracker.objects.filter(user=self.user).delete()
		

class ModelViewTracker(models.Model):
	class Meta:
		unique_together = ('user', 'model')
	
	user = models.ForeignKey(User)
	model = models.CharField(max_length=256)
	last_view = models.DateTimeField(auto_now_add=True)
	
	def save(self, *args, **kwargs):
		self.last_view = datetime.now()
		super(ModelViewTracker, self).save(*args, **kwargs)
		
		# delete all InstanceViewTracker instances that are for this user
		InstanceViewTracker.objects.filter(user=self.user, model=self.model).delete()

class InstanceViewTracker(models.Model):
	class Meta:
		unique_together = ('user', 'model', 'model_pk')
	
	user = models.ForeignKey(User)
	model = models.CharField(max_length=256)
	model_pk = models.IntegerField()
	last_view = models.DateTimeField(auto_now_add=True)
	
	def save(self, *args, **kwargs):
		self.last_view = datetime.now()
		super(InstanceViewTracker, self).save(*args, **kwargs)

MODIFICATION_FIELD_NAMES = (
	'last_modified',
	'last_updated',
	'modified',
	'updated',
	'changed',
	'created'
)

class ViewTracker(object):
	def __init__(self, user):
		if user == None or user.is_anonymous():
			# anonymous user.  make everything return being read, and disable tracking.
			self.mark_instance_viewed = self.mark_model_viewed = self.mark_all_viewed = self.has_viewed = (lambda *args, **kwargs: True)
		else:
			self.user = user
	
	def last_activity(self):
		"Finds the datetime that the user last accessed anything that is ViewTracker enabled.  Returns None if there is no information about views by the user."
		
		last_view = None
		for x in (AllViewTracker, ModelViewTracker, InstanceViewTracker):
			try:
				if last_view == None:
					last_view = x.objects.filter(user=self.user).order_by('-last_view').values_list('last_view', flat=True)[0]
				else:
					last_view = x.objects.filter(user=self.user, last_view__gt=last_view).order_by('-last_view').values_list('last_view', flat=True)[0]
			except ObjectDoesNotExist:
				pass
			except IndexError:
				pass
		return last_view
	
	def mark_instance_viewed(self, instance):
		"Marks the instance of the model as having being viewed."
		vt = InstanceViewTracker.objects.get_or_create(user=self.user, model=instance._meta.db_table, model_pk=instance.pk)
		vt[0].save()
	
	def mark_model_viewed(self, model):
		"Marks all instances of the model as having being viewed.  `model` may be an instance of the Model, the Model class, or a name of a table in a unicode or regular str."
		if isinstance(model, str) or isinstance(model, unicode):
			# table name was specified
			tablename = model
		else: # it's a model, or an instance of one.
			tablename = model._meta.db_table
		
		vt = ModelViewTracker.objects.get_or_create(user=self.user, model=tablename)
		vt[0].save()
		
	def mark_all_viewed(self):
		"Mark all items as viewed."
		vt = AllViewTracker.objects.get_or_create(user=self.user)
		vt[0].save()
		
	def has_viewed(self, instance, last_update=None, updated_field=None):
		"""Determine if an instance of a model has been viewed.  Takes parameters:
		
			instance: The instance of the model that is being looked up.
			
		Requires only ONE of the following parameters:
			
			last_update: When the instance was last updated.
			
			updated_field: The name of the field on the object that stores when it was last updated.  If it is callable, it will be called instead.
		"""
		if last_update == None:
			# no updated field name was given.  try to guess
			if updated_field == None:
				for x in MODIFICATION_FIELD_NAMES:
					try:
						return self.has_viewed(instance, updated_field=x)
					except:
						pass
				
				raise Exception("You must supply either last_update or updated_field parameter to is_instance_read. I tried to guess, and failed.")
						
			# update time not supplied, try to look it up
			if hasattr(instance, updated_field):
				last_update = getattr(instance, updated_field)
				if callable(last_update):
					last_update = last_update()
			else:
				# fail
				raise Exception("You must supply either last_update or updated_field parameter to is_instance_read.  No field %s was found on the instance." % updated_field)
		
		# test to see if it is a datetime
		if not isinstance(last_update, datetime):
			raise Exception("The last_updated value must be an instance of datetime.datetime.  Instead it was a %s." % type(last_update))
		
		# now we can check.
		# stage 1: see if it was updated since the AllViewTracker for the user.
		try:
			AllViewTracker.objects.get(user=self.user, last_view__gte=last_update)
			# success, there was a matching object.  this means the object has been read.
			return True
		except ObjectDoesNotExist:
			pass
			
		# Hasn't been read since the last "AllViewTracker" instance for the user.
		
		# Stage 2: see if it was updated since the ModelViewTracker for the user
		# and model.
		try:
			ModelViewTracker.objects.get(user=self.user, model=instance._meta.db_table, last_view__gte=last_update)
			return True
		except ObjectDoesNotExist:
			pass
			
		# Hasn't been read since the last "ModelViewTracker" instance for the user
		# and model.
		
		# Stage 3: see if it was updated since the last InstanceViewTracker for the
		# user and instance.
		try:
			InstanceViewTracker.objects.get(user=self.user, model=instance._meta.db_table, model_pk=instance.pk, last_view__gte=last_update)
			return True
		except ObjectDoesNotExist:
			# unread
			return False
			
