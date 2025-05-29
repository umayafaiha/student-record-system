import mysql.connector

def get_db_connection():
	connection=mysql.connector.connect(
		host="yamabiko.proxy.rlwy.net",
		user="root",
		password="SpLALXLnaPtuWSqZQKUxNMHYPdOONYwY",
		database="railway",
		port=30874
	)
	return connection