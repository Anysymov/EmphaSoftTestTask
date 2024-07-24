import datetime
from django.shortcuts import render
from django.db import connection
from django.utils import timezone
from rest_framework import generics
from .forms import FilterForm, LoginForm, OrderChoice, RegistrationForm, ReservationForm
from MainApp.models import Room, Reservation, User
from MainApp.serializers import RoomSerializer, UserSerializer, ReservationSerializer


class RoomList(generics.ListCreateAPIView):
    queryset = Room.objects.all()
    serializer_class = RoomSerializer

class RoomDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Room.objects.all()
    serializer_class = RoomSerializer

class UserList(generics.ListCreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer

class UserDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer

class Reservationist(generics.ListCreateAPIView):
    queryset = Reservation.objects.all()
    serializer_class = ReservationSerializer

class ReservationDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Reservation.objects.all()
    serializer_class = ReservationSerializer


def create_room(name, price, spots):
    Room.objects.create(name=name, price=price, spots=spots)


def create_user(username, full_name, password=None):
    User.objects.create(username=username, password=password, full_name=full_name)


def create_reservation(room, reserved_for, reservation_date):
    Reservation.objects.create(room=room, reserved_for=reserved_for, reservation_date=reservation_date)


def db_access(sql_query, result_needed=True):
    with connection.cursor() as cursor:
        cursor.execute(sql_query)

        if result_needed:
            result = cursor.fetchall()
            return result


def get_all_rooms_unfiltered(get_only_name=False):
    if get_only_name:
        rooms_query = 'SELECT name FROM public."MainApp_room"'

        table = db_access(rooms_query)

        return table
    else:
        rooms_query = 'SELECT name, price, spots FROM public."MainApp_room"'

        table = db_access(rooms_query)

        new_table = []

        for room in table:
            room_name = f"'{room[1]}'"
            second_query = f'SELECT reservation_date FROM public."MainApp_reservation" WHERE room = {room_name}'
            result = db_access(second_query)

            new_room_data = list(room)

            if len(result) > 0:
                new_room_data.append(result)

            new_table.append(new_room_data)

        return new_table


def get_rooms_by_filter(filter=None, get_only_name=False):
    if filter is None:
        table = get_all_rooms_unfiltered()

        new_table = []

        for room in table:
            room_name = f"'{room[0]}'"
            second_query = f'SELECT reservation_date FROM public."MainApp_reservation" WHERE room = {room_name}'
            result = db_access(second_query)
            
            new_room_data = list(room)
            current_list = []

            if len(result) > 0:
                for day in result:
                    date_to_append = day[0]
                    current_list.append(date_to_append)

            new_room_data.append(current_list)
            new_table.append(new_room_data)
    
        return new_table

    else:
        sql_queries = []

        if "spots_min" in filter:
            spots_min = filter.get("spots_min")
            query_extension = f" spots >= {spots_min}"
            sql_queries.append(query_extension)
        
        if "spots_max" in filter:
            spots_max = filter.get("spots_max")
            query_extension = f" spots <= {spots_max}"
            sql_queries.append(query_extension)

        if "price_min" in filter:
            price_min = filter.get("price_min")
            query_extension = f" price >= {price_min}"
            sql_queries.append(query_extension)
        
        if "price_max" in filter:
            price_max = filter.get("price_max")
            query_extension = f" price <= {price_max}"
            sql_queries.append(query_extension)

        if "vacant_from" in filter or "vacant_untill" in filter:
            if "vacant_from" in filter and "vacant_untill" in filter:
                vacant_from = datetime.datetime.strptime(filter.get("vacant_from"), "%Y-%m-%d").date()
                vacant_untill = datetime.datetime.strptime(filter.get("vacant_untill"), "%Y-%m-%d").date()

                vacant_from = f"'{vacant_from}'"
                vacant_untill = f"'{vacant_untill}'"
                
                reservations_query = f'SELECT room FROM public."MainApp_reservation" WHERE reservation_date BETWEEN {vacant_from} AND {vacant_untill}'
            elif "vacant_from" in filter:
                vacant_from = datetime.datetime.strptime(filter.get("vacant_from"), "%Y-%m-%d").date()
                vacant_from = f"'{vacant_from}'"

                reservations_query = f'SELECT room FROM public."MainApp_reservation" WHERE reservation_date > {vacant_from}'
            else:
                vacant_untill = datetime.datetime.strptime(filter.get("vacant_untill"), "%Y-%m-%d").date()
                vacant_untill = f"'{vacant_untill}'"
                
                reservations_query = f'SELECT room FROM public."MainApp_reservation" WHERE reservation_date < {vacant_untill}'

            reservations = db_access(reservations_query)
            reservations_list = []

            for reservation in reservations:
                reservations_list.append(reservation[0])
            
            reservations_list = tuple(reservations_list)
            
            string_for_query = str(reservations_list)

            if string_for_query.endswith(",)"):
                reservations_list = string_for_query[:-2] + ")"

            if len(reservations_list) > 0:
                query_extension = f" name NOT IN {reservations_list}"
            
                sql_queries.append(query_extension)
        
        if "orderchoice" in filter and len(sql_queries) < 1:
            if get_only_name:
                rooms_query = 'SELECT name FROM public."MainApp_room"'
            else:
                rooms_query = 'SELECT name, price, spots FROM public."MainApp_room"'
        else:
            if get_only_name:
                rooms_query = 'SELECT name FROM public."MainApp_room" WHERE'
            else:
                rooms_query = 'SELECT name, price, spots FROM public."MainApp_room" WHERE'
        
        order_param = None
        
        if "orderchoice" in filter:
            orderchoice = filter.get("orderchoice")

            if orderchoice == "name_asc":
                order = "name ASC"
            elif orderchoice == "name_desc":
                order = "name DESC"
            elif orderchoice == "price_asc":
                order = "price ASC"
            elif orderchoice == "price_desc":
                order = "price DESC"
            elif orderchoice == "spots_asc":
                order = "spots ASC"
            elif orderchoice == "spots_desc":
                order = "spots DESC"
            
            order_param = f" ORDER BY {order}"

        if len(sql_queries) > 1:
            counter = len(sql_queries) - 1

            for i in sql_queries:
                rooms_query += i

                if counter > 0:
                    rooms_query += " AND"
                    counter -= 1
        elif len(sql_queries) == 1:
            rooms_query += sql_queries[0]
        elif len(sql_queries) < 1 and order_param is not None:
            pass
        else:
            rooms_query = 'SELECT name, price, spots FROM public."MainApp_room"'

        if order_param is not None:
            rooms_query += order_param
        
        table = db_access(rooms_query)


        if get_only_name:
            return table
        else:
            new_table = []

            for room in table:
                room_name = f"'{room[0]}'"
                second_query = f'SELECT reservation_date FROM public."MainApp_reservation" WHERE room = {room_name}'
                result = db_access(second_query)
                
                new_room_data = list(room)
                current_list = []

                if len(result) > 0:
                    for day in result:
                        date_to_append = day[0]
                        current_list.append(date_to_append)

                new_room_data.append(current_list)
                new_table.append(new_room_data)
        
            return new_table


def check_user(username=None, password=None, check_only_username=False):
    if username is None:
        return False
    else:
        username = f"'{username}'"
        password = f"'{password}'"

        if check_only_username:
            query = f'SELECT username, password FROM public."MainApp_user" WHERE username = {username}'
            user_check = db_access(query)
        else:
            query = f'SELECT username, password FROM public."MainApp_user" WHERE username = {username} AND password = {password}'
            user_check = db_access(query)

    if not user_check:
        return False
    else:
        return True


def form_rooms_list(filter=None, cookie_check=False):
    filterform = FilterForm
    orderchoice = OrderChoice

    rooms_list = []

    try:
        rooms_query = get_rooms_by_filter(filter)

        for room in rooms_query:
            if room[3] != []:
                rooms_list.append({"number": room[0], "price":room[1], "spots": room[2], "status": "Reserved for", "reservation_data": room[3]})
            else:
                rooms_list.append({"number": room[0], "price":room[1], "spots": room[2], "status": "Not reserved"})

    except:
        rooms_list = [{"number": None, "price": None, "spots": None, "status": None, "reservation_data": None}]
    
    user_status = cookie_check

    result = {"title": "Rooms list", "rooms_list": rooms_list, "user_status": user_status, "filters": filterform, "orderchoice": orderchoice}

    return result


def get_rooms_tuple():
    rooms_query = 'SELECT name FROM public."MainApp_room"'
    table = db_access(rooms_query)
    rooms_list = []

    for room in table:
        room_tuple = (room[0], room[0])
        rooms_list.append(room_tuple)
    
    rooms_tuple = tuple(rooms_list)

    return rooms_tuple


def get_dates_for_reservation(date1, date2):
    tz = timezone.get_current_timezone()

    date1 = timezone.make_aware(datetime.datetime.strptime(date1, '%Y-%m-%d'), tz)
    date2 = timezone.make_aware(datetime.datetime.strptime(date2, '%Y-%m-%d'), tz)

    return [date1 + datetime.timedelta(days=x) for x in range((date2-date1).days + 1)]


def rooms_list(request):
    try:
        username_cookie = request.COOKIES["username"]
        password_cookie = request.COOKIES["password"]
    except KeyError:
        username_cookie = None
        password_cookie = None

    cookie_check = check_user(username=username_cookie, password=password_cookie)

    if request.method == "POST":

        spots_min = request.POST.get("spots_min", "")
        spots_max = request.POST.get("spots_max", "")
        price_min = request.POST.get("price_min", "")
        price_max = request.POST.get("price_max", "")
        vacant_from = request.POST.get("vacant_from", "")
        vacant_untill = request.POST.get("vacant_untill", "")
        orderchoice = request.POST.get("orderchoice", "")

        params_dict = {}

        if spots_min != "":
            params_dict.update({"spots_min": spots_min})
        if spots_max != "":
            params_dict.update({"spots_max": spots_max})
        if price_min != "":
            params_dict.update({"price_min": price_min})
        if price_max != "":
            params_dict.update({"price_max": price_max})
        if vacant_from != "":
            params_dict.update({"vacant_from": vacant_from})
        if vacant_untill != "":
            params_dict.update({"vacant_untill": vacant_untill})
        if orderchoice != "":
            params_dict.update({"orderchoice": orderchoice})

        if not params_dict:
            data = form_rooms_list(cookie_check=cookie_check)
        else:
            data = form_rooms_list(filter=params_dict, cookie_check=cookie_check)
    else:
        data = form_rooms_list(cookie_check=cookie_check)

    return render(request, "rooms.html", data)


def room_reservation(request, name=None):
    loginform = LoginForm

    rooms = get_rooms_tuple()

    reservationform = ReservationForm(request.POST)
    reservationform.fields['room'].choices = rooms

    try:
        username_cookie = request.COOKIES["username"]
        password_cookie = request.COOKIES["password"]
    except KeyError:
        username_cookie = None
        password_cookie = None
    
    cookie_check = check_user(username=username_cookie, password=password_cookie)

    if not cookie_check:
        title = "Login required"
        data = {"title": title, "loginform": loginform, "status": "Reservations are only available to registered users", "status_color": "Red"}
        html = "login.html"
    else:
        title = "Reserve a room"
        html = "reservation.html"
        
        if request.method == "POST":
            room = request.POST.get("room", "")

            if room == "" and name != None:
                room = name

            date_from = request.POST.get("date_from", "")
            date_untill = request.POST.get("date_untill", "")

            if room != "" and date_from != "" and date_untill != "":
                if date_untill < date_from:
                    status = "Start date cannot be after end date"
                    data = {"title": title, "reservationform": reservationform, "status": status}
                else:
                    vacancy_dict = {'vacant_from': date_from, 'vacant_untill': date_untill}
                    vacancy_check = get_rooms_by_filter(filter=vacancy_dict, get_only_name=True)

                    occupied_check = True

                    for i in vacancy_check:
                        if room == i[0]:
                            occupied_check = False
                            break
                    
                    if occupied_check:
                        room_name = f"'{room}'"

                        sql_query = f'SELECT reservation_date FROM public."MainApp_reservation" WHERE room = {room_name}'
                        reservations_list = db_access(sql_query)
                        final_reservations_list = []

                        for reservation in reservations_list:
                            final_reservations_list.append(reservation[0])

                        status = f"Room {room} is occupied somewhere between {date_from} and {date_untill}"
                        occupancy_label = "The room is occupied on:"

                        data = {"title": title, "reservationform": reservationform, "status": status, "room_occupancy": final_reservations_list, "occupancy_label": occupancy_label}
                    else:
                        dates_list = get_dates_for_reservation(date_from, date_untill)

                        for reservation_date in dates_list:
                            create_reservation(room=room, reserved_for=username_cookie, reservation_date=reservation_date)

                        status = "Room successfully reserved!"
                        data = {"title": title, "reservationform": reservationform, "status": status}
            else:
                status = ""
                data = {"title": title, "reservationform": reservationform, "status": status, "name": name}

        else:
            status = ""
            data = {"title": title, "reservationform": reservationform, "status": status}
    
    response = render(request, html, context=data)

    return response


def profile_entrance(request):
    loginform = LoginForm

    try:
        username_cookie = request.COOKIES["username"]
        password_cookie = request.COOKIES["password"]
    except KeyError:
        username_cookie = None
        password_cookie = None

    cookie_check = check_user(username=username_cookie, password=password_cookie)

    if request.method == "POST":
        login = request.POST.get("login", "")
        password = request.POST.get("password", "")

        db_check = check_user(username=login, password=password)

        if db_check:
            title = "Your profile"
            data = {"title": title}
            html = "profile.html"
            response = render(request, html, context=data)
            response.set_cookie("username", login)
            response.set_cookie("password", password)
        else:
            title = "Login required"
            data = {"title": title, "loginform": loginform, "status": "Incorrect login/password", "status_color": "Red"}
            html = "login.html"
            response = render(request, html, context=data)
    else:
        if cookie_check:
            title = "Your profile"
            data = {"title": title}
            html = "profile.html"
            response = render(request, html, context=data)
        else:
            title = "Login required"
            data = {"title": title, "loginform": loginform, "status": title, "status_color": None}
            html = "login.html"
            response = render(request, html, context=data)

    return response


def profile_logout(request):
    loginform = LoginForm

    try:
        username_cookie = request.COOKIES["username"]
        password_cookie = request.COOKIES["password"]
    except KeyError:
        username_cookie = None
        password_cookie = None
    
    title = "Login required"
    data = {"title": title, "loginform": loginform, "status": title, "status_color": None}
    html = "login.html"
    response = render(request, html, context=data)
    
    
    if username_cookie is not None:
        response.delete_cookie("username")
    if password_cookie is not None:
        response.delete_cookie("password")
    
    return response


def user_register(request):
    registrationform = RegistrationForm
    loginform = LoginForm

    if request.method == "POST":
        username = request.POST.get("username", "")
        full_name = request.POST.get("full_name", "")
        password1 = request.POST.get("password1", "")
        password2 = request.POST.get("password2", "")

        if username == "":
            title = "Registration"
            data = {"title": title, "registrationform": registrationform, "status": "Create your profile"}
            html = "register.html"
        else:
            if password1 == password2:
                user_existence_check = check_user(username=username, check_only_username=True)

                if user_existence_check:
                    title = "Registration"
                    data = {"title": title, "registrationform": registrationform, "status": "Username already exists", "status_color": "Red"}
                    html = "register.html"
                else:
                    create_user(username=username, password=password1, full_name=full_name)

                    title = "Login required"
                    status = "You can now log into your account"
                    data = {"title": title, "loginform": loginform, "status": status, "status_color": None}
                    html = "login.html"
            else:
                title = "Registration"
                data = {"title": title, "registrationform": registrationform, "status": "Passwords do not match", "status_color": "Red"}
                html = "register.html"
        
    else:
        title = "Registration"
        data = {"title": title, "registrationform": registrationform, "status": "Create your profile", "status_color": None}
        html = "register.html"

    return render(request, html, context=data)


def user_profile(request, room=None, date=None):
    loginform = LoginForm

    try:
        username_cookie = request.COOKIES["username"]
        password_cookie = request.COOKIES["password"]
    except KeyError:
        username_cookie = None
        password_cookie = None

    cookie_check = check_user(username=username_cookie, password=password_cookie)

    if cookie_check:
        if request.method == "POST":
            if room is not None and date is not None:
                room_str = f"'{room}'"
                
                try:
                    date_str = datetime.datetime.strptime(date, "%b. %d, %Y")
                except ValueError:
                    date_str = datetime.datetime.strptime(date, "%B %d, %Y")
                    
                date_str = f"'{date_str}'"

                sql_query = f'DELETE FROM public."MainApp_reservation" WHERE room = {room_str} AND reservation_date = {date_str}'
                db_access(sql_query, result_needed=False)

        reserved_for_str = f"'{username_cookie}'"
        sql_query1 = f'SELECT room, reservation_date FROM public."MainApp_reservation" WHERE reserved_for = {reserved_for_str}'
        reservations_table = db_access(sql_query1)
        reservations = []

        for reservation in reservations_table:
            name_str = f"'{reservation[0]}'"
            sql_query2 = f'SELECT price, spots FROM public."MainApp_room" WHERE name = {name_str}'
            rooms_table = db_access(sql_query2)

            reservations.append({"number": reservation[0], "date": reservation[1], "price": rooms_table[0][0], "spots": rooms_table[0][1]})
        
        title = "Your profile"
        data = {"title": title, "reservations": reservations}
        html = "profile.html"
    else:
        title = "Login required"
        data = {"title": title, "loginform": loginform, "status": title}
        html = "login.html"

    return render(request, html, context=data)
