"""
	marvin.views.promo
	~~~~~~~~~~~~~~~~~~

	Promo page for Streamr.

"""

from flask import Blueprint, render_template

mod = Blueprint(__name__, 'marvin.promo')

@mod.route('/promo')
def promo():
	return render_template('promo.html')

