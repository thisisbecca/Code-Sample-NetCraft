from tkinter import *
from tkinter import messagebox
import sqlite3

def openAppointmentPopup(appointment_id, role):

    """
    opens a popup window showing the details of a specific appointment
    allows editing depending on the users role
    -recpetionist can edit all fields
    -dentist can only edit notes
    """

    win= Toplevel()
    win.title('Appointment Details')
    win.geometry('500x420')
    win.config(bg='white')

    #fetch all appointment info and patient
    conn = sqlite3.connect('testing.db')
    c=conn.cursor()
    c.execute('''
        SELECT a.date, a.time, a.type, a.notes, a.dentist_username,
              p.firstName, p.lastName, p.dob
        FROM appointments a
        JOIN patients p ON a.patient_id = p.patient_id
        WHERE a.appointment_id=?
    ''', (appointment_id,))
    row = c.fetchone()
    conn.close()

    if not row:
        messagebox.showerror('Error','Appointment not found')
        win.destroy()
        return
     
    #unpack database row into variables
    date, time, atype, notes, dentist, fname, lname, dob = row

    Label(win, text=f'Editing appointment for {fname.capitalize()} {lname.capitalize()}', font=('Verdana' , 16,'bold'),bg='white').pack(pady=10)

    #holds feilds neatly
    form = Frame(win, bg='white')
    form.pack(pady=10)

    info = [
        ('Date (YYYY-MM-DD)', date),
        ('Time (HH:MM)',time),
        ('Type',atype),
        ('Dentist',dentist),
    ]

    #dictionary to store entry widgets by label name
    entries = {}

    #create a label and entry for each appointment field 
    for i, (label, value) in enumerate(info):
        Label(form, text=label,bg='white').grid(row=i,column=0,sticky='e',padx=5,pady=5)
        e = Entry(form, width=30)
        e.grid(row=i,column=1,pady=5)
        e.insert(0, value or '')
        entries[label] = e

    Label(win, text='Notes: ',font=('Verdana',11,'bold'),bg='white').pack(anchor='w',padx=30,pady=(10,0))

    notesBox = Text(win,height=5,font=('Verdana',10))
    notesBox.pack(padx=30, fill=X)
    notesBox.insert('1.0',notes or '')


    #permission handling
    #recpetionist can edit everything
    canEditAll = role == 'Receptionist'
    #dentist and recpeitoniswt can edit the notes 
    canEditNotes = role == 'Dentist' or role == 'Receptionist'

    #lock edits if user isnt allowed to have full permissions
    if not canEditAll:
        for label in('Date (YYYY-MM-DD)', 'Time (HH:MM)', 'Type','Dentist'):
            entries[label].config(state='readonly')

    #lock notes if not allowed
    if not canEditNotes:
        notesBox.config(state='disabled')

    def saveChanges():

        """
        saves changes to the appointment
        dentists can only update notes
        receptionist can update all appoitnment details
        """

        newNotes = notesBox.get('1.0',END).strip()
        
        conn = sqlite3.connect('testing.db')
        c = conn.cursor()
        
        #update notes only
        if role == 'Dentist':
            c.execute('''
                UPDATE appointments
                SET notes=?
                WHERE appointment_id=?
            ''', (newNotes, appointment_id))

            #receptionist update all editiable fiedls
        else:
            #collect updated date from entry widgets7
            data = {k: v.get().strip() for k,v in entries.items()}

            if not data['Date (YYYY-MM-DD)'] or not data['Time (HH:MM)']:
                messagebox.showerror('Error', 'Date and time are required')
                conn.close()
                return
            
            c.execute('''
                UPDATE appointments
                SET date=?, time=?,type=?,dentist_username=?,notes=?
                WHERE appointment_id=?
            ''', (
                data['Date (YYYY-MM-DD)'],
                data['Time (HH:MM)'],
                data['Type'],
                data['Dentist'],
                newNotes,
                appointment_id
            ))

        conn.commit()
        conn.close()

        messagebox.showinfo('Success',' Appointment updated succesfully')
        win.master.event_generate('<<RefreshCalendar>>')
        win.destroy()

    def deleteAppointment():

        """
        deletes the appointment
        only available to receptionists
        """

        if not messagebox.askyesno('Confirm','Cancel this appointment?'):
            return
        
        conn = sqlite3.connect('testing.db')
        c=conn.cursor()

        c.execute('DELETE FROM appointments WHERE appointment_id=?',(appointment_id,))
        conn.commit()
        conn.close()

        messagebox.showinfo('Deleted','Appointment cancelled')
        win.master.event_generate('<<RefreshCalendar>>')
        win.destroy()

 
    saveButton = Button(win, text='Save Changes', bg='#bdd0d6',command=saveChanges)
    deleteButton = Button(win, text='Cancel Appointment', bg='#ffb3b3',command=deleteAppointment)

    #only show delete button to users who have permissions
    saveButton.pack(pady=10)
    if canEditAll:
        deleteButton.pack(pady=5)
