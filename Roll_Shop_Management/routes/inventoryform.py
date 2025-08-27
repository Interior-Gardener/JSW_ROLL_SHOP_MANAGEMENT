from flask import Blueprint, request, render_template, session, redirect, url_for
import os
import pandas as pd
from config import UPLOAD_FOLDER
from utils.validation import validate_excel
from utils.submission import submit_to_db

bp = Blueprint('inventoryform', __name__)


@bp.route('/inventoryform.html')
def inventoryform():
    if 'employeeid' not in session:
        return redirect(url_for('login'))
    return render_template('inventoryform.html', employeeid=session['employeeid'])