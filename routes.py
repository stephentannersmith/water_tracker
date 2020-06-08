from config import app
from controller_functions import index, register_new_user, username, login_page, validate_login, success, add_entry, logout, edit_landing, update_prof

app.add_url_rule("/", view_func=index)
app.add_url_rule("/register", view_func=register_new_user, methods=["POST"])
app.add_url_rule("/email", view_func=username, methods=["POST"])
app.add_url_rule("/login_page", view_func=login_page)
app.add_url_rule("/login", view_func=validate_login, methods=["POST"])
app.add_url_rule("/home", view_func=success)
app.add_url_rule("/add_entry", view_func=add_entry, methods=["POST"])
app.add_url_rule("/logout", view_func=logout)
app.add_url_rule("/edit_profile", view_func=edit_landing)
app.add_url_rule("/update_user", view_func=update_prof, methods=["POST"])