# Face-Recognition-based-Attendance-System
A attendance system based on Face Recognition

This is a python program that registers its users/students/employees and saves their image in its database.
Upon each login, it matchs the face of the user trying to log in with its database.
If a match is found, the user_name [assuming it will be unique:  else use employee id/roll number or any id that is unique], and the log in time is updated
Same goes with the log out.

Finally when the admin exits the program, it generates a csv file with each user's id, check-in time and check-out time.
This csv file will be stored as the DATE, under the directory /attendance as /attendance/<DATE.csv>
Database will be managed under the directory /database

These 2 directories will be stored in the folder where this program is being kept and run from.

This program uses face_recognition, opencv2, pandas, Pillow and tkinter modules.
