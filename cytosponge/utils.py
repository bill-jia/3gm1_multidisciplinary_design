template = "An exception of type {0} occurred. Arguments:\n{1!r}"
def format_error_message(e):
	message = template.format(type(e).__name__, e.args)
	return message
