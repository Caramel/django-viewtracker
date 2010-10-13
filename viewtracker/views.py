from models import ViewTracker

def mark_all_as_read(request, fallback_redirect_to='/'):
	"""Marks all objects as read for ViewTracker.  POST to this view and all objects will be marked as read.
	
	Redirects the user back to the page from whence they came when done, or if there is no referrer, then fallback_redirect_to.
	"""
	
	if request.method != 'POST':
		raise Exception("You must POST to this view.")
		
	tracking = ObjectTracker(request.user)
	tracking.mark_all_read()
	
	if request.META.has_key('HTTP_REFERER'):
		return HttpResponseRedirect(request.META['HTTP_REFERER'])
	else:
		return HttpResponseRedirect(redirect_to)
