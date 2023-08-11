import csv
import datetime
import os.path
import subprocess
import tkinter as tk
import cv2
import util
from PIL import Image, ImageTk
import pandas as pd


class App:
    def __init__(self):

        # Main Tkinter Window
        self.main_window = tk.Tk()
        self.main_window.geometry("900x520+350+100")

        # Exit Button
        self.exit_button_main = util.exit_button(
            self.main_window, 'Exit', 'red', self.exit)
        self.exit_button_main.place(x=740, y=20)

        # Login Button
        self.login_button_main = util.get_button(
            self.main_window, 'Login', 'green', self.login)
        self.login_button_main.place(x=600, y=200)

        # LogOut Button
        self.login_button_main = util.get_button(
            self.main_window, 'Logout', 'brown', self.logout)
        self.login_button_main.place(x=600, y=300)

        # Register Button
        self.register_button_main = util.get_button(
            self.main_window, 'Register a New User', 'blue', self.register)
        self.register_button_main.place(x=600, y=400)

        # Webcam Positioning on Main Window
        self.webcam_label = util.get_img_label((self.main_window))
        self.webcam_label.place(x=10, y=0, width=500, height=500)

        # Adding webcam on Tkinter Window
        self.add_webcam(self.webcam_label)

        # Path of directory containing a Database of
        # Images of different registered users
        self.db_dir = './database'
        #  If path doesn't exist => no Database => We create one
        if not os.path.exists(self.db_dir):
            os.mkdir(self.db_dir)

        # making directory to store csv files as attendance
        self.csv_dir = './attendance'
        if not os.path.exists(self.csv_dir):
            os.mkdir(self.csv_dir)

        self.csv_dir = self.csv_dir + '/'
        # we use this date to manage all the files created by the program
        self.curr_date = datetime.datetime.now().strftime("%Y-%m-%d")

        # function to open all csv files
        self.open_csv()

        # names list. it will be updated constantly so that a person already logged in,
        # cannot log in again: cannot update the check-in time or create a duplicate entry
        # a person no having logged in shall not be able to log himself/herself out
        self.names = []

    def open_csv(self):
        # function to open csv files for constant editing by the program
        # if files don't exist, then they are created
        self.file_login = self.csv_dir + self.curr_date + '_Login.csv'
        self.fin = open(self.file_login, 'w+', newline='')
        self.file_logout = self.csv_dir + self.curr_date + '_Logout.csv'
        self.fout = open(self.file_logout, 'w+', newline='')

    # Function to add Webcam
    def add_webcam(self, label):
        if 'cap' not in self.__dict__:
            self.cap = cv2.VideoCapture(0)

        self._label = label
        self.process_webcam()

    def process_webcam(self):
        # ret is the signal whereas
        # frame is the image
        ret, frame = self.cap.read()
        self.most_recent_capture_arr = frame

        # converting image from 2d array of pixels to Pillow format
        img_ = cv2.cvtColor(self.most_recent_capture_arr, cv2.COLOR_BGR2RGB)
        self.most_recent_capture_pil = Image.fromarray(img_)

        imgtk = ImageTk.PhotoImage(image=self.most_recent_capture_pil)

        self._label.imgtk = imgtk
        self._label.configure(image=imgtk)

        # Repeating the process recursively after every 20ms
        self._label.after(20, self.process_webcam)

    def start(self):
        # starts main window with infinite loop
        self.main_window.mainloop()

    # Function to exit: generates a final csv file with both Login and logout time
    def exit(self):
        self.exit_window = tk.Toplevel(self.main_window)
        self.exit_window.geometry("500x300+580+250")

        # Text indicating that Admin has to enter the password
        self.text_label_exit = util.get_text_label(self.exit_window, 'Dear Admin,\nPlease enter the Password: ')
        self.text_label_exit.place(x=70, y=20)

        # Taking Password as Input
        self.password_input = util.get_password(self.exit_window)
        self.password_input.place(x=70, y=100, height=60, width=250)

        # Submit Button
        self.submit_exit_window_button = util.exit_button(
            self.exit_window, 'Submit', 'green', self.submit_password)
        self.submit_exit_window_button.place(x=70, y=220)

        # Go Back Button
        self.go_back_window_button = util.exit_button(
            self.exit_window, 'Go Back', 'blue', self.go_back)
        self.go_back_window_button.place(x=200, y=220)

    # Go Back Button Function
    def go_back(self):
        self.exit_window.destroy()

    def check_password(self, pass_input):
        password = "qwertyuiop"
        ret = 0
        if pass_input == "":
            util.msg_box('No Password', 'Please enter password to proceed :(')
            return ret
        elif pass_input != password:
            util.msg_box('Wrong Password', 'Submitted password is Incorrect :(')
            return ret
        else:
            ret = 1
            return ret

    # Submit Button Function
    def submit_password(self):

        # get password from tk.Entry widget
        pass_input = self.password_input.get()

        if self.check_password(pass_input):
            # when password provided is correct
            try:
                self.compiling_attendance()
            except:
                self.open_csv()
                # incase one or both the files (login-logout) are empty
                util.msg_box('File Empty', 'No New logins-logouts have taken place since last compilation.'
                                           '\n\nFiles Empty!')

    def compiling_attendance(self):
        # closing the previously open csv files
        self.fin.close()
        self.fout.close()
        # assign header columns
        headerList_login = ['Name', 'CheckIn_Time']
        headerList_logout = ['Name', 'CheckOut_Time']

        # update file to provide a header
        self.update_csv(self.file_login, headerList_login)
        self.update_csv(self.file_logout, headerList_logout)

        # creating separate dataframes for login and log out files
        df1 = pd.read_csv(self.file_login)
        df2 = pd.read_csv(self.file_logout)

        # how='left helps us retain all the values(names/ids) that have logged-in
        # but have forgotten to log themselves out
        merged_df = pd.merge(df1, df2, how='left', on=["Name"])

        # we dropped the first row because it was repeated
        merged_df.drop(0)

        # Index should start from 1
        merged_df.index += 1

        # file name of the final attendance
        file = self.csv_dir + '/' + self.curr_date + '.csv'
        merged_df.to_csv(file, index_label="Index")
        util.msg_box('Attendance',
                     "Attendance for the day has be compiled successfully!"
                     "\nYou may find the file at the storage!\nThank You")

        # removing the login and logout file as a new merged file has been generated
        os.remove(self.file_login)
        os.remove(self.file_logout)

        # exit commands
        self.exit_window.destroy()
        self.main_window.destroy()

    # update csv files and provide them with a suitable header
    def update_csv(self, file_name, header):
        # Read all lines of csv file as list of lists
        with open(file_name, 'r') as fileObj:
            readerObj = csv.reader(fileObj)
            listOfRows = list(readerObj)
        # Open csv file
        with open(file_name, 'w') as fileObj:
            writerObj = csv.writer(fileObj)
            # Add header to csv file
            writerObj.writerow(header)
            # Add list of lists as rows to the csv file
            writerObj.writerows(listOfRows)

    # Function to log in a user
    def login(self):
        # To compare two images, we need to
        # first take the recent capture of the user
        # and save it as tmp.jpg
        unknown_img_path = './tmp.jpg'
        # saving the recent capture using cv2 as tmp.jpg
        cv2.imwrite(unknown_img_path, self.most_recent_capture_arr)

        # Comparing the recent capture with our database
        output = subprocess.check_output(['face_recognition', self.db_dir, unknown_img_path])
        # print(output)
        # Parsing Output
        user_name = output.split(b',')[1][:-2].decode()

        if user_name == 'no_persons_found':
            util.msg_box('No Person Found', 'Please align your face with the camera.\nThank You!')

        elif user_name == 'unknown_person':
            util.msg_box('Unknown User', 'Please Register yourself and try again.\nThank You!')

        else:
            # user_name = user_name.capitalize()
            # print(user_name)

            if user_name not in self.names:
                util.msg_box('Welcome', f'Welcome back {user_name}!')
                self.names.append(user_name)
                curr_time = datetime.datetime.now().strftime("%H-%M-%S")
                csv.writer(self.fin).writerow([user_name, curr_time])

            else:
                util.msg_box('Already Logged In', f'Dear {user_name}, you are already logged in!')

        # Deleting tmp.jpg as the comparison is complete
        os.remove(unknown_img_path)

    # Function to log out a user

    def logout(self):
        unknown_img_path = './tmp.jpg'
        # saving the recent capture using cv2 as tmp.jpg
        cv2.imwrite(unknown_img_path, self.most_recent_capture_arr)

        # Comparing the recent capture with our database
        output = subprocess.check_output(['face_recognition', self.db_dir, unknown_img_path])
        # print(output)
        # Parsing Output
        user_name = output.split(b',')[1][:-2].decode()

        if user_name == 'no_persons_found':
            util.msg_box('No Person Found', 'Please align your face with the camera.\nThank You!')

        elif user_name == 'unknown_person':
            util.msg_box('Unknown User', 'Please Register yourself and try again.\nThank You!')

        else:
            # user_name = user_name.capitalize()
            # print(user_name)

            if user_name in self.names:
                self.names.remove(user_name)
                curr_time = datetime.datetime.now().strftime("%H-%M-%S")
                csv.writer(self.fout).writerow([user_name, curr_time])

                util.msg_box('Logout', f'Have a nice day {user_name}!')

            else:
                util.msg_box('Not Logged In', f'Dear {user_name}, you haven\'t logged in today!')

    # Function to register a New User
    def register(self):
        # Declaring the new window for registering new users
        self.register_new_user_window = tk.Toplevel(self.main_window)
        self.register_new_user_window.geometry("900x520+370+120")

        # Accept Button
        self.accept_register_window_button = util.get_button(
            self.register_new_user_window, 'Accept', 'green', self.accept_register_new_user)

        self.accept_register_window_button.place(x=600, y=300)

        # Try Again Button
        self.tryAgain_register_window_button = util.get_button(
            self.register_new_user_window, 'Go Back', 'red', self.tryAgain_register_new_user)

        self.tryAgain_register_window_button.place(x=600, y=400)

        # Capturing the Image of new user
        self.capture_label = util.get_img_label(self.register_new_user_window)
        self.capture_label.place(x=10, y=0, width=500, height=500)

        self.add_img_to_label(self.capture_label)

        # Taking the name of new user as Input
        self.entry_text_new_user = util.get_entry_text(self.register_new_user_window)
        self.entry_text_new_user.place(x=600, y=150)

        # Text indicating that the new user has to enter his name
        self.text_label_register = util.get_text_label(self.register_new_user_window, 'Please\nEnter your Name: ')
        self.text_label_register.place(x=600, y=60)

    def add_img_to_label(self, label):
        imgtk = ImageTk.PhotoImage(image=self.most_recent_capture_pil)

        label.imgtk = imgtk
        label.configure(image=imgtk)
        self.register_new_user_capture = self.most_recent_capture_arr.copy()

    def accept_register_new_user(self):
        name = self.entry_text_new_user.get(1.0, "end-1c")
        # Saving the captured image to our database with its name as INPUT NAME
        cv2.imwrite(os.path.join(self.db_dir, '{}.jpg'.format(name)), self.register_new_user_capture)

        # Prompt the user that he is successfully registered
        util.msg_box('Successfully Registered', f'Congrats {name}!!\nYou have been registered successfully!')
        self.register_new_user_window.destroy()

    # If User is not satisfied with the Picture,
    # he/she may go back and get a new one clicked!
    def tryAgain_register_new_user(self):
        self.register_new_user_window.destroy()


if __name__ == '__main__':
    app = App()
    app.start()
