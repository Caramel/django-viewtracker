"""
viewtracker/views.py - Views for managing view tracking in Django
Copyright 2010-2013 Caramel.

This software is licensed under the terms of the 3-clause BSD license.  See
COPYING for details.

"""

from models import ViewTracker
from django.http import HttpResponseRedirect, HttpResponseNotAllowed

def mark_all_as_viewed(request, fallback_redirect_to='/'):
	"""Marks all objects as viewed for ViewTracker.  POST to this view and all objects will be marked as viewed.
	
	Redirects the user back to the page from whence they came when done, or if there is no referrer, then fallback_redirect_to.
	"""
	
	if request.method != 'POST':
		return HttpResponseNotAllowed(['POST'])
		
	tracking = ViewTracker(request.user)
	tracking.mark_all_viewed()
	
	if request.META.has_key('HTTP_REFERER'):
		return HttpResponseRedirect(request.META['HTTP_REFERER'])
	else:
		return HttpResponseRedirect(redirect_to)
		
		
def mark_model_as_viewed(request, model, fallback_redirect_to='/'):
	"""Marks all objects of a particular type as viewed for ViewTracker.  POST to this view and all objects of that type will be marked as viewed.
	
	Redirects the user back to the page from whence they came when done, or if there is no referrer, then fallback_redirect_to.
	
	Specify the parameter model to set the model that is being marked as read.  This may be an instance of the model, the class of the model, or the name of the model's table.
	"""
	
	if request.method != 'POST':
		return HttpResponseNotAllowed(['POST'])
				
	tracking = ViewTracker(request.user)
	tracking.mark_model_viewed(model)
	
	if request.META.has_key('HTTP_REFERER'):
		return HttpResponseRedirect(request.META['HTTP_REFERER'])
	else:
		return HttpResponseRedirect(redirect_to)
		
