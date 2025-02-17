from flask import Blueprint, render_template, redirect, url_for, flash, request
from urllib.parse import urlparse
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import check_password_hash

from models.models import Player
from crud.player import get_player_by_nick
from extensions import db

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        nick = request.form.get('nick')
        password = request.form.get('password')
        
        if not nick or not password:
            flash('Proszę wypełnić wszystkie pola!', 'error')
            return render_template('auth/login.html')

        player = get_player_by_nick(db.session, nick)
        if player and check_password_hash(player.password, password):
            login_user(player)
            flash('Zalogowano pomyślnie!', 'success')
            next_page = request.args.get('next', '')
            if next_page:
                next_page = next_page.replace('\\', '')
                if not urlparse(next_page).netloc and not urlparse(next_page).scheme:
                    return redirect(next_page)
            return redirect(url_for('index'))
        
        flash('Nieprawidłowy nick lub hasło!', 'error')
    
    return render_template('auth/login.html')

@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Zostałeś wylogowany.', 'info')
    return redirect(url_for('index'))