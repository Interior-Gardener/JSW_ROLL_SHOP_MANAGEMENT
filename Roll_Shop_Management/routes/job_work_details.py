from flask import Blueprint, request, render_template, session, redirect, url_for
import os
import pandas as pd
from config import UPLOAD_FOLDER
from utils.validation import validate_excel
from utils.submission import submit_to_db

bp = Blueprint('job_work_details', __name__)

@bp.route('/job_work_details.html')
def job_work_details():
    if 'employeeid' not in session:
        return redirect(url_for('login'))
    return render_template('job_work_details.html', employeeid=session['employeeid'])