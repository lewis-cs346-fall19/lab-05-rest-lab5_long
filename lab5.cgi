#! /usr/bin/python3
# -*- coding: UTF-8 -*-

import cgi
import os
import json
import MySQLdb
import passwords

#import cgitb
#cgitb.enable()

form = cgi.FieldStorage()

def play_list():
    set_type_json()

    db = getdb()
    db_json = json.dumps(db, indent=2)
    
    print(db_json)

def set_type_json():
    print("Content-type: application/json")
    print("Status: 200 OK")
    print()


def set_type_html():
    print("Content-type: text/html")
    print("Status: 200 OK")
    print()

def setConn():
    conn = MySQLdb.connect(host = passwords.SQL_HOST,
                       user = passwords.SQL_USER,
                       passwd = passwords.SQL_PASSWD,
                       db = "zhiyu_long")
    return conn

def getID():
    conn = setConn()
    cursor = conn.cursor()
    try:
        cursor.execute('SELECT id from play_list;')
        ids = cursor.fetchall()
    except:
        ids = []
    cursor.close()
    conn.commit()
    conn.close()

    return [i[0] for i in ids]

def getdb():
    conn = setConn()
    cursor = conn.cursor()
    try:
        cursor.execute("SHOW columns from play_list;")
        fields = cursor.fetchall()
        cursor.close()
        cursor = conn.cursor()
        cursor.execute("SELECT * from play_list;")
        records = cursor.fetchall()
    except:
        fields =  []
        records = []

    cursor.close()
    conn.commit()
    conn.close()
    
    fields = [fie[0] for fie in fields]
    db = []
    for rec in records:
        dic = {}
        index = 0
        id = 0
        for fie in fields:
            if fie == 'id':
                id = rec[index]
                val = id
            else:
                val = str(rec[index])
            tmp = {fie:val}
            dic.update(tmp)
            index += 1
        dic.update({'url':f'http://ec2-54-89-190-70.compute-1.amazonaws.com/cgi-bin/lab5.cgi/play_list/{id}'})
        db.append(dic)
    return db
    

def singleObj(ID):
    set_type_json()
    
    conn = setConn()
    cursor = conn.cursor()
    
    
    cursor.execute('SELECT * from play_list WHERE id='+ID+';')    
    obj = cursor.fetchall()[0]
    cursor.close()
    cursor = conn.cursor()
    cursor.execute("SHOW columns from play_list;")
    fields = [i[0] for i in cursor.fetchall()]
    cursor.close()
    conn.commit()
    conn.close()
    
    dic = {}
    id = 0
    for i in range(len(fields)):
        if fields[i] == 'id':
            val = obj[i]
            id = val
        else:
            val = str(obj[i])
        dic.update({fields[i]:val})
    dic.update({'url':f'http://ec2-54-89-190-70.compute-1.amazonaws.com/cgi-bin/lab5.cgi/play_list/{id}'})
    obj_json = json.dumps([dic], indent=2)
    print(obj_json)  

def post():
    set_type_html()
    print('''
    <form action = 'tmppost' method='post'>
        <p>song name:<br>
        <input type='text' name='song_name'><br>
        <p>artist:<br>
        <input type='text' name='artist'><br>
        <p>release_date:<br>
        <input type='text' name='date'><br>
        <input type='submit'>
    </form>
    ''')

def insert(name, artist, date):
    conn = setConn()
    cursor = conn.cursor()
    
    cursor.execute(f'''
         INSERT INTO play_list (song_name, artist, release_date)
         VALUES ('{name}', '{artist}', '{date}');
         ''')
    
    new_id = cursor.lastrowid
    cursor.close()
    conn.commit()
    conn.close()
    
     
    print("Status: 302 Redirect")
    print(f"Location: play_list/{new_id}")
    print()
    
def trampoline():
    print("Status: 302 Redirect")
    print("Location: landing_pad")
    print()

def landing_pad():
    print("Status: 200 OK")
    print("Content-type: text/html")
    print()

    print("This is the landing pad, after the redirect")    

def mainpage():
    set_type_html()
    print ('<html>')
    print ('<head>')
    print ('<meta charset="utf-8">')
    print ('<title>REST</title>')
    print ('</head>')
    print ('<body>')
    print ('''
    <h2>Play list (REST): Main links</h2>
    <p><a href="http://ec2-54-89-190-70.compute-1.amazonaws.com/cgi-bin/lab5.cgi/play_list/">play list</a>/ (GET)
    
    <br><a href="http://ec2-54-89-190-70.compute-1.amazonaws.com/cgi-bin/lab5.cgi/new_song">new play list form</a> (form, will POST to play_list)

    <p><a href="http://ec2-54-89-190-70.compute-1.amazonaws.com/cgi-bin/lab5.cgi/">back to the root of this REST site</a>
    ''')
    print ('</body>')
    print ('</html>')

if "PATH_INFO" in os.environ:
    pathinfo = os.environ["PATH_INFO"]
else:
    pathinfo = "/"


if pathinfo == "/":
    mainpage()

elif pathinfo == '/play_list' or pathinfo == '/play_list/':
    play_list()

elif pathinfo == "/trampoline":
    trampoline()
elif pathinfo == "/landing_pad":
    landing_pad()

elif pathinfo == '/new_song':
    post()

else:
    ids = getID()
    if pathinfo in ['/play_list/'+str(i) for i in ids]:
        singleObj(pathinfo.split('/')[-1])
    elif pathinfo[-1]=='/' and pathinfo[:-1] in ['/play_list/'+str(i) for i in ids]:
        singleObj(pathinfo.split('/')[-2])
    
    elif form.getvalue('song_name') and form.getvalue('artist') and form.getvalue('date'):
        insert(form.getvalue('song_name'), form.getvalue('artist'), form.getvalue('date'))

    else:

        set_type_html()
        print('PATH_INFO: '+ pathinfo)
        print('<br><b>ERROR:</b> Unrecognized path: '+pathinfo)
        
        print ('''
            <br>
            <p><a href="http://ec2-54-89-190-70.compute-1.amazonaws.com/cgi-bin/lab5.cgi/play_list/">play list</a>/ (GET)
            <br><a href="http://ec2-54-89-190-70.compute-1.amazonaws.com/cgi-bin/lab5.cgi/new_song">new play list form</a> (form, will POST to play_list)

            <p><a href="http://ec2-54-89-190-70.compute-1.amazonaws.com/cgi-bin/lab5.cgi/">back to the root of this REST site</a>
            ''')
