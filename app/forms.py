from flask.ext.wtf import Form, TextField, BooleanField
from flask.ext.wtf import Required

class BookForm(Form):
	title = TextField('openid', validators = [Required()])
	ean = BooleanField('remember_me', default = False)
	isbn =