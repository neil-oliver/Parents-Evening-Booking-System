#parents evening booking system
import allparents
import datetime
import time
import sqlite3
import json


#lets start playing with databases
db = sqlite3.connect('bookingdb')

#parents evening start and end time with slot length in minutes
date = datetime.date(2018, 7, 7)
start = datetime.datetime(2018,7,7,14,0,0)
end = datetime.datetime(2018,7,7,19,30,0)
slotLength = 5

#Flags
goodParent = False
maxBookings = 0 # 0 is null
calculateMax = False
verboseBookings = True
fillGaps = False

#global booking dicts
teacherBookings ={}
parentBookings ={}

def addTeacher(teacherName, teacherStart, teacherFinish):
    teacherBookings[teacherName] = {}
    slots = []
    time = start
    while time != end + datetime.timedelta(minutes=slotLength):
        slots.append(time)
        time = time + datetime.timedelta(minutes=slotLength)
    for slotIndex, slot in enumerate(slots):
        if slot < teacherStart or slot > teacherFinish:
            teacherBookings[teacherName][slot] = "x"
        else:
            teacherBookings[teacherName][slot] = ""


def addParent(parentName, parentStart, parentFinish, teachers):
    parentBookings[parentName] = [{},[],[]]
    slots = []
    time = start
    while time != end + datetime.timedelta(minutes=slotLength):
        slots.append(time)
        time = time + datetime.timedelta(minutes=slotLength)
    for slotIndex, slot in enumerate(slots):
        if slot < parentStart or slot > parentFinish:
            parentBookings[parentName][0][slot] = "x"
        else:
            parentBookings[parentName][0][slot] = ""
    parentBookings[parentName][1] = teachers

    for teacher in teachers:
        parentBookings[parentName][2].append(teacher)


def userParent():
    name = str(input("Please enter your title and surname \n"))
    start = str(input("Please enter your start time in the format 17:00 \n"))
    end = str(input("Please enter your finish time in the format 19:00 \n"))
    teachers = []
    while True:
        teacher = str(input("Please enter the name of a teacher you wish to see. When you are finished, type done. \n"))
        if teacher != "done":
            teachers.append(teacher)
        else:
            break
    startHour, startMinute = start.split(":",1)
    endHour, endMinute = end.split(":",1)
    parentStart = datetime.datetime.combine(date, datetime.time(int(startHour), int(startMinute), 0))
    parentFinish = datetime.datetime.combine(date, datetime.time(int(endHour), int(endMinute), 0))

    addParent(name,parentStart,parentFinish,teachers)


def printBookings(booking, parent):
    print("\n")

    if parent == True:
        for p in booking:
            print("Parent: " + p)
            for s in booking[p][0]:
                print(str(s) + " - '" + booking[p][0][s] + "'")
            print("\n")


    else:
        for t in booking:
            print("Teacher: " + t)
            for s in booking[t]:
                print(str(s) + " - '" + booking[t][s] + "'")
            print("\n")


def menu():
    while True:
        parent = input("Would you like to input a parents details? \n").lower()
        if parent == "yes" or parent == "y":
            userParent()
        else:
            option = int(input("Please select from the following options: \n1. First Come First Served Booking \n2. Parent Priority FCFS Booking \n3. Teacher Priority Booking \n4. Whatever is currently being tested! \n"))
            if option == 1:
                print("Running Booking Algorythm... \n")
                time.sleep(1)
                fcfsBooking()
                break
            elif option == 2:
                print("Running Booking Algorythm... \n")
                time.sleep(1)
                parentPriorityBooking()
                break
            elif option == 3:
                print("Running Booking Algorythm... \n")
                time.sleep(1)
                teacherPriorityBooking()
                break
            elif option == 4:
                print("Running Booking Algorythm... \n")
                time.sleep(1)
                createDatabases(drop=True)
                importParents()
                importTeachers()
                break
            else:
                print("We did not understand your option selection.")


def fcfsBooking():
    #First come first served booking process.
    #Each parent is given all appointments in order of subject priority before the next parent is 'served'.
    for parent in parentBookings:
        for teacher in parentBookings[parent][1]:
            if teacher in teacherBookings:
                booking = False
                for slot in teacherBookings[teacher]:
                    if teacherBookings[teacher][slot] == "" and parentBookings[parent][0][slot] == "":
                        parentBookings[parent][0][slot] = teacher
                        teacherBookings[teacher][slot] = parent
                        print(parent + " has made a booking with " + teacher + " at " + str(slot))
                        booking = True
                        break

                if booking != True:
                    print("A booking has not been achieved for " + parent + " with " + teacher + ".")

            else:
                print(parent + " has requested a booking with " + teacher + ", however " + teacher + " is not available for bookings on this event.")

    fitness()


def parentPriorityBooking():
    #Each parents is given their first priority subject and then the next parent is served. Continues to 2nd priority, then 3rd etc.
    v = verboseBookings
    bookings = 1
    parentBookingCount = {}

    # Choose whether to book parents based on how few bookings their require and how flexible their availability is.
    if goodParent == True:
        Parents = rateMyParent()
    else:
        Parents = parentBookings

    while bookings > 0:
        bookings = 0

        #iterate through the parents
        for parent in Parents:

            if goodParent == True:
                parent = parent[0]

            # add parent to the booking count
            if parent not in parentBookingCount:
                parentBookingCount[parent] = 0

            #check that parents still require a booking with a teacher
            if len(parentBookings[parent][2]) > 0:
                teacher = parentBookings[parent][2][0]

                #check that the teacher is available at the parents evening.
                if teacher in teacherBookings:
                    booking = False
                    for slot in parentBookings[parent][0]:
                        if teacherBookings[teacher][slot] == "" and parentBookings[parent][0][slot] == "":

                            # Check to see if max booking are in play
                            if maxBookings != 0:

                                # Check if parent has reached max bookings
                                if parentBookingCount[parent] < maxBookings:

                                    parentBookings[parent][0][slot] = teacher
                                    teacherBookings[teacher][slot] = parent
                                    if v == True:
                                        print(parent + " has made a booking with " + teacher + " at " + str(slot))
                                    bookings = bookings + 1
                                    parentBookings[parent][2].remove(teacher)
                                    booking = True
                                    # Increase individual parent booking count
                                    parentBookingCount[parent] = parentBookingCount[parent] + 1
                                    break
                            else:
                                parentBookings[parent][0][slot] = teacher
                                teacherBookings[teacher][slot] = parent
                                if v == True:
                                    print(parent + " has made a booking with " + teacher + " at " + str(slot))
                                bookings = bookings + 1
                                parentBookings[parent][2].remove(teacher)
                                booking = True
                                break

                    if booking != True:
                        if v == True:
                            print("A booking has not been achieved for " + parent + " with " + teacher + ".")
                        parentBookings[parent][2].remove(teacher)
                else:
                    if v == True:
                        print(parent + " has requested a booking with " + teacher + ", however " + teacher + " is not available for bookings on this event.")
                    parentBookings[parent][2].remove(teacher)

    fitness()


def teacherPriorityBooking():
    #Each teacher slot is filled from earliest to latest, selecting parents on priority order.
    #priority conflicts are resolved on a first come first served basis.
    #current issue: orders teachers by earliest first, but not earliest match with parent.
    v = verboseBookings
    parentBookingCount = {}

    # Choose whether to book parents based on how few bookings their require and how flexible their availability is.
    if goodParent == True:
        Parents = rateMyParent()
    else:
        Parents = parentBookings

    #if no bookings are made it runs the loop once more to
    #keep looping while bookings are being made
    bookings = 1
    while bookings > 0:
        bookings = 0

        #find the first available slot for each teacher. Order based on earliest slot.
        order = []
        for teacher in teacherBookings:
            for slot in teacherBookings[teacher]:
                if teacherBookings[teacher][slot] == "":
                    order.append([teacher, slot])
                    break
        order.sort(key=lambda teacher: teacher[1])

        #iterate through teachers from ordered.
        for teacher in order:
            teacher = teacher[0]

            #iterate through the list of all appointments of selected teacher.
            for slot in teacherBookings[teacher]:

                booking = False

                if teacherBookings[teacher][slot] == "":
                    #adds teachers next empty slot to 'nextAvail'
                    nextAvail = slot
                    bookingPriority = ["", float('inf')]

                    #loops through parents booking.
                    for parent in Parents:

                        if goodParent == True:
                            parent = parent[0]

                        # add parent to the booking count
                        if parent not in parentBookingCount:
                            parentBookingCount[parent] = 0

                        #checks to see if the parent has the slot free and if they are wanting an appointment with the teacher.
                        if parentBookings[parent][0][nextAvail] == "" and teacher in parentBookings[parent][2]:
                            # Check to see if max booking are in play
                            if maxBookings != 0:

                                # Check if parent has reached max bookings
                                if parentBookingCount[parent] < maxBookings:

                                    # if the parents subject priority is higher than a previous parent, the bookingPriority is updated with the new parent.
                                    if bookingPriority[1] > parentBookings[parent][2].index(teacher):

                                        bookingPriority = [parent, parentBookings[parent][2].index(teacher)]

                                    #sets the booking flag to true
                                    booking = True

                            else:
                                # if the parents subject priority is higher than a previous parent, the bookingPriority is updated with the new parent.
                                if bookingPriority[1] > parentBookings[parent][2].index(teacher):

                                    bookingPriority = [parent, parentBookings[parent][2].index(teacher)]

                                    # sets the booking flag to true
                                    booking = True

                #once all parents have been checked and ordered by priority. If a booking can be made it will
                if booking == True:

                    parentBookings[bookingPriority[0]][0][slot] = teacher
                    teacherBookings[teacher][slot] = bookingPriority[0]
                    if v == True:
                        print(bookingPriority[0] + " has made a booking with " + teacher + " at " + str(slot))
                    #delete the teacher from the booking request list and update the booking total.
                    parentBookings[bookingPriority[0]][2].remove(teacher)
                    bookings = bookings + 1
                    # Increase individual parent booking count
                    parentBookingCount[bookingPriority[0]] = parentBookingCount[bookingPriority[0]] + 1

    #use a more basic setup to fill any gaps in teachers availability
    if fillGaps == True:
        for teacher in teacherBookings:
            for slot in teacherBookings[teacher]:
                if teacherBookings[teacher][slot] == "":
                    for parent in parentBookings:
                        if teacher in parentBookings[parent][2]:
                            parentBookings[parent][0][slot] = teacher
                            teacherBookings[teacher][slot] = parent
                            if v == True:
                                print(parent + " has made a booking with " + teacher + " at " + str(slot))
                            # delete the teacher from the booking request list and update the booking total.
                            parentBookings[parent][2].remove(teacher)

    #once all bookings have been made, cleanup and print error messages. Deleting teachers from the booking request lists as you go.
    for parent in parentBookings:
        for teacher in parentBookings[parent][2]:

            #check to see if a teacher is in the teacher booking list. If not, they are not attending the event.
            if teacher not in teacherBookings:
                if v == True:
                    print(parent + " has requested a booking with " + teacher + ", however " + teacher + " is not available for bookings on this event.")
            else:
                full = True
                #check for any empty bookings for any teachers remaining in parents booking request lists. Change flag if empty slots found.
                for booking in teacherBookings[teacher]:
                    if teacherBookings[teacher][booking] == "":
                        full = False

                if full == True:
                    if v == True:
                        print("A booking has not been achieved for " + parent + " with " + teacher + " as they are fully booked.")
                else:
                    if v == True:
                        if maxBookings != 0 and parentBookingCount[parent] == maxBookings:
                            print("A booking has not been achieved for " + parent + " with " + teacher + ". Maximum booking per parent reached.")
                        else:
                            possible = False
                            for slot in parentBookings[parent][0]:
                                if parentBookings[parent][0][slot] == "" and teacherBookings[teacher][slot] == "":
                                    possible = True

                            if possible == True:
                                print("Error: A booking was possible for " + parent + " with " + teacher + " but it was missed for an unknown reason.")
                            else:
                                print("A booking has not been achieved for " + parent + " with " + teacher + ". Please try extending your availability or booking at an earlier date.")
            #remove any remaining teachers in the booking request list.
            parentBookings[parent][2].remove(teacher)

    fitness()


def calculateMaxBookings():
    global maxBookings
    total = 0
    for teacher in teacherBookings:
        for slot in teacherBookings[teacher]:
            if teacherBookings[teacher][slot] == "":
                total = total + 1

    maxBookings = int(total / len(parentBookings))

    #print("A new Maximum per parent booking calculated and set to " + str(maxBookings))


def rateMyParent():
    order = []
    for parent in parentBookings:

        #rate number of slots
        count = 0
        for slot in parentBookings[parent][0]:
            if parentBookings[parent][0][slot] != "x":
                count = count + 1

        #calculate request to slot ratio
        order.append([parent, count / len(parentBookings[parent][1])])

    order.sort(key=lambda parent: parent[1], reverse=True)
    return order


def fitness():
    #currently only working for FCFS

    print("")
    #parents requests fitness

    totalBookingCount = 0

    #teacher requests fitness
    teacherPossible = 0
    teacherUnbooked = 0
    for teacher in teacherBookings:
        for booking in teacherBookings[teacher]:
            if teacherBookings[teacher][booking] == "":
                teacherPossible = teacherPossible + 1
                teacherUnbooked = teacherUnbooked + 1
            elif teacherBookings[teacher][booking] != "x":
                teacherPossible = teacherPossible + 1

    totalBookingCount = teacherPossible - teacherUnbooked

    print("A total of " + str(teacherPossible) + " possible booking slots were available and " + str(totalBookingCount) + " bookings were made. This is an average of " + str(((teacherPossible-teacherUnbooked) / teacherPossible)*100) + "%")

    #first choice fitness
    firstChoice = 0
    for parent in parentBookings:
        for booking in parentBookings[parent][0]:
            if parentBookings[parent][1][0] == parentBookings[parent][0][booking]:
                 firstChoice = firstChoice + 1

    print( str(firstChoice) + " out of a total of " + str(len(parentBookings)) + " parents received their first choice in booking. This is an average of " + str((firstChoice / len(parentBookings))*100) + "%")


    #top 3 fitness
    top3 = 0
    for parent in parentBookings:

        gotBooking = [False, False, False]

        for booking in parentBookings[parent][0]:
            if parentBookings[parent][1][0] == parentBookings[parent][0][booking]:
                gotBooking[0] = True
            elif parentBookings[parent][1][1] == parentBookings[parent][0][booking]:
                gotBooking[1] = True
            elif parentBookings[parent][1][2] == parentBookings[parent][0][booking]:
                gotBooking[2] = True

        if gotBooking == [True, True, True]:
            top3 = top3 + 1

    print(str(top3) + " out of a total of " + str(len(parentBookings)) + " parents received their top 3 booking choices. This is an average of " + str((top3 / len(parentBookings)) * 100) + "%")



                #Calculate missed opportunities fitness
    missed = 0
    alreadyBooked = False

    for teacher in teacherBookings:
        for slot in teacherBookings[teacher]:
            if teacherBookings[teacher][slot] == "":
                alreadyBooked = False
                for parent in parentBookings:
                    if parentBookings[parent][0][slot] == "" and teacher in parentBookings[parent][1]:
                        for pslot in parentBookings[parent][0]:
                            if parentBookings[parent][0][pslot] == teacher:
                                alreadyBooked = True

                        if alreadyBooked == False:
                            missed = missed + 1

    print(str(missed) + " opportunities to match a parent and teacher were missed.")


#lets start to play with databases


def importParents():

    cursor = db.cursor()

    early = True

    for parent in allparents.booking:
        if early == True:
            start = datetime.datetime(2018, 7, 7, 14, 0, 0)
            end = datetime.datetime(2018, 7, 7, 19, 0, 0)
            early = False
        else:
            start = datetime.datetime(2018, 7, 7, 15, 30, 0)
            end = datetime.datetime(2018, 7, 7, 19, 30, 0)
            early = True

        cursor.execute('''INSERT INTO parents(name, start, end, requests, created_at) VALUES(?,?,?,?,?)''', (
            parent, start, end, json.dumps(allparents.booking[parent]), datetime.datetime.now()))

    db.commit()

    cursor.execute('''SELECT * FROM parents''')

    for row in cursor:
        print(row)


def importTeachers():
    #add blocked slots

    cursor = db.cursor()

    early = True

    for teacher in allparents.teachers:

        if early == True:
            start = datetime.datetime(2018, 7, 7, 14, 0, 0)
            end = datetime.datetime(2018, 7, 7, 19, 0, 0)
            early = False
        else:
            start = datetime.datetime(2018, 7, 7, 15, 30, 0)
            end = datetime.datetime(2018, 7, 7, 19, 30, 0)
            early = True

        cursor.execute('''INSERT INTO teachers(name, start, end) VALUES(?,?,?)''', (teacher, start, end))

    db.commit()

    cursor.execute('''SELECT * FROM teachers''')

    for row in cursor:
        print(row)

def createDatabases(drop=False):

    #setup teachers
    cursor = db.cursor()

    if drop == True:
        cursor.execute('''DROP TABLE teachers''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS teachers(teacherID INTEGER PRIMARY KEY, name TEXT, start DATE, end DATE, blocked TEXT, requests TEXT)''')

    #setup parents
    if drop == True:
        cursor.execute('''DROP TABLE parents''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS parents(parentID INTEGER PRIMARY KEY, name TEXT, start DATE, end DATE, requests TEXT, created_at DATE)''')

    #setup students
    if drop == True:
        cursor.execute('''DROP TABLE students''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS students(studentID INTEGER PRIMARY KEY, name TEXT, year INTEGER, tutor TEXT, parent1 INTEGER, parent2 INTEGER, teachers TEXT, FOREIGN KEY(parent1) REFERENCES parents(parentID), FOREIGN KEY(parent1) REFERENCES parents(parentID))''')

    #setup classes
    if drop == True:
        cursor.execute('''DROP TABLE classes''')
        cursor.execute('''DROP TABLE studentClass''')
        cursor.execute('''DROP TABLE teacherClass''')

    cursor.execute('''CREATE TABLE IF NOT EXISTS classes(classID TEXT PRIMARY KEY, notes TEXT)''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS studentClass(class TEXT, student INTEGER, FOREIGN KEY(class) REFERENCES classes(classID), FOREIGN KEY(student) REFERENCES students(studentID))''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS teacherClass(class TEXT, teacher INTEGER, FOREIGN KEY(class) REFERENCES classes(classID), FOREIGN KEY(teacher) REFERENCES teachers(teacherID))''')


    #setup bookings
    if drop == True:
        cursor.execute('''DROP TABLE bookings''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS bookings(id INTEGER PRIMARY KEY, slot TEXT, teacher INTEGER, parent INTEGER, notes TEXT, FOREIGN KEY(teacher) REFERENCES teachers(teacherID), FOREIGN KEY(parent) REFERENCES parents(parentID))''')



############################################################

#Setup

#create parents from SIMS export
allparents.createTestPeople()

early = True

for parent in allparents.booking:
    if early == True:
        addParent(parent, datetime.datetime(2018, 7, 7, 14, 0, 0),datetime.datetime(2018, 7, 7, 19, 0, 0), allparents.booking[parent])
        early = False
    else:
        addParent(parent, datetime.datetime(2018, 7, 7, 15, 30, 0),datetime.datetime(2018, 7, 7, 19, 30, 0), allparents.booking[parent])
        early = True

for teacher in allparents.teachers:
    if early == True:
        addTeacher(teacher, datetime.datetime(2018, 7, 7, 14, 0, 0), datetime.datetime(2018, 7, 7, 19, 0, 0))
        early = False
    else:
        addTeacher(teacher, datetime.datetime(2018, 7, 7, 15, 0, 0), datetime.datetime(2018, 7, 7, 19, 30, 0))
        early = True

# check if we need to calculate the highest maximum
if calculateMax == True:
    calculateMaxBookings()

############################################################

menu()

if verboseBookings == False:
    printBookings(teacherBookings, False)
    printBookings(parentBookings, True)

'''
Priority order for fitness score:
all subjects
subject priority
booking date priority
gaps (both parent and teacher)
intentional gaps (5 minute gaps for parents)

****** What if the person didn't get their first priority? (should they be next inline for their second choice? ******

'''



